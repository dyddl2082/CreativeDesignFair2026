from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_pkg = Path(get_package_share_directory('macrobot_description'))
    moveit_pkg = Path(get_package_share_directory('macrobot_moveit_config'))
    xacro_file = description_pkg / 'urdf' / 'macrobot_arm_kinematic.urdf.xacro'
    srdf_file = moveit_pkg / 'config' / 'macrobot.srdf'

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
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[robot_description],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
            parameters=[robot_description],
        ),
    ])
