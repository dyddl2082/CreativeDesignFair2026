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
    xacro_file = pkg / 'urdf' / 'macrobot_full_visual.urdf.xacro'
    rviz_file = pkg / 'rviz' / 'display.rviz'
    kinematics_config = pkg / 'config' / 'kinematics.yaml'

    use_sim_time = LaunchConfiguration('use_sim_time')
    auto_apply_ik = LaunchConfiguration('auto_apply_ik')
    start_rviz = LaunchConfiguration('start_rviz')

    description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', str(xacro_file)]),
        value_type=str,
    )
    robot_description = {'robot_description': description}

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'auto_apply_ik',
            default_value='true',
            description='Directly apply raw IK solutions. Disable when using IK validator.',
        ),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'use_sim_time': use_sim_time}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='world_to_base_link',
            output='screen',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0',
                '--roll', '0', '--pitch', '0', '--yaw', '0',
                '--frame-id', 'world',
                '--child-frame-id', 'base_link',
            ],
        ),
        # The only /joint_states publisher for the full closed-linkage model.
        Node(
            package='macrobot_arm_kinematics',
            executable='linkage_state_node',
            name='macrobot_linkage_state_node',
            output='screen',
            parameters=[str(kinematics_config)],
        ),
        Node(
            package='macrobot_arm_kinematics',
            executable='ik_node',
            name='macrobot_arm_ik_node',
            output='screen',
            parameters=[
                str(kinematics_config),
                {'auto_apply_ik': ParameterValue(auto_apply_ik, value_type=bool)},
            ],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', str(rviz_file)],
            condition=IfCondition(start_rviz),
        ),
    ])
