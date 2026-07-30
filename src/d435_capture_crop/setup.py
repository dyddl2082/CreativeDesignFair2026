from glob import glob
from setuptools import find_packages, setup

package_name = "d435_capture_crop"

setup(
    name=package_name,
    version="2.0.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml", "README.md", "README_KO.md"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
        (f"share/{package_name}/web", glob("web/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="MacRobot",
    maintainer_email="macrobot@example.com",
    description=(
        "Capture Intel RealSense D435 color/depth frames, crop them in a "
        "browser before saving, maintain reusable negative libraries, and write MacRobot dataset metadata."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "d435_capture_crop_node = "
            "d435_capture_crop.d435_capture_crop_node:main",
        ],
    },
)
