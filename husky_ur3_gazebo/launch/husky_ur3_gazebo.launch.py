#!/usr/bin/env python3
"""
ROS2 Humble Launch file for Husky UR3 Gazebo simulation
"""

import os
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directories
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Set GAZEBO_MODEL_PATH to find meshes
    gazebo_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    # Add the package share directory so Gazebo can resolve package:// URIs
    new_model_path = os.path.dirname(pkg_husky_ur3_gazebo) + ':' + gazebo_model_path
    os.environ['GAZEBO_MODEL_PATH'] = new_model_path

    # Also set GAZEBO_RESOURCE_PATH for mesh files
    gazebo_resource_path = os.environ.get('GAZEBO_RESOURCE_PATH', '')
    new_resource_path = pkg_husky_ur3_gazebo + ':' + gazebo_resource_path
    os.environ['GAZEBO_RESOURCE_PATH'] = new_resource_path

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_husky_ur3_gazebo, 'worlds', 'empty.world'),
        description='Full path to world model file to load'
    )

    declare_x_pose = DeclareLaunchArgument(
        'x_pose',
        default_value='0.0',
        description='Initial x position of the robot'
    )

    declare_y_pose = DeclareLaunchArgument(
        'y_pose',
        default_value='0.0',
        description='Initial y position of the robot'
    )

    declare_z_pose = DeclareLaunchArgument(
        'z_pose',
        default_value='0.1',
        description='Initial z position of the robot'
    )

    # Path to URDF file
    urdf_file = os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro')

    # Process xacro using subprocess (avoids stderr warning issues)
    xacro_result = subprocess.run(
        ['xacro', urdf_file],
        capture_output=True,
        text=True
    )
    robot_description = xacro_result.stdout

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description
        }]
    )

    # Gazebo server with world file
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    # Gazebo client
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # Spawn robot in Gazebo - with delay to ensure Gazebo is ready
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_husky_ur3',
        arguments=[
            '-entity', 'husky_ur3',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-timeout', '120'
        ],
        output='screen'
    )

    # Delay spawn to ensure Gazebo is ready
    delayed_spawn = TimerAction(
        period=5.0,
        actions=[spawn_robot]
    )

    # Controller spawners - delayed to ensure robot is spawned
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    ur3_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['ur3_arm_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Delay controllers to ensure robot is spawned and controller manager is ready
    delayed_controllers = TimerAction(
        period=10.0,
        actions=[
            joint_state_broadcaster_spawner,
            diff_drive_spawner,
            ur3_arm_controller_spawner,
            gripper_controller_spawner
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,
        declare_x_pose,
        declare_y_pose,
        declare_z_pose,
        robot_state_publisher,
        gazebo_server,
        gazebo_client,
        delayed_spawn,
        delayed_controllers,
    ])
