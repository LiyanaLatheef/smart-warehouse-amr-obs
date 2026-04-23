import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Launch RPLiDAR with the specific USB port
    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rplidar_ros'), 'launch', 'rplidar_a1_launch.py')
        ),
        launch_arguments={'serial_port': '/dev/ttyUSB0'}.items()
    )

    # 2. Launch your Avoidance Brain
    # (Using the ROS2 Node method based on your previous 'ros2 run' setup)
    avoid_node = Node(
        package='two_wheel_robot',
        executable='avoid_physical',
        output='screen'
    )

    return LaunchDescription([
        rplidar_launch,
        avoid_node
    ])