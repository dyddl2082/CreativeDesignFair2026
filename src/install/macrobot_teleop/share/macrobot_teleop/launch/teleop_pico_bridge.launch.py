from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port')
    baudrate = LaunchConfiguration('baudrate')

    control_mode = LaunchConfiguration('control_mode')

    step_cm = LaunchConfiguration('step_cm')
    turn_deg = LaunchConfiguration('turn_deg')
    step_speed = LaunchConfiguration('step_speed')
    turn_speed = LaunchConfiguration('turn_speed')

    max_pwm = LaunchConfiguration('max_pwm')
    min_pwm = LaunchConfiguration('min_pwm')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/ttyACM0',
            description='Pico serial port'
        ),
        DeclareLaunchArgument(
            'baudrate',
            default_value='115200',
            description='Pico serial baudrate'
        ),
        DeclareLaunchArgument(
            'control_mode',
            default_value='step',
            description='step or velocity'
        ),
        DeclareLaunchArgument(
            'step_cm',
            default_value='5.0',
            description='Step distance in cm for forward/backward key'
        ),
        DeclareLaunchArgument(
            'turn_deg',
            default_value='15.0',
            description='Step turn angle in degrees for left/right key'
        ),
        DeclareLaunchArgument(
            'step_speed',
            default_value='110',
            description='Pico MOVE_CM speed'
        ),
        DeclareLaunchArgument(
            'turn_speed',
            default_value='90',
            description='Pico TURN_DEG speed'
        ),
        DeclareLaunchArgument(
            'max_pwm',
            default_value='110',
            description='Velocity mode max PWM'
        ),
        DeclareLaunchArgument(
            'min_pwm',
            default_value='45',
            description='Velocity mode min PWM'
        ),

        Node(
            package='pico_debug',
            executable='pico_debug_node',
            name='pico_debug_node',
            output='screen',
            parameters=[{
                'serial_port': serial_port,
                'baudrate': ParameterValue(baudrate, value_type=int),
                'interactive': False,
                'auto_reconnect': True,
                'send_stop_on_shutdown': True,
            }],
        ),

        Node(
            package='macrobot_teleop',
            executable='teleop_to_pico_node',
            name='teleop_to_pico_node',
            output='screen',
            parameters=[{
                'cmd_vel_topic': '/cmd_vel',
                'pico_cmd_topic': '/pico_debug/cmd',
                'pico_response_topic': '/pico_debug/response',

                'control_mode': control_mode,

                'step_cm': ParameterValue(step_cm, value_type=float),
                'turn_deg': ParameterValue(turn_deg, value_type=float),
                'step_speed': ParameterValue(step_speed, value_type=int),
                'turn_speed': ParameterValue(turn_speed, value_type=int),

                'max_pwm': ParameterValue(max_pwm, value_type=int),
                'min_pwm': ParameterValue(min_pwm, value_type=int),

                'stop_on_start': True,
                'stop_on_shutdown': True,
            }],
        ),
    ])
