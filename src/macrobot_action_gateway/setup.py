import os
from glob import glob

from setuptools import find_packages, setup

package_name = "macrobot_action_gateway"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "LICENSE"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "examples"), glob("examples/*.py")),
        (os.path.join("share", package_name, "docs"), glob("docs/*.md")),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="Kim Jinhyeong",
    maintainer_email="dyddl2082@snu.ac.kr",
    description="Robot Action Gateway with resilient visual pick/place integration for MacRobot LLM API v0.2.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "action_gateway_node = macrobot_action_gateway.gateway_node:main",
            "robot_code_runner = macrobot_action_gateway.code_runner:main",
            "action_gateway_cli = macrobot_action_gateway.gateway_cli:main",
        ],
    },
)
