from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'macrobot_arm_kinematics'

setup(
    name=package_name,
    version='0.3.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Kim Jinhyeong',
    maintainer_email='dyddl2082@snu.ac.kr',
    description='Reduced FK/IK and full-linkage visualization mapping for MacRobot.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'linkage_state_node = macrobot_arm_kinematics.linkage_state_node:main',
            'ik_node = macrobot_arm_kinematics.ik_node:main',
        ],
    },
)
