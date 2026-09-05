from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    realsense_share = Path(get_package_share_directory("realsense2_camera"))
    output_file = LaunchConfiguration("output_file")
    source_camera_name = LaunchConfiguration("source_camera_name")
    camera_namespace = LaunchConfiguration("camera_namespace")
    serial_no = LaunchConfiguration("serial_no")
    timeout_sec = LaunchConfiguration("timeout_sec")
    require_infra_frames = LaunchConfiguration("require_infra_frames")
    anchor_color_roll = LaunchConfiguration("anchor_color_roll")
    anchor_color_pitch = LaunchConfiguration("anchor_color_pitch")
    anchor_color_yaw = LaunchConfiguration("anchor_color_yaw")

    camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(realsense_share / "launch" / "rs_launch.py")),
        launch_arguments={
            "camera_name": source_camera_name,
            "camera_namespace": camera_namespace,
            "serial_no": serial_no,
            "publish_tf": "true",
            "tf_publish_rate": "0.0",
            "enable_color": "true",
            "enable_depth": "true",
            "enable_infra1": "true",
            "enable_infra2": "true",
            "pointcloud.enable": "false",
            "align_depth.enable": "true",
            "enable_sync": "true",
            "rgb_camera.color_profile": "640x480x15",
            "depth_module.depth_profile": "640x480x15",
            "depth_module.infra_profile": "640x480x15",
        }.items(),
    )

    capture = TimerAction(
        period=2.0,
        actions=[
            Node(
                package="macrobot_camera_tf",
                executable="capture_realsense_rgb_anchor",
                name="macrobot_capture_realsense_rgb_anchor",
                output="screen",
                parameters=[{
                    "output_file": output_file,
                    "source_camera_name": source_camera_name,
                    "target_camera_name": "camera",
                    "urdf_anchor_frame": "camera_link",
                    "timeout_sec": ParameterValue(timeout_sec, value_type=float),
                    "require_infra_frames": ParameterValue(
                        require_infra_frames, value_type=bool
                    ),
                    "anchor_color_roll": ParameterValue(
                        anchor_color_roll, value_type=float
                    ),
                    "anchor_color_pitch": ParameterValue(
                        anchor_color_pitch, value_type=float
                    ),
                    "anchor_color_yaw": ParameterValue(
                        anchor_color_yaw, value_type=float
                    ),
                }],
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "output_file",
            default_value=str(Path.home() / "MacRobot" / "data" / "camera_tf" / "d435_rgb_anchor.yaml"),
        ),
        DeclareLaunchArgument("source_camera_name", default_value="calib_camera"),
        DeclareLaunchArgument("camera_namespace", default_value="camera_calibration"),
        DeclareLaunchArgument("serial_no", default_value="''"),
        DeclareLaunchArgument("timeout_sec", default_value="25.0"),
        DeclareLaunchArgument("require_infra_frames", default_value="false"),
        DeclareLaunchArgument(
            "anchor_color_roll",
            default_value="0.0",
            description="roll from URDF camera_link to RealSense color_frame body axes",
        ),
        DeclareLaunchArgument(
            "anchor_color_pitch",
            default_value="0.0",
            description="pitch from URDF camera_link to RealSense color_frame body axes",
        ),
        DeclareLaunchArgument(
            "anchor_color_yaw",
            default_value="0.0",
            description="yaw from URDF camera_link to RealSense color_frame body axes",
        ),
        camera,
        capture,
    ])
