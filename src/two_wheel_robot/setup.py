from setuptools import setup
import os
from glob import glob

package_name = 'two_wheel_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # This includes all launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # This includes all URDF/Xacro files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # This includes your warehouse world files
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        # This includes navigation and slam parameters
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        # This includes your saved maps
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='LiyanaLatheef',
    maintainer_email='liyanalatheef17@gmail.com',
    description='Smart Warehouse AMR Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # If you want to run avoid_physical.py using 'ros2 run'
            'avoid_physical = two_wheel_robot.avoid_physical:main',
        ],
    },
)
