#!/usr/bin/env python3
"""
ROS2 Humble Launch file for displaying Husky UR3 in RViz
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directory
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    use_gui = LaunchConfiguration('use_gui', default='true')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    declare_use_gui = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Use joint state publisher GUI'
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

    # Joint State Publisher GUI
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=LaunchConfiguration('use_gui')
    )

    # Joint State Publisher (non-GUI)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RViz2
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(pkg_husky_ur3_gazebo, 'config', 'display.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_use_gui,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz2,
    ])
