from glob import glob
import os

from setuptools import find_packages, setup

package_name = "macrobot_ui"

setup(
    name=package_name,
    version="0.3.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml", "README.md", "LICENSE"]),
        (
            os.path.join("share", package_name, "launch"),
            glob("launch/*.launch.py"),
        ),
        (
            os.path.join("share", package_name, "config"),
            glob("config/*.yaml"),
        ),
        (
            os.path.join("share", package_name, "knowledge"),
            glob("knowledge/*"),
        ),
        (
            os.path.join("share", package_name),
            ["requirements-ui.txt", ".env.example"],
        ),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=False,
    maintainer="Kim Jinhyeong",
    maintainer_email="dyddl2082@snu.ac.kr",
    description=(
        "ROS 2 MacRobot UI with Korean-safe fonts and WSLg IBus input, a "
        "desktop frontend, and a Pi-local Action Gateway execution backend."
    ),
    license="MIT",
    entry_points={
        "console_scripts": [
            "macrobot_ui = macrobot_ui.runtime_bootstrap:main",
            "macrobot_ui_backend = macrobot_ui.backend_node:main",
            "macrobot_ui_font_check = macrobot_ui.runtime_bootstrap:font_check_main",
            "macrobot_ui_ime_check = macrobot_ui.runtime_bootstrap:ime_check_main",
        ],
    },
)
