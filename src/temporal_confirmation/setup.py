from glob import glob
from setuptools import find_packages, setup

package_name = "temporal_confirmation"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="MacRobot",
    maintainer_email="macrobot@example.com",
    description="Spatial tracking and multi-frame confirmation for MacRobot retrieval results.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "temporal_confirmation_node = temporal_confirmation.temporal_confirmation_node:main",
        ],
    },
)
