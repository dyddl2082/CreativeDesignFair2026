from machine import Pin, PWM, I2C
import machine
import math
import select
import sys
import time
import ujson


# ============================================================
# MacRobot Pico 2 H firmware
# ============================================================
# Roles:
# - USB serial command receiver from Raspberry Pi
# - MDD10A left/right track motor control
# - Quadrature encoder reading
# - Encoder-synchronized relative movement
# - Track-distance kinematics for straight / turn motion
# - Session-relative track encoder odometry
# - PCA9685 arm servo output
#
# Important conventions:
# - MOVE_CM positive: forward
# - DRIVE_REL yaw positive: left / counterclockwise
# - TURN_DEG positive: right / clockwise (legacy Pico protocol)
# - Public robot.TURN_BASE positive is left / counterclockwise;
#   the Raspberry Pi Gateway is expected to invert the sign.
# - Servo shaft angle positive is counterclockwise when viewed from
#   the protruding output-shaft side toward the servo body.
# ============================================================

FIRMWARE_NAME = "MacRobot_Pico_MotorArmController"
FIRMWARE_VERSION = "0.4.1-turn-torque"
CONFIG_SCHEMA_VERSION = 2


# ============================================================
# Pin map
# ============================================================

# I2C0 for PCA9685
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
I2C_FREQ_HZ = 100000

# Quadrature encoders
LEFT_ENC_A_PIN = 2
LEFT_ENC_B_PIN = 3
RIGHT_ENC_A_PIN = 4
RIGHT_ENC_B_PIN = 5

# MDD10A-style PWM + DIR motor inputs
LEFT_PWM_PIN = 10
LEFT_DIR_PIN = 11
RIGHT_PWM_PIN = 12
RIGHT_DIR_PIN = 13


# ============================================================
# Motor control constants
# ============================================================

PWM_FREQ_HZ = 20000
PWM_ABS_MAX = 255

# 2S LiPo + 6 V motor protection starting point.
PWM_LIMIT = 180

# Linear motion can start at a much lower PWM than a skid-steer turn.
MIN_MOTION_PWM = 45

# The tracked chassis needs enough breakaway torque on both tracks while
# turning.  Keep each active track at or above this PWM and use a limited
# synchronization correction so one side is never starved of torque.
MIN_TURN_PWM = 120

DEFAULT_MOVE_PWM = 120
DEFAULT_TURN_PWM = 150
DEFAULT_DRIVE_PWM = 100

# These three values replace a separate TICKS_PER_DEG constant.
# Calibrate LEFT/RIGHT_TICKS_PER_CM with straight forward/reverse tests.
# Measure EFFECTIVE_TRACK_WIDTH_CM between track centerlines, then refine
# only if turn tests or camera closed-loop alignment require it.
LEFT_TICKS_PER_CM = 72.422
RIGHT_TICKS_PER_CM = 71.82
EFFECTIVE_TRACK_WIDTH_CM = 19.0

# Motor and encoder direction correction.
MOTOR_LEFT_INVERT = False
MOTOR_RIGHT_INVERT = False
ENC_LEFT_INVERT = False
ENC_RIGHT_INVERT = False

# Progress synchronization gain for straight relative motion.
KP_SYNC = 0.60

# Turn-specific controller.  A tracked chassis can fail to rotate if the
# synchronization controller reduces either track below its breakaway PWM.
TURN_KP_SYNC = 0.25
TURN_MAX_CORRECTION_PWM = 20
TURN_DECEL_START_RATIO = 0.12
TURN_DECEL_MIN_SCALE = 0.80

CONTROL_DT_MS = 20
STALL_TIMEOUT_MS = 1800
STALL_MIN_PROGRESS_TICKS = 3
ENCODER_DIRECTION_CHECK_TICKS = 12

NEAR_TARGET_TOLERANCE_CM = 0.75
NEAR_TARGET_TOLERANCE_RATIO = 0.05
NEAR_TARGET_MAX_YAW_ERROR_DEG = 3.0

# ============================================================
# PCA9685 / arm servo configuration
# ============================================================

PCA9685_ADDR = 0x40
SERVO_FREQ_HZ = 50
ARM_SERVO_CHANNELS = (0, 1, 2)

SERVO_NAMES = {
    0: "left_mg996r_arm_tilt",
    1: "right_mg996r_rear_lift",
    2: "mg90s_gripper",
}

# Per-channel pulse clamp: (minimum_us, center_us, maximum_us)
SERVO_PULSE_US = {
    0: (500.0, 1500.0, 2500.0),
    1: (500.0, 1500.0, 2500.0),
    2: (500.0, 1500.0, 2500.0),
}

# Manual SERVO_DEG / ARM_DEG bench-test calibration:
# (deg_min, us_min, deg_center, us_center, deg_max, us_max)
SERVO_ANGLE_CAL = {
    0: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),
    1: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),
    2: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),
}

# None means the PCA9685 channel is FULL OFF.
last_servo_us = {
    0: None,
    1: None,
    2: None,
}


# ============================================================
# Config persistence
# ============================================================

CONFIG_PATH = "pico_config.json"


# ============================================================
# Runtime state
# ============================================================

stop_requested = False
estopped = False
motion_active = False
manual_motor_active = False

# Session-relative track encoder odometry.
# +x: initial forward, +y: initial left, +yaw: CCW / left.
odom_x_m = 0.0
odom_y_m = 0.0
odom_yaw_rad = 0.0
odom_reliable = True
odom_updated_ms = time.ticks_ms()


# ============================================================
# Generic helpers
# ============================================================

def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def normalize_angle_rad(angle_rad):
    while angle_rad >= math.pi:
        angle_rad -= 2.0 * math.pi
    while angle_rad < -math.pi:
        angle_rad += 2.0 * math.pi
    return angle_rad


def normalize_angle_deg(angle_deg):
    angle = float(angle_deg)
    while angle >= 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle


def positive_float(value, name):
    value = float(value)
    if value <= 0.0:
        raise ValueError("{} must be > 0".format(name))
    return value


def send(ok=True, event="response", **kwargs):
    # Every serial output is one JSON object. Do not print raw lists/text.
    payload = {
        "ok": bool(ok),
        "event": event,
        "time_ms": time.ticks_ms(),
    }
    payload.update(kwargs)

    try:
        sys.stdout.write(ujson.dumps(payload) + "\n")
    except Exception:
        sys.stdout.write('{"ok":false,"event":"json_error"}\n')


def current_calibration_dict():
    average_ticks_per_cm = 0.5 * (
        float(LEFT_TICKS_PER_CM) + float(RIGHT_TICKS_PER_CM)
    )
    derived_ticks_per_deg = (
        average_ticks_per_cm
        * math.pi
        * float(EFFECTIVE_TRACK_WIDTH_CM)
        / 360.0
    )
    return {
        "left_ticks_per_cm": LEFT_TICKS_PER_CM,
        "right_ticks_per_cm": RIGHT_TICKS_PER_CM,
        "effective_track_width_cm": EFFECTIVE_TRACK_WIDTH_CM,
        # Compatibility/readability values; no longer authoritative.
        "legacy_average_ticks_per_cm": average_ticks_per_cm,
        "derived_ticks_per_deg": derived_ticks_per_deg,
    }


def current_odometry_dict():
    return {
        "x_m": odom_x_m,
        "y_m": odom_y_m,
        "yaw_deg": odom_yaw_rad * 180.0 / math.pi,
        "reliable": odom_reliable,
        "source": "track_encoder_odometry",
        "updated_ms": odom_updated_ms,
    }


# ============================================================
# Quadrature encoder
# ============================================================

class QuadratureEncoder:
    # Transition table for old_state << 2 | new_state.
    _TABLE = (
        0, -1, 1, 0,
        1, 0, 0, -1,
        -1, 0, 0, 1,
        0, 1, -1, 0,
    )

    def __init__(self, pin_a, pin_b, invert=False):
        self.a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.invert = invert
        self.count = 0
        self.state = (self.a.value() << 1) | self.b.value()

        self.a.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=self._callback,
        )
        self.b.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=self._callback,
        )

    def _callback(self, pin):
        new_state = (self.a.value() << 1) | self.b.value()
        index = (self.state << 2) | new_state
        delta = self._TABLE[index]

        if self.invert:
            delta = -delta

        self.count += delta
        self.state = new_state

    def read(self):
        irq_state = machine.disable_irq()
        value = self.count
        machine.enable_irq(irq_state)
        return value

    def reset(self):
        irq_state = machine.disable_irq()
        self.count = 0
        self.state = (self.a.value() << 1) | self.b.value()
        machine.enable_irq(irq_state)


# ============================================================
# PCA9685
# ============================================================

class PCA9685:
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06

    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.write8(self.MODE1, 0x00)
        time.sleep_ms(10)
        self.set_pwm_freq(SERVO_FREQ_HZ)

        # Never command an unknown arm pose at boot.
        self.arm_off()

    def write8(self, reg, value):
        self.i2c.writeto_mem(
            self.address,
            reg,
            bytes([value & 0xFF]),
        )

    def read8(self, reg):
        return self.i2c.readfrom_mem(
            self.address,
            reg,
            1,
        )[0]

    def set_pwm_freq(self, freq_hz):
        prescale_value = (
            25000000.0 / (4096.0 * float(freq_hz)) - 1.0
        )
        prescale = int(prescale_value + 0.5)

        old_mode = self.read8(self.MODE1)
        sleep_mode = (old_mode & 0x7F) | 0x10

        self.write8(self.MODE1, sleep_mode)
        self.write8(self.PRESCALE, prescale)
        self.write8(self.MODE1, old_mode)
        time.sleep_ms(5)

        # Restart + auto increment + all call.
        self.write8(self.MODE1, old_mode | 0xA1)

    def set_pwm(self, channel, on_tick, off_tick):
        channel = int(channel)
        if not 0 <= channel <= 15:
            raise ValueError("PCA9685 channel must be 0..15")

        reg = self.LED0_ON_L + 4 * channel
        data = bytes([
            on_tick & 0xFF,
            (on_tick >> 8) & 0xFF,
            off_tick & 0xFF,
            (off_tick >> 8) & 0xFF,
        ])
        self.i2c.writeto_mem(self.address, reg, data)

    def _pulse_calibration(self, channel):
        channel = int(channel)
        if channel not in SERVO_PULSE_US:
            raise ValueError(
                "Servo channel is not configured: {}".format(channel)
            )
        return SERVO_PULSE_US[channel]

    def _clamp_servo_us(self, channel, pulse_us):
        values = self._pulse_calibration(channel)
        minimum = float(values[0])
        maximum = float(values[-1])
        return clamp(float(pulse_us), minimum, maximum)

    def _write_servo_us_unchecked(self, channel, pulse_us):
        # 50 Hz period = 20,000 us.
        ticks = int(round(float(pulse_us) * 4096.0 / 20000.0))
        ticks = int(clamp(ticks, 0, 4095))
        self.set_pwm(int(channel), 0, ticks)

    def set_servo_us(self, channel, pulse_us):
        channel = int(channel)
        applied_us = self._clamp_servo_us(channel, pulse_us)
        self._write_servo_us_unchecked(channel, applied_us)
        last_servo_us[channel] = applied_us
        return applied_us

    def _servo_deg_to_us(self, channel, angle_deg):
        channel = int(channel)
        if channel not in SERVO_ANGLE_CAL:
            raise ValueError(
                "Servo angle calibration missing: {}".format(channel)
            )

        values = SERVO_ANGLE_CAL[channel]
        deg_min = float(values[0])
        us_min = float(values[1])
        deg_center = float(values[2])
        us_center = float(values[3])
        deg_max = float(values[4])
        us_max = float(values[5])

        angle_deg = clamp(float(angle_deg), deg_min, deg_max)

        if angle_deg <= deg_center:
            denominator = deg_center - deg_min
            ratio = 0.0 if denominator == 0.0 else (
                (angle_deg - deg_min) / denominator
            )
            return us_min + ratio * (us_center - us_min)

        denominator = deg_max - deg_center
        ratio = 0.0 if denominator == 0.0 else (
            (angle_deg - deg_center) / denominator
        )
        return us_center + ratio * (us_max - us_center)

    def set_servo_deg(self, channel, angle_deg):
        requested_us = self._servo_deg_to_us(channel, angle_deg)
        applied_us = self.set_servo_us(channel, requested_us)
        return requested_us, applied_us

    def set_arm_us(self, left_us, right_us, gripper_us):
        requested = {
            0: float(left_us),
            1: float(right_us),
            2: float(gripper_us),
        }

        # Clamp all channels before changing any output.
        applied = {
            channel: self._clamp_servo_us(
                channel,
                requested[channel],
            )
            for channel in ARM_SERVO_CHANNELS
        }

        for channel in ARM_SERVO_CHANNELS:
            self._write_servo_us_unchecked(
                channel,
                applied[channel],
            )
            last_servo_us[channel] = applied[channel]

        return [applied[0], applied[1], applied[2]]

    def set_arm_deg(self, left_deg, right_deg, gripper_deg):
        requested_deg = [
            float(left_deg),
            float(right_deg),
            float(gripper_deg),
        ]
        requested_us = [
            self._servo_deg_to_us(0, requested_deg[0]),
            self._servo_deg_to_us(1, requested_deg[1]),
            self._servo_deg_to_us(2, requested_deg[2]),
        ]
        applied_us = self.set_arm_us(
            requested_us[0],
            requested_us[1],
            requested_us[2],
        )
        return requested_deg, requested_us, applied_us

    def servo_off(self, channel):
        channel = int(channel)
        if channel not in ARM_SERVO_CHANNELS:
            raise ValueError(
                "Arm servo channel is not configured: {}".format(channel)
            )

        # OFF_H bit 4 = FULL OFF; off_tick=4096 packs 0x1000.
        self.set_pwm(channel, 0, 4096)
        last_servo_us[channel] = None

    def arm_off(self):
        for channel in ARM_SERVO_CHANNELS:
            self.servo_off(channel)


# ============================================================
# Hardware initialization
# ============================================================

left_pwm = PWM(Pin(LEFT_PWM_PIN))
right_pwm = PWM(Pin(RIGHT_PWM_PIN))
left_pwm.freq(PWM_FREQ_HZ)
right_pwm.freq(PWM_FREQ_HZ)

left_dir = Pin(LEFT_DIR_PIN, Pin.OUT)
right_dir = Pin(RIGHT_DIR_PIN, Pin.OUT)

left_encoder = QuadratureEncoder(
    LEFT_ENC_A_PIN,
    LEFT_ENC_B_PIN,
    invert=ENC_LEFT_INVERT,
)
right_encoder = QuadratureEncoder(
    RIGHT_ENC_A_PIN,
    RIGHT_ENC_B_PIN,
    invert=ENC_RIGHT_INVERT,
)

i2c = I2C(
    0,
    scl=Pin(I2C_SCL_PIN),
    sda=Pin(I2C_SDA_PIN),
    freq=I2C_FREQ_HZ,
)

pca = None

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)


# ============================================================
# Configuration load/save
# ============================================================

def save_config():
    cfg = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "PWM_LIMIT": PWM_LIMIT,
        "MIN_MOTION_PWM": MIN_MOTION_PWM,
        "MIN_TURN_PWM": MIN_TURN_PWM,
        "DEFAULT_TURN_PWM": DEFAULT_TURN_PWM,
        "TURN_KP_SYNC": TURN_KP_SYNC,
        "TURN_MAX_CORRECTION_PWM": TURN_MAX_CORRECTION_PWM,
        "LEFT_TICKS_PER_CM": LEFT_TICKS_PER_CM,
        "RIGHT_TICKS_PER_CM": RIGHT_TICKS_PER_CM,
        "EFFECTIVE_TRACK_WIDTH_CM": EFFECTIVE_TRACK_WIDTH_CM,
        "MOTOR_LEFT_INVERT": MOTOR_LEFT_INVERT,
        "MOTOR_RIGHT_INVERT": MOTOR_RIGHT_INVERT,
        "ENC_LEFT_INVERT": ENC_LEFT_INVERT,
        "ENC_RIGHT_INVERT": ENC_RIGHT_INVERT,
        "KP_SYNC": KP_SYNC,
    }

    with open(CONFIG_PATH, "w") as file_handle:
        file_handle.write(ujson.dumps(cfg))

    return cfg


def load_config():
    global PWM_LIMIT
    global MIN_MOTION_PWM
    global MIN_TURN_PWM
    global DEFAULT_TURN_PWM
    global TURN_KP_SYNC
    global TURN_MAX_CORRECTION_PWM
    global LEFT_TICKS_PER_CM
    global RIGHT_TICKS_PER_CM
    global EFFECTIVE_TRACK_WIDTH_CM
    global MOTOR_LEFT_INVERT
    global MOTOR_RIGHT_INVERT
    global ENC_LEFT_INVERT
    global ENC_RIGHT_INVERT
    global KP_SYNC

    try:
        with open(CONFIG_PATH, "r") as file_handle:
            cfg = ujson.loads(file_handle.read())

        PWM_LIMIT = int(cfg.get("PWM_LIMIT", PWM_LIMIT))
        MIN_MOTION_PWM = int(
            cfg.get("MIN_MOTION_PWM", MIN_MOTION_PWM)
        )
        MIN_TURN_PWM = int(
            cfg.get("MIN_TURN_PWM", MIN_TURN_PWM)
        )
        DEFAULT_TURN_PWM = int(
            cfg.get("DEFAULT_TURN_PWM", DEFAULT_TURN_PWM)
        )
        TURN_KP_SYNC = float(
            cfg.get("TURN_KP_SYNC", TURN_KP_SYNC)
        )
        TURN_MAX_CORRECTION_PWM = int(
            cfg.get(
                "TURN_MAX_CORRECTION_PWM",
                TURN_MAX_CORRECTION_PWM,
            )
        )

        # New schema.
        if "LEFT_TICKS_PER_CM" in cfg:
            LEFT_TICKS_PER_CM = positive_float(
                cfg.get("LEFT_TICKS_PER_CM"),
                "LEFT_TICKS_PER_CM",
            )
        if "RIGHT_TICKS_PER_CM" in cfg:
            RIGHT_TICKS_PER_CM = positive_float(
                cfg.get("RIGHT_TICKS_PER_CM"),
                "RIGHT_TICKS_PER_CM",
            )
        if "EFFECTIVE_TRACK_WIDTH_CM" in cfg:
            EFFECTIVE_TRACK_WIDTH_CM = positive_float(
                cfg.get("EFFECTIVE_TRACK_WIDTH_CM"),
                "EFFECTIVE_TRACK_WIDTH_CM",
            )

        # Legacy migration: old TICKS_PER_CM/TICKS_PER_DEG.
        if (
            "LEFT_TICKS_PER_CM" not in cfg
            and "TICKS_PER_CM" in cfg
        ):
            common_ticks_per_cm = positive_float(
                cfg.get("TICKS_PER_CM"),
                "TICKS_PER_CM",
            )
            LEFT_TICKS_PER_CM = common_ticks_per_cm
            RIGHT_TICKS_PER_CM = common_ticks_per_cm

        if (
            "EFFECTIVE_TRACK_WIDTH_CM" not in cfg
            and "TICKS_PER_DEG" in cfg
        ):
            legacy_ticks_per_deg = positive_float(
                cfg.get("TICKS_PER_DEG"),
                "TICKS_PER_DEG",
            )
            average_ticks_per_cm = 0.5 * (
                LEFT_TICKS_PER_CM + RIGHT_TICKS_PER_CM
            )
            EFFECTIVE_TRACK_WIDTH_CM = (
                legacy_ticks_per_deg
                * 360.0
                / (math.pi * average_ticks_per_cm)
            )

        MOTOR_LEFT_INVERT = bool(
            cfg.get("MOTOR_LEFT_INVERT", MOTOR_LEFT_INVERT)
        )
        MOTOR_RIGHT_INVERT = bool(
            cfg.get("MOTOR_RIGHT_INVERT", MOTOR_RIGHT_INVERT)
        )
        ENC_LEFT_INVERT = bool(
            cfg.get("ENC_LEFT_INVERT", ENC_LEFT_INVERT)
        )
        ENC_RIGHT_INVERT = bool(
            cfg.get("ENC_RIGHT_INVERT", ENC_RIGHT_INVERT)
        )
        KP_SYNC = float(cfg.get("KP_SYNC", KP_SYNC))

        return cfg

    except Exception:
        return None


# ============================================================
# Motor and encoder helpers
# ============================================================

def pwm_to_duty_u16(pwm_value):
    pwm_value = clamp(abs(int(pwm_value)), 0, PWM_ABS_MAX)
    return int(pwm_value * 65535 / PWM_ABS_MAX)


def set_motors(left_value, right_value):
    if estopped:
        left_pwm.duty_u16(0)
        right_pwm.duty_u16(0)
        return

    left_value = int(clamp(left_value, -PWM_LIMIT, PWM_LIMIT))
    right_value = int(clamp(right_value, -PWM_LIMIT, PWM_LIMIT))

    if MOTOR_LEFT_INVERT:
        left_value = -left_value
    if MOTOR_RIGHT_INVERT:
        right_value = -right_value

    if left_value >= 0:
        left_dir.value(1)
    else:
        left_dir.value(0)
    left_pwm.duty_u16(pwm_to_duty_u16(left_value))

    if right_value >= 0:
        right_dir.value(1)
    else:
        right_dir.value(0)
    right_pwm.duty_u16(pwm_to_duty_u16(right_value))


def stop_motors():
    left_pwm.duty_u16(0)
    right_pwm.duty_u16(0)


def reset_encoders():
    left_encoder.reset()
    right_encoder.reset()


def get_encoders():
    return left_encoder.read(), right_encoder.read()


def motion_pwm_from_magnitude(magnitude, minimum_pwm):
    magnitude = float(magnitude)
    if magnitude <= 1.0:
        return 0

    minimum_pwm = int(clamp(minimum_pwm, 0, PWM_LIMIT))
    return int(clamp(magnitude, minimum_pwm, PWM_LIMIT))


def current_turn_control_dict():
    return {
        "default_turn_pwm": DEFAULT_TURN_PWM,
        "min_turn_pwm": MIN_TURN_PWM,
        "turn_kp_sync": TURN_KP_SYNC,
        "turn_max_correction_pwm": TURN_MAX_CORRECTION_PWM,
        "turn_decel_start_ratio": TURN_DECEL_START_RATIO,
        "turn_decel_min_scale": TURN_DECEL_MIN_SCALE,
    }


# ============================================================
# Track kinematics and odometry
# ============================================================

def calculate_track_targets(distance_cm, yaw_ccw_deg):
    distance_cm = float(distance_cm)
    yaw_ccw_deg = float(yaw_ccw_deg)

    theta_rad = yaw_ccw_deg * math.pi / 180.0
    half_turn_arc_cm = (
        0.5 * EFFECTIVE_TRACK_WIDTH_CM * theta_rad
    )

    left_distance_cm = distance_cm - half_turn_arc_cm
    right_distance_cm = distance_cm + half_turn_arc_cm

    left_target_ticks = left_distance_cm * LEFT_TICKS_PER_CM
    right_target_ticks = right_distance_cm * RIGHT_TICKS_PER_CM

    return {
        "distance_cm": distance_cm,
        "yaw_ccw_deg": yaw_ccw_deg,
        "left_distance_cm": left_distance_cm,
        "right_distance_cm": right_distance_cm,
        "left_target_ticks": left_target_ticks,
        "right_target_ticks": right_target_ticks,
    }


def update_odometry_from_counts(
    left_count,
    right_count,
    reliable=True,
):
    global odom_x_m
    global odom_y_m
    global odom_yaw_rad
    global odom_reliable
    global odom_updated_ms

    left_distance_m = (
        float(left_count) / LEFT_TICKS_PER_CM / 100.0
    )
    right_distance_m = (
        float(right_count) / RIGHT_TICKS_PER_CM / 100.0
    )

    center_distance_m = 0.5 * (
        left_distance_m + right_distance_m
    )
    track_width_m = EFFECTIVE_TRACK_WIDTH_CM / 100.0
    yaw_delta_rad = (
        right_distance_m - left_distance_m
    ) / track_width_m

    middle_yaw_rad = odom_yaw_rad + 0.5 * yaw_delta_rad
    odom_x_m += center_distance_m * math.cos(middle_yaw_rad)
    odom_y_m += center_distance_m * math.sin(middle_yaw_rad)
    odom_yaw_rad = normalize_angle_rad(
        odom_yaw_rad + yaw_delta_rad
    )

    if not reliable:
        odom_reliable = False
    odom_updated_ms = time.ticks_ms()


def reset_odometry(x_m=0.0, y_m=0.0, yaw_deg=0.0):
    global odom_x_m
    global odom_y_m
    global odom_yaw_rad
    global odom_reliable
    global odom_updated_ms

    odom_x_m = float(x_m)
    odom_y_m = float(y_m)
    odom_yaw_rad = normalize_angle_rad(
        float(yaw_deg) * math.pi / 180.0
    )
    odom_reliable = True
    odom_updated_ms = time.ticks_ms()


def finish_manual_motor_session(mark_reliable=False):
    global manual_motor_active

    if not manual_motor_active:
        return None

    stop_motors()
    left_count, right_count = get_encoders()
    update_odometry_from_counts(
        left_count,
        right_count,
        reliable=bool(mark_reliable),
    )
    manual_motor_active = False

    return {
        "left_count": left_count,
        "right_count": right_count,
    }


# ============================================================
# Motion execution
# ============================================================

def check_immediate_serial():
    # During blocking closed-loop motion, STOP and ESTOP remain responsive.
    global stop_requested
    global estopped

    try:
        events = poller.poll(0)
    except Exception:
        return False

    if not events:
        return False

    line = sys.stdin.readline().strip()
    if not line:
        return False

    cmd = line.split()[0].upper()

    if cmd == "STOP":
        stop_requested = True
        stop_motors()
        send(ok=True, event="stop_requested")
        return True

    if cmd == "ESTOP":
        stop_requested = True
        estopped = True
        stop_motors()
        send(ok=True, event="estop_latched")
        return True

    send(ok=False, event="busy", ignored=line)
    return False

def _target_distance_cm_for_side(target_ticks, ticks_per_cm):
    ticks_per_cm = max(float(ticks_per_cm), 1.0)
    return abs(float(target_ticks)) / ticks_per_cm


def _track_error_cm(count_ticks, target_ticks, ticks_per_cm):
    ticks_per_cm = max(float(ticks_per_cm), 1.0)
    return (
        abs(abs(float(target_ticks)) - abs(float(count_ticks)))
        / ticks_per_cm
    )


def _yaw_delta_deg_from_counts(left_ticks, right_ticks):
    left_distance_cm = (
        float(left_ticks) / max(float(LEFT_TICKS_PER_CM), 1.0)
    )
    right_distance_cm = (
        float(right_ticks) / max(float(RIGHT_TICKS_PER_CM), 1.0)
    )
    track_width_cm = max(float(EFFECTIVE_TRACK_WIDTH_CM), 1.0)
    yaw_rad = (
        right_distance_cm - left_distance_cm
    ) / track_width_cm
    return yaw_rad * 180.0 / math.pi


def _is_near_target_completion(
    left_count,
    right_count,
    left_target,
    right_target,
):
    left_target_cm = _target_distance_cm_for_side(
        left_target,
        LEFT_TICKS_PER_CM,
    )
    right_target_cm = _target_distance_cm_for_side(
        right_target,
        RIGHT_TICKS_PER_CM,
    )

    left_allowed_cm = max(
        float(NEAR_TARGET_TOLERANCE_CM),
        left_target_cm * float(NEAR_TARGET_TOLERANCE_RATIO),
    )
    right_allowed_cm = max(
        float(NEAR_TARGET_TOLERANCE_CM),
        right_target_cm * float(NEAR_TARGET_TOLERANCE_RATIO),
    )

    left_error_cm = _track_error_cm(
        left_count,
        left_target,
        LEFT_TICKS_PER_CM,
    )
    right_error_cm = _track_error_cm(
        right_count,
        right_target,
        RIGHT_TICKS_PER_CM,
    )

    target_yaw_deg = _yaw_delta_deg_from_counts(
        left_target,
        right_target,
    )
    actual_yaw_deg = _yaw_delta_deg_from_counts(
        left_count,
        right_count,
    )
    yaw_error_deg = abs(
        normalize_angle_deg(actual_yaw_deg - target_yaw_deg)
    )

    ok = (
        left_error_cm <= left_allowed_cm
        and right_error_cm <= right_allowed_cm
        and yaw_error_deg <= float(NEAR_TARGET_MAX_YAW_ERROR_DEG)
    )

    return {
        "ok": bool(ok),
        "left_error_cm": left_error_cm,
        "right_error_cm": right_error_cm,
        "left_allowed_cm": left_allowed_cm,
        "right_allowed_cm": right_allowed_cm,
        "target_yaw_deg": target_yaw_deg,
        "actual_yaw_deg": actual_yaw_deg,
        "yaw_error_deg": yaw_error_deg,
    }


def _finalize_closed_loop_motion(
    status,
    left_count,
    right_count,
    left_target,
    right_target,
    start_ms,
):
    global motion_active
    global odom_reliable

    stop_motors()
    motion_active = False

    raw_status = str(status)
    completion_reason = raw_status
    near_target = None

    # Convert only end-of-motion stall into a valid completion
    # when the encoder counts prove that the robot is already
    # sufficiently close to the requested target.
    if raw_status == "stall":
        near_target = _is_near_target_completion(
            left_count,
            right_count,
            left_target,
            right_target,
        )
        if near_target.get("ok", False):
            status = "done"
            completion_reason = "near_target_stall"

    # Encoder direction errors mean encoder polarity is not trustworthy.
    if status != "encoder_direction_error":
        update_odometry_from_counts(
            left_count,
            right_count,
            reliable=(status == "done"),
        )
    else:
        odom_reliable = False

    result = {
        "status": status,
        "raw_status": raw_status,
        "completion_reason": completion_reason,
        "left_count": left_count,
        "right_count": right_count,
        "left_target": left_target,
        "right_target": right_target,
        "elapsed_ms": time.ticks_diff(time.ticks_ms(), start_ms),
        "odom": current_odometry_dict(),
    }

    if near_target is not None:
        result["near_target"] = near_target

    return result


def move_ticks(
    left_target,
    right_target,
    speed=DEFAULT_MOVE_PWM,
    timeout_sec=10.0,
    motion_profile=None,
):
    # Relative encoder motion with profile-specific progress synchronization.
    global stop_requested
    global motion_active

    if estopped:
        left_count, right_count = get_encoders()
        return {
            "status": "estopped",
            "left_count": left_count,
            "right_count": right_count,
            "left_target": float(left_target),
            "right_target": float(right_target),
            "elapsed_ms": 0,
            "odom": current_odometry_dict(),
        }

    # End any direct MOTOR session before a closed-loop command.
    finish_manual_motor_session(mark_reliable=False)

    stop_requested = False
    motion_active = True
    reset_encoders()

    left_target = float(left_target)
    right_target = float(right_target)
    left_abs_target = abs(left_target)
    right_abs_target = abs(right_target)
    left_sign = sign(left_target)
    right_sign = sign(right_target)

    requested_speed = int(float(speed))
    if requested_speed <= 0:
        raise ValueError("speed must be > 0")

    if motion_profile is None:
        if left_sign != right_sign:
            motion_profile = "turn"
        else:
            motion_profile = "linear"

    motion_profile = str(motion_profile).lower()
    if motion_profile == "turn":
        minimum_pwm = int(clamp(MIN_TURN_PWM, 1, PWM_LIMIT))
        speed = int(clamp(
            max(requested_speed, minimum_pwm),
            1,
            PWM_LIMIT,
        ))
        sync_kp = max(0.0, float(TURN_KP_SYNC))
        max_correction_pwm = int(clamp(
            TURN_MAX_CORRECTION_PWM,
            0,
            PWM_LIMIT,
        ))
        decel_start_ratio = clamp(
            float(TURN_DECEL_START_RATIO),
            0.001,
            1.0,
        )
        decel_min_scale = clamp(
            float(TURN_DECEL_MIN_SCALE),
            0.0,
            1.0,
        )
    else:
        motion_profile = "linear"
        minimum_pwm = int(clamp(MIN_MOTION_PWM, 1, PWM_LIMIT))
        speed = int(clamp(requested_speed, 1, PWM_LIMIT))
        sync_kp = max(0.0, float(KP_SYNC))
        max_correction_pwm = PWM_LIMIT
        decel_start_ratio = 0.25
        decel_min_scale = 0.35

    start_ms = time.ticks_ms()

    if left_abs_target < 1.0 and right_abs_target < 1.0:
        return _finalize_closed_loop_motion(
            "done",
            0,
            0,
            left_target,
            right_target,
            start_ms,
        )

    last_progress_ms = start_ms
    last_total_progress = 0

    while True:
        now_ms = time.ticks_ms()

        if check_immediate_serial() or stop_requested:
            left_count, right_count = get_encoders()
            return _finalize_closed_loop_motion(
                "stopped",
                left_count,
                right_count,
                left_target,
                right_target,
                start_ms,
            )

        if timeout_sec > 0.0:
            if time.ticks_diff(now_ms, start_ms) > int(
                float(timeout_sec) * 1000.0
            ):
                left_count, right_count = get_encoders()
                return _finalize_closed_loop_motion(
                    "timeout",
                    left_count,
                    right_count,
                    left_target,
                    right_target,
                    start_ms,
                )

        left_count, right_count = get_encoders()

        if (
            left_abs_target >= 1.0
            and abs(left_count) >= ENCODER_DIRECTION_CHECK_TICKS
            and sign(left_count) != left_sign
        ):
            return _finalize_closed_loop_motion(
                "encoder_direction_error",
                left_count,
                right_count,
                left_target,
                right_target,
                start_ms,
            )

        if (
            right_abs_target >= 1.0
            and abs(right_count) >= ENCODER_DIRECTION_CHECK_TICKS
            and sign(right_count) != right_sign
        ):
            return _finalize_closed_loop_motion(
                "encoder_direction_error",
                left_count,
                right_count,
                left_target,
                right_target,
                start_ms,
            )

        left_done = (
            True
            if left_abs_target < 1.0
            else abs(left_count) >= left_abs_target
        )
        right_done = (
            True
            if right_abs_target < 1.0
            else abs(right_count) >= right_abs_target
        )

        if left_done and right_done:
            return _finalize_closed_loop_motion(
                "done",
                left_count,
                right_count,
                left_target,
                right_target,
                start_ms,
            )

        left_progress = (
            1.0
            if left_abs_target < 1.0
            else clamp(
                abs(left_count) / left_abs_target,
                0.0,
                1.0,
            )
        )
        right_progress = (
            1.0
            if right_abs_target < 1.0
            else clamp(
                abs(right_count) / right_abs_target,
                0.0,
                1.0,
            )
        )

        avg_progress = 0.5 * (left_progress + right_progress)
        remaining = clamp(1.0 - avg_progress, 0.0, 1.0)

        # Profile-specific deceleration.  The turn profile never lets an
        # active track fall below MIN_TURN_PWM, because the tracked chassis
        # needs substantial breakaway torque to keep rotating.
        if remaining < decel_start_ratio:
            speed_scale = clamp(
                remaining / decel_start_ratio,
                decel_min_scale,
                1.0,
            )
        else:
            speed_scale = 1.0

        base = max(float(minimum_pwm), speed * speed_scale)
        base = min(base, float(PWM_LIMIT))

        progress_error = left_progress - right_progress
        requested_correction = sync_kp * progress_error * speed

        # Keep both active tracks above their torque floor and below the
        # configured PWM limit.  This prevents the synchronization term from
        # starving one track during a turn.
        correction_headroom = min(
            float(max_correction_pwm),
            max(0.0, base - float(minimum_pwm)),
            max(0.0, float(PWM_LIMIT) - base),
        )
        correction = clamp(
            requested_correction,
            -correction_headroom,
            correction_headroom,
        )

        left_magnitude = base - correction
        right_magnitude = base + correction

        left_command = (
            0
            if left_done
            else left_sign * motion_pwm_from_magnitude(
                left_magnitude,
                minimum_pwm,
            )
        )
        right_command = (
            0
            if right_done
            else right_sign * motion_pwm_from_magnitude(
                right_magnitude,
                minimum_pwm,
            )
        )

        set_motors(left_command, right_command)

        total_progress = abs(left_count) + abs(right_count)
        if total_progress > (
            last_total_progress + STALL_MIN_PROGRESS_TICKS
        ):
            last_total_progress = total_progress
            last_progress_ms = now_ms
        elif time.ticks_diff(
            now_ms,
            last_progress_ms,
        ) > STALL_TIMEOUT_MS:
            return _finalize_closed_loop_motion(
                "stall",
                left_count,
                right_count,
                left_target,
                right_target,
                start_ms,
            )

        time.sleep_ms(CONTROL_DT_MS)


def drive_relative(
    distance_cm,
    yaw_ccw_deg,
    speed=DEFAULT_DRIVE_PWM,
    timeout_sec=10.0,
):
    targets = calculate_track_targets(
        distance_cm,
        yaw_ccw_deg,
    )
    left_sign = sign(targets["left_target_ticks"])
    right_sign = sign(targets["right_target_ticks"])
    motion_profile = (
        "turn"
        if left_sign != right_sign
        else "linear"
    )

    result = move_ticks(
        targets["left_target_ticks"],
        targets["right_target_ticks"],
        speed=speed,
        timeout_sec=timeout_sec,
        motion_profile=motion_profile,
    )
    result["requested_distance_cm"] = targets["distance_cm"]
    result["requested_yaw_ccw_deg"] = targets["yaw_ccw_deg"]
    result["left_distance_cm"] = targets["left_distance_cm"]
    result["right_distance_cm"] = targets["right_distance_cm"]
    return result


def move_cm(
    distance_cm,
    speed=DEFAULT_MOVE_PWM,
    timeout_sec=10.0,
):
    return drive_relative(
        distance_cm=float(distance_cm),
        yaw_ccw_deg=0.0,
        speed=speed,
        timeout_sec=timeout_sec,
    )


def turn_deg(
    angle_deg,
    speed=DEFAULT_TURN_PWM,
    timeout_sec=8.0,
):
    # Legacy Pico protocol: positive angle = right / clockwise.
    # Internal kinematics: positive yaw = left / counterclockwise.
    return drive_relative(
        distance_cm=0.0,
        yaw_ccw_deg=-float(angle_deg),
        speed=speed,
        timeout_sec=timeout_sec,
    )


# ============================================================
# Command handling
# ============================================================

def handle_command(line):
    global stop_requested
    global estopped
    global PWM_LIMIT
    global MIN_MOTION_PWM
    global MIN_TURN_PWM
    global DEFAULT_TURN_PWM
    global TURN_KP_SYNC
    global TURN_MAX_CORRECTION_PWM
    global LEFT_TICKS_PER_CM
    global RIGHT_TICKS_PER_CM
    global EFFECTIVE_TRACK_WIDTH_CM
    global MOTOR_LEFT_INVERT
    global MOTOR_RIGHT_INVERT
    global ENC_LEFT_INVERT
    global ENC_RIGHT_INVERT
    global KP_SYNC
    global manual_motor_active
    global odom_reliable
    global pca

    line = line.strip()
    if not line:
        return

    parts = line.split()
    cmd = parts[0].upper()

    try:
        if cmd == "PING":
            send(
                ok=True,
                event="pong",
                firmware=FIRMWARE_NAME,
                version=FIRMWARE_VERSION,
            )

        elif cmd == "HELP":
            send(
                ok=True,
                event="help",
                commands=[
                    "PING",
                    "STATUS?",
                    "ENC?",
                    "RESET_ENC",
                    "ODOM?",
                    "RESET_ODOM [x_m y_m yaw_deg]",
                    "STOP",
                    "ESTOP",
                    "CLEAR_ESTOP",
                    "MOTOR <left_pwm> <right_pwm>",
                    "MOVE_CM <cm> [speed] [timeout_sec]",
                    "TURN_DEG <deg_right_positive> [speed] [timeout_sec]",
                    "DRIVE_REL <cm> <yaw_ccw_deg> [speed] [timeout_sec]",
                    "MOVE_TICKS <left_ticks> <right_ticks> [speed] [timeout_sec]",
                    "GET_CAL",
                    "SET_TRACK_CAL <left_ticks_per_cm> <right_ticks_per_cm> <track_width_cm>",
                    "SET_LINEAR_CAL <left_ticks_per_cm> <right_ticks_per_cm>",
                    "SET_TRACK_WIDTH <track_width_cm>",
                    "SET_CAL <legacy_common_ticks_per_cm> <legacy_ticks_per_deg>",
                    "SERVO <channel> <angle_deg>",
                    "SERVO_DEG <channel> <angle_deg>",
                    "SERVO_US <channel> <pulse_us>",
                    "ARM_DEG <left_deg> <right_deg> <gripper_deg>",
                    "ARM_US <left_us> <right_us> <gripper_us>",
                    "SERVO_OFF <channel>",
                    "ARM_OFF",
                    "SERVO_STATE?",
                    "SERVO_CAL?",
                    "SET_PWM_LIMIT <0-255>",
                    "SET_MIN_PWM <0-255>",
                    "GET_TURN_CONTROL",
                    "SET_TURN_CONTROL <default_pwm> <min_pwm> <kp_sync> <max_correction_pwm>",
                    "SET_KP_SYNC <value>",
                    "SET_MOTOR_INVERT <left 0/1> <right 0/1>",
                    "SET_ENCODER_INVERT <left 0/1> <right 0/1>",
                    "SAVE_CONFIG",
                    "LOAD_CONFIG",
                ],
            )

        elif cmd == "STATUS?":
            left_count, right_count = get_encoders()
            send(
                ok=True,
                event="status",
                firmware=FIRMWARE_NAME,
                version=FIRMWARE_VERSION,
                estopped=estopped,
                motion_active=motion_active,
                manual_motor_active=manual_motor_active,
                left_encoder=left_count,
                right_encoder=right_count,
                pwm_limit=PWM_LIMIT,
                min_motion_pwm=MIN_MOTION_PWM,
                kp_sync=KP_SYNC,
                turn_control=current_turn_control_dict(),
                calibration=current_calibration_dict(),
                odometry=current_odometry_dict(),
                pca9685_available=(pca is not None),
                servo_pulse_us={
                    "0": last_servo_us[0],
                    "1": last_servo_us[1],
                    "2": last_servo_us[2],
                },
            )

        elif cmd == "ENC?":
            left_count, right_count = get_encoders()
            send(
                ok=True,
                event="encoders",
                left=left_count,
                right=right_count,
            )

        elif cmd == "RESET_ENC":
            reset_encoders()
            send(ok=True, event="encoders_reset")

        elif cmd == "ODOM?":
            send(
                ok=True,
                event="odometry",
                odometry=current_odometry_dict(),
            )

        elif cmd == "RESET_ODOM":
            if len(parts) == 1:
                reset_odometry()
            elif len(parts) == 4:
                reset_odometry(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3]),
                )
            else:
                raise ValueError(
                    "Usage: RESET_ODOM [x_m y_m yaw_deg]"
                )
            send(
                ok=True,
                event="odometry_reset",
                odometry=current_odometry_dict(),
            )

        elif cmd == "STOP":
            stop_requested = True
            manual_result = finish_manual_motor_session(
                mark_reliable=False
            )
            stop_motors()
            send(
                ok=True,
                event="stopped",
                manual_motion=manual_result,
                odometry=current_odometry_dict(),
            )

        elif cmd == "ESTOP":
            stop_requested = True
            estopped = True
            manual_result = finish_manual_motor_session(
                mark_reliable=False
            )
            stop_motors()
            send(
                ok=True,
                event="estop_latched",
                manual_motion=manual_result,
                odometry=current_odometry_dict(),
            )

        elif cmd == "CLEAR_ESTOP":
            estopped = False
            stop_requested = False
            stop_motors()
            send(ok=True, event="estop_cleared")

        elif cmd == "MOTOR":
            if estopped:
                raise ValueError("ESTOP is active")
            if len(parts) != 3:
                raise ValueError(
                    "Usage: MOTOR <left_pwm> <right_pwm>"
                )

            left_value = int(float(parts[1]))
            right_value = int(float(parts[2]))

            if left_value == 0 and right_value == 0:
                manual_result = finish_manual_motor_session(
                    mark_reliable=False
                )
                stop_motors()
                send(
                    ok=True,
                    event="motor_stopped",
                    manual_motion=manual_result,
                    odometry=current_odometry_dict(),
                )
            else:
                if not manual_motor_active:
                    reset_encoders()
                    manual_motor_active = True
                    odom_reliable = False
                set_motors(left_value, right_value)
                send(
                    ok=True,
                    event="motor_set",
                    left=left_value,
                    right=right_value,
                    odometry_reliable=False,
                )

        elif cmd == "MOVE_CM":
            if len(parts) < 2:
                raise ValueError(
                    "Usage: MOVE_CM <cm> [speed] [timeout_sec]"
                )
            distance_cm = float(parts[1])
            speed = (
                int(float(parts[2]))
                if len(parts) >= 3
                else DEFAULT_MOVE_PWM
            )
            timeout_sec = (
                float(parts[3])
                if len(parts) >= 4
                else max(5.0, abs(distance_cm) * 0.5)
            )
            result = move_cm(
                distance_cm,
                speed=speed,
                timeout_sec=timeout_sec,
            )
            send(
                ok=(result["status"] == "done"),
                event="move_cm_result",
                **result
            )

        elif cmd == "TURN_DEG":
            if len(parts) < 2:
                raise ValueError(
                    "Usage: TURN_DEG <deg_right_positive> [speed] [timeout_sec]"
                )
            angle_deg = float(parts[1])
            speed = (
                int(float(parts[2]))
                if len(parts) >= 3
                else DEFAULT_TURN_PWM
            )
            timeout_sec = (
                float(parts[3])
                if len(parts) >= 4
                else max(5.0, abs(angle_deg) * 0.08)
            )
            result = turn_deg(
                angle_deg,
                speed=speed,
                timeout_sec=timeout_sec,
            )
            result["requested_legacy_right_positive_deg"] = angle_deg
            send(
                ok=(result["status"] == "done"),
                event="turn_deg_result",
                **result
            )

        elif cmd == "DRIVE_REL":
            if len(parts) < 3:
                raise ValueError(
                    "Usage: DRIVE_REL <cm> <yaw_ccw_deg> [speed] [timeout_sec]"
                )
            distance_cm = float(parts[1])
            yaw_ccw_deg = float(parts[2])
            speed = (
                int(float(parts[3]))
                if len(parts) >= 4
                else DEFAULT_DRIVE_PWM
            )
            timeout_sec = (
                float(parts[4])
                if len(parts) >= 5
                else 10.0
            )
            result = drive_relative(
                distance_cm,
                yaw_ccw_deg,
                speed=speed,
                timeout_sec=timeout_sec,
            )
            send(
                ok=(result["status"] == "done"),
                event="drive_relative_result",
                **result
            )

        elif cmd == "MOVE_TICKS":
            if len(parts) < 3:
                raise ValueError(
                    "Usage: MOVE_TICKS <left_ticks> <right_ticks> [speed] [timeout_sec]"
                )
            left_target = float(parts[1])
            right_target = float(parts[2])
            speed = (
                int(float(parts[3]))
                if len(parts) >= 4
                else DEFAULT_MOVE_PWM
            )
            timeout_sec = (
                float(parts[4])
                if len(parts) >= 5
                else 10.0
            )
            result = move_ticks(
                left_target,
                right_target,
                speed=speed,
                timeout_sec=timeout_sec,
            )
            send(
                ok=(result["status"] == "done"),
                event="move_ticks_result",
                **result
            )

        elif cmd == "GET_CAL":
            send(
                ok=True,
                event="track_calibration",
                calibration=current_calibration_dict(),
            )

        elif cmd == "SET_TRACK_CAL":
            if len(parts) != 4:
                raise ValueError(
                    "Usage: SET_TRACK_CAL <left_ticks_per_cm> <right_ticks_per_cm> <track_width_cm>"
                )
            LEFT_TICKS_PER_CM = positive_float(
                parts[1],
                "left_ticks_per_cm",
            )
            RIGHT_TICKS_PER_CM = positive_float(
                parts[2],
                "right_ticks_per_cm",
            )
            EFFECTIVE_TRACK_WIDTH_CM = positive_float(
                parts[3],
                "track_width_cm",
            )
            send(
                ok=True,
                event="track_calibration_set",
                calibration=current_calibration_dict(),
            )

        elif cmd == "SET_LINEAR_CAL":
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SET_LINEAR_CAL <left_ticks_per_cm> <right_ticks_per_cm>"
                )
            LEFT_TICKS_PER_CM = positive_float(
                parts[1],
                "left_ticks_per_cm",
            )
            RIGHT_TICKS_PER_CM = positive_float(
                parts[2],
                "right_ticks_per_cm",
            )
            send(
                ok=True,
                event="linear_calibration_set",
                calibration=current_calibration_dict(),
            )

        elif cmd == "SET_TRACK_WIDTH":
            if len(parts) != 2:
                raise ValueError(
                    "Usage: SET_TRACK_WIDTH <track_width_cm>"
                )
            EFFECTIVE_TRACK_WIDTH_CM = positive_float(
                parts[1],
                "track_width_cm",
            )
            send(
                ok=True,
                event="track_width_set",
                calibration=current_calibration_dict(),
            )

        elif cmd == "SET_CAL":
            # Backward-compatible old calibration command:
            # SET_CAL <common_ticks_per_cm> <ticks_per_deg>
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SET_CAL <legacy_common_ticks_per_cm> <legacy_ticks_per_deg>"
                )
            common_ticks_per_cm = positive_float(
                parts[1],
                "legacy_common_ticks_per_cm",
            )
            legacy_ticks_per_deg = positive_float(
                parts[2],
                "legacy_ticks_per_deg",
            )
            LEFT_TICKS_PER_CM = common_ticks_per_cm
            RIGHT_TICKS_PER_CM = common_ticks_per_cm
            EFFECTIVE_TRACK_WIDTH_CM = (
                legacy_ticks_per_deg
                * 360.0
                / (math.pi * common_ticks_per_cm)
            )
            send(
                ok=True,
                event="legacy_calibration_migrated",
                calibration=current_calibration_dict(),
            )

        elif cmd in ("SERVO", "SERVO_DEG"):
            if pca is None:
                raise ValueError("PCA9685 not available")
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SERVO_DEG <channel> <angle_deg>"
                )
            channel = int(parts[1])
            angle_deg = float(parts[2])
            requested_us, applied_us = pca.set_servo_deg(
                channel,
                angle_deg,
            )
            send(
                ok=True,
                event="servo_deg_set",
                channel=channel,
                servo_name=SERVO_NAMES[channel],
                angle_deg=angle_deg,
                requested_us=requested_us,
                applied_us=applied_us,
            )

        elif cmd == "SERVO_US":
            if pca is None:
                raise ValueError("PCA9685 not available")
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SERVO_US <channel> <pulse_us>"
                )
            channel = int(parts[1])
            requested_us = float(parts[2])
            applied_us = pca.set_servo_us(
                channel,
                requested_us,
            )
            send(
                ok=True,
                event="servo_us_set",
                channel=channel,
                servo_name=SERVO_NAMES[channel],
                requested_us=requested_us,
                applied_us=applied_us,
            )

        elif cmd == "ARM_US":
            if pca is None:
                raise ValueError("PCA9685 not available")
            if len(parts) != 4:
                raise ValueError(
                    "Usage: ARM_US <left_us> <right_us> <gripper_us>"
                )
            requested_us = [
                float(parts[1]),
                float(parts[2]),
                float(parts[3]),
            ]
            applied_us = pca.set_arm_us(
                requested_us[0],
                requested_us[1],
                requested_us[2],
            )
            send(
                ok=True,
                event="arm_us_set",
                requested_us=requested_us,
                applied_us=applied_us,
                channels=[0, 1, 2],
            )

        elif cmd == "ARM_DEG":
            if pca is None:
                raise ValueError("PCA9685 not available")
            if len(parts) != 4:
                raise ValueError(
                    "Usage: ARM_DEG <left_deg> <right_deg> <gripper_deg>"
                )
            requested_deg, requested_us, applied_us = pca.set_arm_deg(
                float(parts[1]),
                float(parts[2]),
                float(parts[3]),
            )
            send(
                ok=True,
                event="arm_deg_set",
                requested_deg=requested_deg,
                requested_us=requested_us,
                applied_us=applied_us,
                channels=[0, 1, 2],
            )

        elif cmd == "SERVO_OFF":
            if pca is None:
                raise ValueError("PCA9685 not available")
            if len(parts) != 2:
                raise ValueError(
                    "Usage: SERVO_OFF <channel>"
                )
            channel = int(parts[1])
            pca.servo_off(channel)
            send(
                ok=True,
                event="servo_off",
                channel=channel,
                servo_name=SERVO_NAMES[channel],
            )

        elif cmd == "ARM_OFF":
            if pca is None:
                raise ValueError("PCA9685 not available")
            pca.arm_off()
            send(
                ok=True,
                event="arm_off",
                channels=[0, 1, 2],
            )

        elif cmd == "SERVO_STATE?":
            send(
                ok=True,
                event="servo_state",
                pulse_us={
                    "0": last_servo_us[0],
                    "1": last_servo_us[1],
                    "2": last_servo_us[2],
                },
            )

        elif cmd == "SERVO_CAL?":
            calibration = {}
            for channel in ARM_SERVO_CHANNELS:
                calibration[str(channel)] = {
                    "name": SERVO_NAMES[channel],
                    "pulse_calibration_us": list(SERVO_PULSE_US[channel]),
                    "angle_calibration": list(SERVO_ANGLE_CAL[channel]),
                    "last_servo_us": last_servo_us[channel],
                }
            send(
                ok=True,
                event="servo_calibration",
                calibration=calibration,
            )

        elif cmd == "SET_PWM_LIMIT":
            if len(parts) != 2:
                raise ValueError(
                    "Usage: SET_PWM_LIMIT <0-255>"
                )
            PWM_LIMIT = int(
                clamp(int(float(parts[1])), 0, PWM_ABS_MAX)
            )
            send(
                ok=True,
                event="pwm_limit_set",
                pwm_limit=PWM_LIMIT,
            )

        elif cmd == "SET_MIN_PWM":
            if len(parts) != 2:
                raise ValueError(
                    "Usage: SET_MIN_PWM <0-255>"
                )
            MIN_MOTION_PWM = int(
                clamp(int(float(parts[1])), 0, PWM_ABS_MAX)
            )
            send(
                ok=True,
                event="min_pwm_set",
                min_motion_pwm=MIN_MOTION_PWM,
            )

        elif cmd == "GET_TURN_CONTROL":
            send(
                ok=True,
                event="turn_control",
                turn_control=current_turn_control_dict(),
            )

        elif cmd == "SET_TURN_CONTROL":
            if len(parts) != 5:
                raise ValueError(
                    "Usage: SET_TURN_CONTROL <default_pwm> <min_pwm> <kp_sync> <max_correction_pwm>"
                )

            DEFAULT_TURN_PWM = int(clamp(
                int(float(parts[1])),
                1,
                PWM_ABS_MAX,
            ))
            MIN_TURN_PWM = int(clamp(
                int(float(parts[2])),
                1,
                PWM_ABS_MAX,
            ))
            TURN_KP_SYNC = max(0.0, float(parts[3]))
            TURN_MAX_CORRECTION_PWM = int(clamp(
                int(float(parts[4])),
                0,
                PWM_ABS_MAX,
            ))

            if DEFAULT_TURN_PWM < MIN_TURN_PWM:
                DEFAULT_TURN_PWM = MIN_TURN_PWM

            send(
                ok=True,
                event="turn_control_set",
                turn_control=current_turn_control_dict(),
            )

        elif cmd == "SET_KP_SYNC":
            if len(parts) != 2:
                raise ValueError(
                    "Usage: SET_KP_SYNC <value>"
                )
            KP_SYNC = float(parts[1])
            send(
                ok=True,
                event="kp_sync_set",
                kp_sync=KP_SYNC,
            )

        elif cmd == "SET_MOTOR_INVERT":
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SET_MOTOR_INVERT <left 0/1> <right 0/1>"
                )
            MOTOR_LEFT_INVERT = bool(int(parts[1]))
            MOTOR_RIGHT_INVERT = bool(int(parts[2]))
            send(
                ok=True,
                event="motor_invert_set",
                left=MOTOR_LEFT_INVERT,
                right=MOTOR_RIGHT_INVERT,
            )

        elif cmd == "SET_ENCODER_INVERT":
            if len(parts) != 3:
                raise ValueError(
                    "Usage: SET_ENCODER_INVERT <left 0/1> <right 0/1>"
                )
            ENC_LEFT_INVERT = bool(int(parts[1]))
            ENC_RIGHT_INVERT = bool(int(parts[2]))
            left_encoder.invert = ENC_LEFT_INVERT
            right_encoder.invert = ENC_RIGHT_INVERT
            send(
                ok=True,
                event="encoder_invert_set",
                left=ENC_LEFT_INVERT,
                right=ENC_RIGHT_INVERT,
            )

        elif cmd == "SAVE_CONFIG":
            cfg = save_config()
            send(
                ok=True,
                event="config_saved",
                config=cfg,
            )

        elif cmd == "LOAD_CONFIG":
            cfg = load_config()
            if cfg is None:
                send(ok=False, event="config_load_failed")
            else:
                left_encoder.invert = ENC_LEFT_INVERT
                right_encoder.invert = ENC_RIGHT_INVERT
                send(
                    ok=True,
                    event="config_loaded",
                    config=cfg,
                    calibration=current_calibration_dict(),
                )

        else:
            send(
                ok=False,
                event="unknown_command",
                command=line,
            )

    except Exception as error:
        stop_motors()
        send(
            ok=False,
            event="command_error",
            command=line,
            error=str(error),
        )


# ============================================================
# Boot
# ============================================================

def init_pca9685():
    global pca

    try:
        devices = i2c.scan()
        if PCA9685_ADDR not in devices:
            pca = None
            send(
                ok=False,
                event="pca9685_not_found",
                i2c_devices=devices,
            )
            return

        pca = PCA9685(i2c, PCA9685_ADDR)
        send(
            ok=True,
            event="pca9685_ready",
            address=PCA9685_ADDR,
            i2c_devices=devices,
        )

    except Exception as error:
        pca = None
        send(
            ok=False,
            event="pca9685_init_failed",
            error=str(error),
        )


def boot():
    cfg = load_config()

    left_encoder.invert = ENC_LEFT_INVERT
    right_encoder.invert = ENC_RIGHT_INVERT

    stop_motors()
    reset_encoders()
    reset_odometry()
    init_pca9685()

    send(
        ok=True,
        event="boot",
        firmware=FIRMWARE_NAME,
        version=FIRMWARE_VERSION,
        config_loaded=(cfg is not None),
        pwm_limit=PWM_LIMIT,
        turn_control=current_turn_control_dict(),
        calibration=current_calibration_dict(),
        odometry=current_odometry_dict(),
        pca9685_available=(pca is not None),
        arm_outputs="off",
        pinmap={
            "i2c_sda": I2C_SDA_PIN,
            "i2c_scl": I2C_SCL_PIN,
            "left_enc_a": LEFT_ENC_A_PIN,
            "left_enc_b": LEFT_ENC_B_PIN,
            "right_enc_a": RIGHT_ENC_A_PIN,
            "right_enc_b": RIGHT_ENC_B_PIN,
            "left_pwm": LEFT_PWM_PIN,
            "left_dir": LEFT_DIR_PIN,
            "right_pwm": RIGHT_PWM_PIN,
            "right_dir": RIGHT_DIR_PIN,
        },
    )


boot()


# ============================================================
# Main loop
# ============================================================

while True:
    try:
        line = sys.stdin.readline()
        handle_command(line)
    except Exception as error:
        stop_motors()
        send(
            ok=False,
            event="main_loop_error",
            error=str(error),
        )
        time.sleep_ms(100)