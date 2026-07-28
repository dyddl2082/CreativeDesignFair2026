from glob import glob
from setuptools import find_packages, setup

package_name = "candidate_filter"

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
    description="PC-side quality, depth, color, and shape filtering for MacRobot crops.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "candidate_filter_node = candidate_filter.candidate_filter_node:main",
        ],
    },
)
