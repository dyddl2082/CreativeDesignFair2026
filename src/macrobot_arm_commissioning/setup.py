import os
from glob import glob

from setuptools import find_packages, setup


package_name = "macrobot_arm_commissioning"


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
        (os.path.join("share", package_name, "docs"), glob("docs/*.md")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description="Interactive commissioning, test orchestration, and single-file reporting for MacRobot arm",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "commissioning_cli = macrobot_arm_commissioning.commissioning_cli:main",
            "primitive_executor_node = macrobot_arm_commissioning.primitive_executor_node:main",
            "commissioning_report_summary = macrobot_arm_commissioning.report_summary:main",
            "apply_report_recommendations = macrobot_arm_commissioning.apply_report:main",
        ],
    },
)
