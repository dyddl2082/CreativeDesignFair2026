import os
from glob import glob

from setuptools import find_packages, setup

package_name = "macrobot_pick_pipeline"

setup(
    name=package_name,
    version="0.3.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml", "README.md"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "rviz"), glob("rviz/*.rviz")),
        (os.path.join("share", package_name, "docs"), glob("docs/*.md")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description="Camera localization, validated picking, camera-gated teaching and camera-independent arm demonstration recording for MacRobot",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "detection_localizer_node = macrobot_pick_pipeline.detection_localizer_node:main",
            "pick_coordinator_node = macrobot_pick_pipeline.pick_coordinator_node:main",
            "mock_perception_node = macrobot_pick_pipeline.mock_perception_node:main",
            "pick_teach_node = macrobot_pick_pipeline.pick_teach_node:main",
            "camera_teach_node = macrobot_pick_pipeline.camera_teach_node:main",
            "pick_teach_cli = macrobot_pick_pipeline.pick_teach_cli:main",
            "arm_demo_recorder_node = macrobot_pick_pipeline.arm_demo_recorder_node:main",
            "arm_demo_cli = macrobot_pick_pipeline.arm_demo_cli:main",
        ],
    },
)
