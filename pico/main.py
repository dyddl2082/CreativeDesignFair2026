from machine import Pin, PWM, I2C
import machine
import time
import sys
import select
import ujson


# ============================================================
# MacRobot Pico 2 H Firmware
# Role:
# - USB serial command receiver from Raspberry Pi
# - MDD10A motor driver control
# - Quadrature encoder reading
# - Encoder-based move/turn control
# - PCA9685 servo control
#
# No VL53L1X distance sensor in this version.
# D435f depth is handled on Raspberry Pi side.
# ============================================================


# -----------------------------
# Version
# -----------------------------

FIRMWARE_NAME = "MacRobot_Pico_MotorController"
FIRMWARE_VERSION = "0.2.0-arm-us"


# -----------------------------
# Pin map
# -----------------------------

# I2C0 for PCA9685
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1

# Encoders
LEFT_ENC_A_PIN = 2
LEFT_ENC_B_PIN = 3
RIGHT_ENC_A_PIN = 4
RIGHT_ENC_B_PIN = 5

# MDD10A motor driver
LEFT_PWM_PIN = 10
LEFT_DIR_PIN = 11
RIGHT_PWM_PIN = 12
RIGHT_DIR_PIN = 13


# -----------------------------
# Motor control constants
# -----------------------------

PWM_FREQ_HZ = 20000

PWM_ABS_MAX = 255
PWM_LIMIT = 180       # 2S LiPo + 6V motor protection. 180/255 ~= 70%.
MIN_MOTION_PWM = 45   # minimum PWM used during closed-loop motion

DEFAULT_MOVE_PWM = 120
DEFAULT_TURN_PWM = 100

# Calibration values.
# These MUST be calibrated on the real robot.
TICKS_PER_CM = 180.0
TICKS_PER_DEG = 20.0

# Encoder/motor direction correction.
# Change these if forward command moves backward or encoder sign is reversed.
MOTOR_LEFT_INVERT = False
MOTOR_RIGHT_INVERT = False
ENC_LEFT_INVERT = False
ENC_RIGHT_INVERT = False

# Encoder synchronization gain.
# Higher = stronger correction when one side runs ahead.
KP_SYNC = 0.60

CONTROL_DT_MS = 20
STALL_TIMEOUT_MS = 1800
STALL_MIN_PROGRESS_TICKS = 3


# -----------------------------
# PCA9685 constants
# -----------------------------

PCA9685_ADDR = 0x40
SERVO_FREQ_HZ = 50

# PCA9685 channels
# CH0: left MG996R, arm lift
# CH1: right MG996R, wrist/tilt
# CH2: MG90S, gripper
ARM_SERVO_CHANNELS = (0, 1, 2)

SERVO_NAMES = {
    0: "left_mg996r_lift",
    1: "right_mg996r_tilt",
    2: "mg90s_gripper",
}

SERVO_ANGLE_CAL = {
    0: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),  # left MG996R
    1: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),  # right MG996R
    2: (0.0, 500.0, 90.0, 1500.0, 180.0, 2500.0),  # MG90S
}

SERVO_PULSE_US = {
    0: (500.0, 1500.0, 2500.0),  # left MG996R
    1: (500.0, 1500.0, 2500.0),  # right MG996R
    2: (500.0, 1500.0, 2500.0),  # MG90S gripper
}

SERVO_LIMITS_US = {
    0: (1000.0, 2000.0),
    1: (1000.0, 2000.0),
    2: (1000.0, 2000.0),
}

last_servo_us = {
    0: None,
    1: None,
    2: None,
}


# -----------------------------
# Config persistence
# -----------------------------

CONFIG_PATH = "pico_config.json"


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def send(ok=True, event="response", **kwargs):
    payload = {
        "ok": bool(ok),
        "event": event,
        "time_ms": time.ticks_ms(),
    }
    payload.update(kwargs)

    try:
        sys.stdout.write(ujson.dumps(payload) + "\n")
    except Exception:
        # Fallback for unexpected JSON issue
        sys.stdout.write('{"ok":false,"event":"json_error"}\n')

def lerp(x, x0, y0, x1, y1):
    if abs(x1 - x0) < 1e-9:
        return y0

    t = (x - x0) / (x1 - x0)

    return y0 + t * (y1 - y0)


def servo_deg_to_us(channel, angle_deg):
    channel = int(channel)

    if channel not in SERVO_ANGLE_CAL:
        raise ValueError(
            "Servo angle calibration missing for channel {}".format(channel)
        )

    (
        deg_min,
        us_min,
        deg_center,
        us_center,
        deg_max,
        us_max,
    ) = SERVO_ANGLE_CAL[channel]

    angle_deg = float(angle_deg)

    # 보정표 범위 밖의 각도는 보정표 범위로 먼저 제한한다.
    if angle_deg < deg_min:
        angle_deg = deg_min

    if angle_deg > deg_max:
        angle_deg = deg_max

    # center 기준으로 좌우를 따로 선형 보간한다.
    # 서보가 완벽히 선형이 아니더라도 이 방식이 단일 직선보다 낫다.
    if angle_deg <= deg_center:
        pulse_us = lerp(
            angle_deg,
            deg_min,
            us_min,
            deg_center,
            us_center,
        )
    else:
        pulse_us = lerp(
            angle_deg,
            deg_center,
            us_center,
            deg_max,
            us_max,
        )

    return pulse_us


# ============================================================
# Encoder
# ============================================================

class QuadratureEncoder:
    # transition table for old_state << 2 | new_state
    _TABLE = (
        0, -1, 1, 0,
        1, 0, 0, -1,
        -1, 0, 0, 1,
        0, 1, -1, 0
    )

    def __init__(self, pin_a, pin_b, invert=False):
        self.a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.invert = invert
        self.count = 0
        self.state = (self.a.value() << 1) | self.b.value()

        self.a.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=self._callback
        )
        self.b.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=self._callback
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

        # Do not drive an unknown physical arm pose at boot.
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
            25_000_000.0
            / (4096.0 * float(freq_hz))
            - 1.0
        )
        prescale = int(prescale_value + 0.5)

        old_mode = self.read8(self.MODE1)
        sleep_mode = (old_mode & 0x7F) | 0x10

        self.write8(self.MODE1, sleep_mode)
        self.write8(self.PRESCALE, prescale)
        self.write8(self.MODE1, old_mode)
        time.sleep_ms(5)

        # Restart + auto-increment + all-call.
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

    def _calibration(self, channel):
        channel = int(channel)
        if channel not in SERVO_PULSE_US:
            raise ValueError(
                "Servo channel is not configured: {}".format(channel)
            )
        return SERVO_PULSE_US[channel]

    def _clamp_servo_us(self, channel, pulse_us):
        channel = int(channel)

        if channel not in SERVO_PULSE_US:
            raise ValueError(
                "Servo channel is not configured: {}".format(channel)
            )

        values = SERVO_PULSE_US[channel]

        # (min, center, max) 또는 (min, max) 둘 다 허용
        minimum = float(values[0])
        maximum = float(values[-1])

        return max(
            minimum,
            min(maximum, float(pulse_us)),
        )

    def _write_servo_us_unchecked(self, channel, pulse_us):
        # 50 Hz period is 20,000 us.
        ticks = int(
            round(float(pulse_us) * 4096.0 / 20_000.0)
        )
        ticks = int(clamp(ticks, 0, 4095))
        self.set_pwm(int(channel), 0, ticks)

    def set_servo_us(self, channel, pulse_us):
        channel = int(channel)
        applied_us = self._clamp_servo_us(
            channel,
            pulse_us,
        )
        self._write_servo_us_unchecked(
            channel,
            applied_us,
        )
        last_servo_us[channel] = applied_us
        return applied_us

    def set_servo_deg(self, channel, angle_deg):
        channel = int(channel)
        angle_deg = float(angle_deg)

        requested_us = servo_deg_to_us(
            channel,
            angle_deg,
        )

        applied_us = self.set_servo_us(
            channel,
            requested_us,
        )

        return requested_us, applied_us

    def set_arm_deg(self, lift_deg, tilt_deg, gripper_deg):
        requested_deg = {
            0: float(lift_deg),
            1: float(tilt_deg),
            2: float(gripper_deg),
        }

        requested_us = {
            channel: servo_deg_to_us(
                channel,
                requested_deg[channel],
            )
            for channel in ARM_SERVO_CHANNELS
        }

        applied = self.set_arm_us(
            requested_us[0],
            requested_us[1],
            requested_us[2],
        )

        return (
            [
                requested_deg[0],
                requested_deg[1],
                requested_deg[2],
            ],
            [
                requested_us[0],
                requested_us[1],
                requested_us[2],
            ],
            applied,
        )

    def set_arm_us(self, lift_us, tilt_us, gripper_us):
        requested = {
            0: float(lift_us),
            1: float(tilt_us),
            2: float(gripper_us),
        }

        # Validate/clamp all three before changing any output.
        applied = {
            channel: self._clamp_servo_us(
                channel,
                requested[channel],
            )
            for channel in ARM_SERVO_CHANNELS
        }

        # Sequential I2C writes are much faster than mechanical motion and
        # belong to one serial command/trajectory sample.
        for channel in ARM_SERVO_CHANNELS:
            self._write_servo_us_unchecked(
                channel,
                applied[channel],
            )
            last_servo_us[channel] = applied[channel]

        return [
            applied[0],
            applied[1],
            applied[2],
        ]

    def set_servo_angle(self, channel, angle_deg):
        # Legacy bench-test command. Normal arm motion uses SERVO_US/ARM_US.
        channel = int(channel)
        angle_deg = clamp(float(angle_deg), 0.0, 180.0)
        minimum, center, maximum = self._calibration(channel)

        if angle_deg <= 90.0:
            ratio = angle_deg / 90.0
            pulse_us = minimum + ratio * (center - minimum)
        else:
            ratio = (angle_deg - 90.0) / 90.0
            pulse_us = center + ratio * (maximum - center)

        return self.set_servo_us(channel, pulse_us)

    def servo_off(self, channel):
        channel = int(channel)
        if channel not in ARM_SERVO_CHANNELS:
            raise ValueError(
                "Arm servo channel is not configured: {}".format(channel)
            )

        # OFF_H bit 4 = FULL OFF. set_pwm packs 4096 as 0x1000.
        self.set_pwm(channel, 0, 4096)
        last_servo_us[channel] = None

    def arm_off(self):
        for channel in ARM_SERVO_CHANNELS:
            self.servo_off(channel)


# ============================================================
# Hardware init
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
    invert=ENC_LEFT_INVERT
)

right_encoder = QuadratureEncoder(
    RIGHT_ENC_A_PIN,
    RIGHT_ENC_B_PIN,
    invert=ENC_RIGHT_INVERT
)

i2c = I2C(
    0,
    scl=Pin(I2C_SCL_PIN),
    sda=Pin(I2C_SDA_PIN),
    freq=400000
)

pca = None


# -----------------------------
# Serial polling
# -----------------------------

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

stop_requested = False
estopped = False


# ============================================================
# Config
# ============================================================

def save_config():
    cfg = {
        "PWM_LIMIT": PWM_LIMIT,
        "MIN_MOTION_PWM": MIN_MOTION_PWM,
        "TICKS_PER_CM": TICKS_PER_CM,
        "TICKS_PER_DEG": TICKS_PER_DEG,
        "MOTOR_LEFT_INVERT": MOTOR_LEFT_INVERT,
        "MOTOR_RIGHT_INVERT": MOTOR_RIGHT_INVERT,
        "ENC_LEFT_INVERT": ENC_LEFT_INVERT,
        "ENC_RIGHT_INVERT": ENC_RIGHT_INVERT,
        "KP_SYNC": KP_SYNC,
    }

    with open(CONFIG_PATH, "w") as f:
        f.write(ujson.dumps(cfg))

    return cfg


def load_config():
    global PWM_LIMIT
    global MIN_MOTION_PWM
    global TICKS_PER_CM
    global TICKS_PER_DEG
    global MOTOR_LEFT_INVERT
    global MOTOR_RIGHT_INVERT
    global ENC_LEFT_INVERT
    global ENC_RIGHT_INVERT
    global KP_SYNC

    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = ujson.loads(f.read())

        PWM_LIMIT = int(cfg.get("PWM_LIMIT", PWM_LIMIT))
        MIN_MOTION_PWM = int(cfg.get("MIN_MOTION_PWM", MIN_MOTION_PWM))
        TICKS_PER_CM = float(cfg.get("TICKS_PER_CM", TICKS_PER_CM))
        TICKS_PER_DEG = float(cfg.get("TICKS_PER_DEG", TICKS_PER_DEG))
        MOTOR_LEFT_INVERT = bool(cfg.get("MOTOR_LEFT_INVERT", MOTOR_LEFT_INVERT))
        MOTOR_RIGHT_INVERT = bool(cfg.get("MOTOR_RIGHT_INVERT", MOTOR_RIGHT_INVERT))
        ENC_LEFT_INVERT = bool(cfg.get("ENC_LEFT_INVERT", ENC_LEFT_INVERT))
        ENC_RIGHT_INVERT = bool(cfg.get("ENC_RIGHT_INVERT", ENC_RIGHT_INVERT))
        KP_SYNC = float(cfg.get("KP_SYNC", KP_SYNC))

        return cfg

    except Exception:
        return None


# ============================================================
# Motor functions
# ============================================================

def pwm_to_duty_u16(pwm_value):
    pwm_value = clamp(abs(int(pwm_value)), 0, PWM_ABS_MAX)
    return int(pwm_value * 65535 / PWM_ABS_MAX)


def set_motors(left_value, right_value):
    global estopped

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
        left_pwm.duty_u16(pwm_to_duty_u16(left_value))
    else:
        left_dir.value(0)
        left_pwm.duty_u16(pwm_to_duty_u16(left_value))

    if right_value >= 0:
        right_dir.value(1)
        right_pwm.duty_u16(pwm_to_duty_u16(right_value))
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


def motion_pwm_from_magnitude(magnitude):
    magnitude = abs(float(magnitude))

    if magnitude <= 1:
        return 0

    magnitude = clamp(magnitude, MIN_MOTION_PWM, PWM_LIMIT)
    return int(magnitude)


def check_immediate_serial():
    """
    During blocking motion, allow STOP and ESTOP.
    Other commands are rejected as BUSY.
    """
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


def move_ticks(left_target, right_target, speed=DEFAULT_MOVE_PWM, timeout_sec=10.0):
    """
    Relative encoder motion.
    left_target/right_target can be positive or negative.
    This function uses encoder progress synchronization to reduce drift.
    """
    global stop_requested

    if estopped:
        return {
            "status": "estopped",
            "left_count": left_encoder.read(),
            "right_count": right_encoder.read(),
        }

    stop_requested = False
    reset_encoders()

    left_target = float(left_target)
    right_target = float(right_target)

    left_abs_target = abs(left_target)
    right_abs_target = abs(right_target)

    left_sign = sign(left_target)
    right_sign = sign(right_target)

    speed = int(clamp(speed, 0, PWM_LIMIT))

    if left_abs_target < 1 and right_abs_target < 1:
        stop_motors()
        return {
            "status": "done",
            "left_count": 0,
            "right_count": 0,
        }

    start_ms = time.ticks_ms()
    last_progress_ms = start_ms
    last_total_progress = 0

    while True:
        now_ms = time.ticks_ms()

        if check_immediate_serial():
            stop_motors()
            return {
                "status": "stopped",
                "left_count": left_encoder.read(),
                "right_count": right_encoder.read(),
            }

        if stop_requested:
            stop_motors()
            return {
                "status": "stopped",
                "left_count": left_encoder.read(),
                "right_count": right_encoder.read(),
            }

        if timeout_sec > 0:
            if time.ticks_diff(now_ms, start_ms) > int(timeout_sec * 1000):
                stop_motors()
                return {
                    "status": "timeout",
                    "left_count": left_encoder.read(),
                    "right_count": right_encoder.read(),
                }

        left_count, right_count = get_encoders()

        left_done = True if left_abs_target < 1 else abs(left_count) >= left_abs_target
        right_done = True if right_abs_target < 1 else abs(right_count) >= right_abs_target

        if left_done and right_done:
            stop_motors()
            return {
                "status": "done",
                "left_count": left_count,
                "right_count": right_count,
            }

        left_progress = 1.0 if left_abs_target < 1 else clamp(abs(left_count) / left_abs_target, 0.0, 1.0)
        right_progress = 1.0 if right_abs_target < 1 else clamp(abs(right_count) / right_abs_target, 0.0, 1.0)

        avg_progress = 0.5 * (left_progress + right_progress)
        remaining = clamp(1.0 - avg_progress, 0.0, 1.0)

        # Slow down in the last 25 percent.
        if remaining < 0.25:
            speed_scale = clamp(remaining / 0.25, 0.35, 1.0)
        else:
            speed_scale = 1.0

        base = speed * speed_scale

        # If left progresses faster than right, reduce left magnitude and increase right magnitude.
        progress_error = left_progress - right_progress
        correction = KP_SYNC * progress_error * speed

        left_mag = base - correction
        right_mag = base + correction

        if left_done:
            left_cmd = 0
        else:
            left_cmd = left_sign * motion_pwm_from_magnitude(left_mag)

        if right_done:
            right_cmd = 0
        else:
            right_cmd = right_sign * motion_pwm_from_magnitude(right_mag)

        set_motors(left_cmd, right_cmd)

        total_progress = abs(left_count) + abs(right_count)

        if total_progress > last_total_progress + STALL_MIN_PROGRESS_TICKS:
            last_total_progress = total_progress
            last_progress_ms = now_ms
        else:
            if time.ticks_diff(now_ms, last_progress_ms) > STALL_TIMEOUT_MS:
                stop_motors()
                return {
                    "status": "stall",
                    "left_count": left_count,
                    "right_count": right_count,
                }

        time.sleep_ms(CONTROL_DT_MS)


def move_cm(distance_cm, speed=DEFAULT_MOVE_PWM, timeout_sec=10.0):
    ticks = float(distance_cm) * TICKS_PER_CM
    return move_ticks(ticks, ticks, speed=speed, timeout_sec=timeout_sec)


def turn_deg(angle_deg, speed=DEFAULT_TURN_PWM, timeout_sec=8.0):
    """
    Positive angle = right turn by default.
    If actual direction is opposite, invert motor direction or call with negative sign.
    """
    ticks = float(angle_deg) * TICKS_PER_DEG
    return move_ticks(ticks, -ticks, speed=speed, timeout_sec=timeout_sec)


# ============================================================
# Command handling
# ============================================================

def handle_command(line):
    global stop_requested
    global estopped
    global PWM_LIMIT
    global MIN_MOTION_PWM
    global TICKS_PER_CM
    global TICKS_PER_DEG
    global MOTOR_LEFT_INVERT
    global MOTOR_RIGHT_INVERT
    global ENC_LEFT_INVERT
    global ENC_RIGHT_INVERT
    global KP_SYNC
    global pca

    line = line.strip()

    if not line:
        return

    parts = line.split()
    cmd = parts[0].upper()

    try:
        if cmd == "PING":
            send(ok=True, event="pong", firmware=FIRMWARE_NAME, version=FIRMWARE_VERSION)

        elif cmd == "HELP":
            send(
                ok=True,
                event="help",
                commands=[
                    "PING",
                    "STATUS?",
                    "ENC?",
                    "RESET_ENC",
                    "STOP",
                    "ESTOP",
                    "CLEAR_ESTOP",
                    "MOTOR <left_pwm> <right_pwm>",
                    "MOVE_CM <cm> [speed] [timeout_sec]",
                    "TURN_DEG <deg> [speed] [timeout_sec]",
                    "MOVE_TICKS <left_ticks> <right_ticks> [speed] [timeout_sec]",
                    "SERVO <channel> <angle_deg>",
                    "SERVO_US <channel> <pulse_us>",
                    "SERVO_DEG <channel> <angle_deg>",
                    "ARM_DEG <lift_deg> <tilt_deg> <gripper_deg>",
                    "SERVO_CAL?",
                    "ARM_US <lift_us> <tilt_us> <gripper_us>",
                    "SERVO_OFF <channel>",
                    "ARM_OFF",
                    "SERVO_STATE?",
                    "SET_CAL <ticks_per_cm> <ticks_per_deg>",
                    "GET_CAL",
                    "SET_PWM_LIMIT <0-255>",
                    "SET_MIN_PWM <0-255>",
                    "SET_KP_SYNC <value>",
                    "SET_MOTOR_INVERT <left 0/1> <right 0/1>",
                    "SAVE_CONFIG",
                    "LOAD_CONFIG",
                ]
            )

        elif cmd == "STATUS?":
            l, r = get_encoders()
            send(
                ok=True,
                event="status",
                estopped=estopped,
                left_encoder=l,
                right_encoder=r,
                pwm_limit=PWM_LIMIT,
                ticks_per_cm=TICKS_PER_CM,
                ticks_per_deg=TICKS_PER_DEG,
                kp_sync=KP_SYNC,
                pca9685_available=(pca is not None),
                servo_pulse_us={
                    "0": last_servo_us[0],
                    "1": last_servo_us[1],
                    "2": last_servo_us[2],
                },
            )

        elif cmd == "ENC?":
            l, r = get_encoders()
            send(ok=True, event="encoders", left=l, right=r)

        elif cmd == "RESET_ENC":
            reset_encoders()
            send(ok=True, event="encoders_reset")

        elif cmd == "STOP":
            stop_requested = True
            stop_motors()
            send(ok=True, event="stopped")

        elif cmd == "ESTOP":
            stop_requested = True
            estopped = True
            stop_motors()
            send(ok=True, event="estop_latched")

        elif cmd == "CLEAR_ESTOP":
            estopped = False
            stop_requested = False
            stop_motors()
            send(ok=True, event="estop_cleared")

        elif cmd == "MOTOR":
            left = int(float(parts[1]))
            right = int(float(parts[2]))
            set_motors(left, right)
            send(ok=True, event="motor_set", left=left, right=right)

        elif cmd == "MOVE_CM":
            distance = float(parts[1])
            speed = int(float(parts[2])) if len(parts) >= 3 else DEFAULT_MOVE_PWM
            timeout = float(parts[3]) if len(parts) >= 4 else max(5.0, abs(distance) * 0.5)
            result = move_cm(distance, speed=speed, timeout_sec=timeout)
            send(ok=(result["status"] == "done"), event="move_cm_result", distance_cm=distance, **result)

        elif cmd == "TURN_DEG":
            angle = float(parts[1])
            speed = int(float(parts[2])) if len(parts) >= 3 else DEFAULT_TURN_PWM
            timeout = float(parts[3]) if len(parts) >= 4 else max(5.0, abs(angle) * 0.08)
            result = turn_deg(angle, speed=speed, timeout_sec=timeout)
            send(ok=(result["status"] == "done"), event="turn_deg_result", angle_deg=angle, **result)

        elif cmd == "MOVE_TICKS":
            left_target = float(parts[1])
            right_target = float(parts[2])
            speed = int(float(parts[3])) if len(parts) >= 4 else DEFAULT_MOVE_PWM
            timeout = float(parts[4]) if len(parts) >= 5 else 10.0
            result = move_ticks(left_target, right_target, speed=speed, timeout_sec=timeout)
            send(ok=(result["status"] == "done"), event="move_ticks_result", left_target=left_target, right_target=right_target, **result)

        elif cmd == "SERVO":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

            if len(parts) != 3:
                raise ValueError(
                    "Usage: SERVO <channel> <angle_deg>"
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
                command_alias="SERVO",
                channel=channel,
                servo_name=SERVO_NAMES[channel],
                angle_deg=angle_deg,
                requested_us=requested_us,
                applied_us=applied_us,
            )

        elif cmd == "SERVO_US":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

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

        elif cmd == "SERVO_DEG":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

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


        elif cmd == "ARM_DEG":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

            if len(parts) != 4:
                raise ValueError(
                    "Usage: ARM_DEG <lift_deg> <tilt_deg> <gripper_deg>"
                )

            lift_deg = float(parts[1])
            tilt_deg = float(parts[2])
            gripper_deg = float(parts[3])

            requested_deg, requested_us, applied_us = pca.set_arm_deg(
                lift_deg,
                tilt_deg,
                gripper_deg,
            )

            send(
                ok=True,
                event="arm_deg_set",
                requested_deg=requested_deg,
                requested_us=requested_us,
                applied_us=applied_us,
                channels=[0, 1, 2],
            )


        elif cmd == "SERVO_CAL?":
            calibration = {}

            for channel in ARM_SERVO_CHANNELS:
                calibration[str(channel)] = {
                    "name": SERVO_NAMES[channel],
                    "pulse_calibration_us": SERVO_PULSE_US[channel],
                    "pulse_limit_us": (
                        SERVO_PULSE_US[channel][0],
                        SERVO_PULSE_US[channel][-1],
                    ),
                    "angle_calibration": SERVO_ANGLE_CAL[channel],
                    "last_servo_us": last_servo_us[channel],
                }

            send(
                ok=True,
                event="servo_calibration",
                calibration=calibration,
            )


        elif cmd == "ARM_US":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

            if len(parts) != 4:
                raise ValueError(
                    "Usage: ARM_US <lift_us> <tilt_us> <gripper_us>"
                )

            requested = [
                float(parts[1]),
                float(parts[2]),
                float(parts[3]),
            ]
            applied = pca.set_arm_us(
                requested[0],
                requested[1],
                requested[2],
            )

            send(
                ok=True,
                event="arm_us_set",
                requested_us=requested,
                applied_us=applied,
                channels=[0, 1, 2],
            )


        elif cmd == "SERVO_OFF":
            if pca is None:
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

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
                send(
                    ok=False,
                    event="servo_error",
                    message="PCA9685 not available",
                )
                return

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

        elif cmd == "SET_CAL":
            TICKS_PER_CM = float(parts[1])
            TICKS_PER_DEG = float(parts[2])
            send(ok=True, event="calibration_set", ticks_per_cm=TICKS_PER_CM, ticks_per_deg=TICKS_PER_DEG)

        elif cmd == "GET_CAL":
            send(ok=True, event="calibration", ticks_per_cm=TICKS_PER_CM, ticks_per_deg=TICKS_PER_DEG)

        elif cmd == "SET_PWM_LIMIT":
            PWM_LIMIT = int(clamp(int(float(parts[1])), 0, 255))
            send(ok=True, event="pwm_limit_set", pwm_limit=PWM_LIMIT)

        elif cmd == "SET_MIN_PWM":
            MIN_MOTION_PWM = int(clamp(int(float(parts[1])), 0, 255))
            send(ok=True, event="min_pwm_set", min_motion_pwm=MIN_MOTION_PWM)

        elif cmd == "SET_KP_SYNC":
            KP_SYNC = float(parts[1])
            send(ok=True, event="kp_sync_set", kp_sync=KP_SYNC)

        elif cmd == "SET_MOTOR_INVERT":
            MOTOR_LEFT_INVERT = bool(int(parts[1]))
            MOTOR_RIGHT_INVERT = bool(int(parts[2]))
            send(ok=True, event="motor_invert_set", left=MOTOR_LEFT_INVERT, right=MOTOR_RIGHT_INVERT)

        elif cmd == "SET_ENCODER_INVERT":
            ENC_LEFT_INVERT = bool(int(parts[1]))
            ENC_RIGHT_INVERT = bool(int(parts[2]))

            # Existing encoder objects keep their invert field.
            left_encoder.invert = ENC_LEFT_INVERT
            right_encoder.invert = ENC_RIGHT_INVERT

            send(ok=True, event="encoder_invert_set", left=ENC_LEFT_INVERT, right=ENC_RIGHT_INVERT)

        elif cmd == "SAVE_CONFIG":
            cfg = save_config()
            send(ok=True, event="config_saved", config=cfg)

        elif cmd == "LOAD_CONFIG":
            cfg = load_config()
            if cfg is None:
                send(ok=False, event="config_load_failed")
            else:
                left_encoder.invert = ENC_LEFT_INVERT
                right_encoder.invert = ENC_RIGHT_INVERT
                send(ok=True, event="config_loaded", config=cfg)

        else:
            send(ok=False, event="unknown_command", command=line)

    except Exception as e:
        stop_motors()
        send(ok=False, event="command_error", command=line, error=str(e))


# ============================================================
# Boot
# ============================================================

def init_pca9685():
    global pca

    try:
        devices = i2c.scan()

        if PCA9685_ADDR not in devices:
            send(ok=False, event="pca9685_not_found", i2c_devices=devices)
            pca = None
            return

        pca = PCA9685(i2c, PCA9685_ADDR)
        send(ok=True, event="pca9685_ready", address=PCA9685_ADDR, i2c_devices=devices)

    except Exception as e:
        pca = None
        send(ok=False, event="pca9685_init_failed", error=str(e))


def boot():
    cfg = load_config()

    left_encoder.invert = ENC_LEFT_INVERT
    right_encoder.invert = ENC_RIGHT_INVERT

    stop_motors()
    reset_encoders()

    init_pca9685()

    send(
        ok=True,
        event="boot",
        firmware=FIRMWARE_NAME,
        version=FIRMWARE_VERSION,
        config_loaded=(cfg is not None),
        pwm_limit=PWM_LIMIT,
        ticks_per_cm=TICKS_PER_CM,
        ticks_per_deg=TICKS_PER_DEG,
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
        }
    )


boot()


# ============================================================
# Main loop
# ============================================================

while True:
    try:
        line = sys.stdin.readline()
        handle_command(line)

    except Exception as e:
        stop_motors()
        send(ok=False, event="main_loop_error", error=str(e))
        time.sleep_ms(100)
