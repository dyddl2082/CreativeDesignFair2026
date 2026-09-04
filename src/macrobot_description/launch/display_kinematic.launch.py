from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = Path(get_package_share_directory("macrobot_description"))
    xacro_file = pkg / "urdf" / "macrobot_arm_kinematic.urdf.xacro"
    use_sim_time = LaunchConfiguration("use_sim_time")
    description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", str(xacro_file)]),
        value_type=str,
    )
    nodes = [
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="world_to_base_link",
            arguments=["--x", "0", "--y", "0", "--z", "0", "--roll", "0", "--pitch", "0", "--yaw", "0",
                       "--frame-id", "world", "--child-frame-id", "base_link"],
            output="screen",
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": description}, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", str(pkg / "rviz" / "display.rviz")],
            output="screen",
        ),
    ]
    return LaunchDescription(nodes)
