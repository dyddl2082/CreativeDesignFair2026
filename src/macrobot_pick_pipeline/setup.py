import os
from glob import glob

from setuptools import find_packages, setup

package_name = "macrobot_pick_pipeline"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "rviz"), glob("rviz/*.rviz")),
        (os.path.join("share", package_name, "docs"), glob("docs/*.md")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description="Camera localization and validated arm pick state machine for MacRobot",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "detection_localizer_node = macrobot_pick_pipeline.detection_localizer_node:main",
            "pick_coordinator_node = macrobot_pick_pipeline.pick_coordinator_node:main",
            "mock_perception_node = macrobot_pick_pipeline.mock_perception_node:main",
        ],
    },
)
