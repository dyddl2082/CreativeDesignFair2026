from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = Path(get_package_share_directory('macrobot_description'))
    xacro_file = pkg / 'urdf' / 'macrobot_arm_kinematic.urdf.xacro'
    rviz_file = pkg / 'rviz' / 'display.rviz'
    kinematics_config = pkg / 'config' / 'kinematics.yaml'

    description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', str(xacro_file)]),
        value_type=str,
    )
    robot_description = {'robot_description': description}

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description],
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
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[
                robot_description,
                {'rate': 30, 'publish_default_positions': True},
            ],
        ),
        # Pose-only mode: read the GUI's logical /joint_states and publish the
        # q-dependent grasp_frame/tool pose without publishing a second /joint_states.
        Node(
            package='macrobot_arm_kinematics',
            executable='linkage_state_node',
            name='macrobot_kinematic_pose_node',
            output='screen',
            parameters=[
                str(kinematics_config),
                {
                    'logical_state_topic': '/joint_states',
                    'publish_full_joint_states': False,
                },
            ],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', str(rviz_file)],
        ),
    ])
