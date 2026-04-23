import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # --- Paths to your package and files ---
    pkg_two_wheel_robot = FindPackageShare('two_wheel_robot')
    
    world_file = PathJoinSubstitution([pkg_two_wheel_robot, 'worlds', 'warehouse.world'])
    urdf_file = PathJoinSubstitution([pkg_two_wheel_robot, 'urdf', 'two_wheel_robot.urdf'])
    map_file = PathJoinSubstitution([pkg_two_wheel_robot, 'maps', 'my_warehouse_map.yaml'])
    rviz_config_file = PathJoinSubstitution([pkg_two_wheel_robot, 'config', 'view_bot.rviz'])

    # ========================================================================
    # PHASE 0: CLEANUP ZOMBIE PROCESSES
    # ========================================================================
    # We use 'sh -c' and '|| true' so the launch file doesn't crash if Gazebo is already closed.
    cleanup_gazebo = ExecuteProcess(
        cmd=['sh', '-c', 'killall -9 gzserver gzclient || true'],
        output='screen'
    )

    # ========================================================================
    # PHASE 1: SIMULATION & ROBOT HARDWARE LOGIC
    # ========================================================================

    start_gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_file],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': Command(['xacro ', urdf_file])
        }]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', urdf_file, '-entity', 'robot1', '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen'
    )

    # ========================================================================
    # PHASE 2: MAP & TRANSFORMATION LOGIC
    # ========================================================================

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_file, 'use_sim_time': True}]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_mapper',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server']
        }]
    )

    static_transform = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )

    # ========================================================================
    # PHASE 3: AUTONOMOUS BRAIN
    # ========================================================================

    avoid_node = Node(
        package='obstacle_avoidance',
        executable='avoid',
        name='avoid_node',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    vel_smoother_node = Node(
        package='obstacle_avoidance',
        executable='vel_smoother',
        name='vel_smoother_node',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # ========================================================================
    # PHASE 4: VISUALS
    # ========================================================================

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # ========================================================================
    # SEQUENTIAL LAUNCH ASSEMBLY
    # ========================================================================
    
    return LaunchDescription([
        # 1. Fire the kill command immediately
        cleanup_gazebo,
        
        # 2. Wait 1 second for processes to die, then launch Gazebo and the Robot
        TimerAction(
            period=1.0,
            actions=[
                start_gazebo,
                robot_state_publisher,
                joint_state_publisher,
                spawn_entity,
                map_server,
                lifecycle_manager,
                static_transform
            ]
        ),

        # 3. Wait another 3 seconds for Gazebo to stabilize, then launch the Brain and RViz
        TimerAction(
            period=4.0,
            actions=[
                avoid_node,
                vel_smoother_node,
                rviz_node
            ]
        )
    ])
