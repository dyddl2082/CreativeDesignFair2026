from glob import glob
from setuptools import find_packages, setup

package_name = "depth_candidate_proposal"

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
    description=(
        "Aligned-depth object proposal node for the MacRobot "
        "Raspberry Pi edge computer."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "aligned_depth_candidate_node = "
            "depth_candidate_proposal.aligned_depth_candidate_node:main",
        ],
    },
)
