from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    realsense_share = Path(get_package_share_directory("realsense2_camera"))
    calibration_file = LaunchConfiguration("calibration_file")
    start_realsense = LaunchConfiguration("start_realsense")
    serial_no = LaunchConfiguration("serial_no")
    initial_reset = LaunchConfiguration("initial_reset")
    color_profile = LaunchConfiguration("color_profile")
    depth_profile = LaunchConfiguration("depth_profile")

    camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(realsense_share / "launch" / "rs_launch.py")),
        condition=IfCondition(start_realsense),
        launch_arguments={
            "camera_name": "camera",
            "camera_namespace": "camera",
            "serial_no": serial_no,
            "initial_reset": initial_reset,
            "publish_tf": "false",
            "tf_publish_rate": "0.0",
            "enable_color": "true",
            "enable_depth": "true",
            "enable_infra1": "false",
            "enable_infra2": "false",
            "pointcloud.enable": "false",
            "align_depth.enable": "true",
            "enable_sync": "true",
            "rgb_camera.color_profile": color_profile,
            "depth_module.depth_profile": depth_profile,
            "rgb_camera.color_format": "RGB8",
            "depth_module.depth_format": "Z16",
            "diagnostics_period": "1.0",
        }.items(),
    )

    tf_publisher = Node(
        package="macrobot_camera_tf",
        executable="rgb_anchor_tf_publisher",
        name="macrobot_rgb_anchor_tf_publisher",
        output="screen",
        parameters=[{"calibration_file": calibration_file}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "calibration_file",
            default_value=str(Path.home() / "MacRobot" / "data" / "camera_tf" / "d435_rgb_anchor.yaml"),
        ),
        DeclareLaunchArgument("start_realsense", default_value="true"),
        DeclareLaunchArgument("serial_no", default_value="''"),
        DeclareLaunchArgument("initial_reset", default_value="false"),
        DeclareLaunchArgument("color_profile", default_value="640x480x15"),
        DeclareLaunchArgument("depth_profile", default_value="640x480x15"),
        camera,
        tf_publisher,
    ])
