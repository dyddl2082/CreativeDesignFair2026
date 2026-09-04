from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_pkg = Path(get_package_share_directory('macrobot_description'))
    moveit_pkg = Path(get_package_share_directory('macrobot_moveit_config'))
    safe_pkg = Path(get_package_share_directory('macrobot_safe_region'))

    xacro_file = description_pkg / 'urdf' / 'macrobot_full_collision.urdf.xacro'
    srdf_file = moveit_pkg / 'config' / 'macrobot_full_collision.srdf'

    output_directory = LaunchConfiguration('output_directory')
    scan_config = LaunchConfiguration('scan_config')

    robot_description = {
        'robot_description': ParameterValue(
            Command([FindExecutable(name='xacro'), ' ', str(xacro_file)]),
            value_type=str,
        )
    }
    robot_description_semantic = {
        'robot_description_semantic': ParameterValue(
            srdf_file.read_text(), value_type=str
        )
    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'output_directory',
            default_value='~/MacRobot/data/safe_region_full',
        ),
        DeclareLaunchArgument(
            'scan_config',
            default_value=str(safe_pkg / 'config' / 'full_coarse_scan.yaml'),
        ),
        Node(
            package='macrobot_safe_region',
            executable='safe_region_generator',
            name='safe_region_generator',
            output='screen',
            parameters=[
                robot_description,
                robot_description_semantic,
                str(safe_pkg / 'config' / 'actuator_limits.yaml'),
                scan_config,
                {
                    'robot_model_mode': 'serial_2r',
                    'model_revision': 'macrobot-serial-2axis-2026-09-04-r4',
                    'output_directory': output_directory,
                },
            ],
        ),
    ])
