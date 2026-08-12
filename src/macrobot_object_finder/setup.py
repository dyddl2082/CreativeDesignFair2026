from glob import glob
import os

from setuptools import find_packages, setup

package_name = "macrobot_object_finder"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml", "README.md"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "docs"), glob("docs/*.md")),
        (os.path.join("share", package_name, "scripts"), glob("scripts/*.sh")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description=(
        "Command/session layer for the MacRobot D435 candidate, DINOv2, and "
        "temporal-confirmation object-finding pipeline."
    ),
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "object_finder_node = macrobot_object_finder.object_finder_node:main",
            "object_finder_cli = macrobot_object_finder.object_finder_cli:main",
            "threshold_calibrator_node = macrobot_object_finder.threshold_calibrator_node:main",
            "threshold_calibration_cli = macrobot_object_finder.threshold_calibration_cli:main",
        ],
    },
)
