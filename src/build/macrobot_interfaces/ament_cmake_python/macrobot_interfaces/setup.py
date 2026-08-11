from setuptools import find_packages
from setuptools import setup

setup(
    name='macrobot_interfaces',
    version='0.3.0',
    packages=find_packages(
        include=('macrobot_interfaces', 'macrobot_interfaces.*')),
)
