from glob import glob
import os

from setuptools import find_packages, setup

package_name = "macrobot_perception"

setup(
    name=package_name,
    version="0.3.1",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml", "requirements.txt", "README.md"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="MacRobot Team",
    maintainer_email="dyddl2082@snu.ac.kr",
    description=(
        "Consolidated WSL2 perception package: candidate filtering, DINOv2 "
        "retrieval, and temporal confirmation."
    ),
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "candidate_filter_node = candidate_filter.candidate_filter_node:main",
            "embedding_retrieval_node = embedding_retrieval.runtime_bootstrap:main",
            "embedding_runtime_check = embedding_retrieval.runtime_bootstrap:check_main",
            "temporal_confirmation_node = temporal_confirmation.temporal_confirmation_node:main",
        ],
    },
)
