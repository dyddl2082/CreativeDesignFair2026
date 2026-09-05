from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_share = Path(get_package_share_directory("macrobot_description"))
    xacro_file = package_share / "urdf" / "macrobot_full_visual.urdf.xacro"

    use_sim_time = LaunchConfiguration("use_sim_time")
    rsp_node_name = LaunchConfiguration("rsp_node_name")

    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", str(xacro_file)]),
        value_type=str,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
            ),
            DeclareLaunchArgument(
                "rsp_node_name",
                default_value="macrobot_pi_robot_state_publisher",
                description=(
                    "Unique name of the Raspberry Pi robot_state_publisher "
                    "that owns the MacRobot URDF TF tree"
                ),
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name=rsp_node_name,
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "use_sim_time": ParameterValue(
                            use_sim_time,
                            value_type=bool,
                        ),
                        "frame_prefix": "",
                    }
                ],
            ),
        ]
    )
