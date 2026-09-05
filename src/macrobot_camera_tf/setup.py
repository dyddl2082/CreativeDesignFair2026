import os
from glob import glob
from setuptools import find_packages, setup

package_name = "macrobot_camera_tf"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "README_KO.md"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description=(
        "Capture RealSense factory TFs and republish them from a CAD camera_link "
        "located at the RGB optical center."
    ),
    license="MIT",
    entry_points={
        "console_scripts": [
            "capture_realsense_rgb_anchor = macrobot_camera_tf.capture_realsense_rgb_anchor:main",
            "rgb_anchor_tf_publisher = macrobot_camera_tf.rgb_anchor_tf_publisher:main",
        ],
    },
)
