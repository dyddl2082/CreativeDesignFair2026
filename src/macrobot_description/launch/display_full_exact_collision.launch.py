from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = Path(get_package_share_directory('macrobot_description'))
    xacro_file = pkg / 'urdf' / 'macrobot_full_exact_gripper.urdf.xacro'
    rviz_file = pkg / 'rviz' / 'display.rviz'
    kinematics_config = pkg / 'config' / 'kinematics.yaml'

    start_rviz = LaunchConfiguration('start_rviz')
    description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', str(xacro_file)]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument('start_rviz', default_value='true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': description}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0',
                '--roll', '0', '--pitch', '0', '--yaw', '0',
                '--frame-id', 'world', '--child-frame-id', 'base_link',
            ],
        ),
        Node(
            package='macrobot_arm_kinematics',
            executable='linkage_state_node',
            output='screen',
            parameters=[str(kinematics_config)],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', str(rviz_file)],
            condition=IfCondition(start_rviz),
        ),
    ])
