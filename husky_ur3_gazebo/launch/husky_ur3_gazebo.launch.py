#!/usr/bin/env python3
"""
ROS2 Humble Launch file for Husky UR3 Gazebo simulation
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directories
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.0')

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
        default_value='0.0',
        description='Initial z position of the robot'
    )

    # Path to URDF file
    urdf_file = os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro')

    # Robot description
    robot_description = Command([
        'xacro ', urdf_file
    ])

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

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Gazebo server
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

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_husky_ur3',
        arguments=[
            '-entity', 'husky_ur3',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ],
        output='screen'
    )

    # Controller manager spawner for diff_drive_controller
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Controller manager spawner for joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Controller manager spawner for UR3 arm controller
    ur3_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['ur3_arm_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Controller manager spawner for gripper controller
    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,
        declare_x_pose,
        declare_y_pose,
        declare_z_pose,
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_robot,
        joint_state_broadcaster_spawner,
        diff_drive_spawner,
        ur3_arm_controller_spawner,
        gripper_controller_spawner,
    ])
