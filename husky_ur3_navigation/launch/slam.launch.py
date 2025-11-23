#!/usr/bin/env python3
"""
ROS2 Humble Launch file for Husky UR3 SLAM using slam_toolbox
(Replaces gmapping from ROS1)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directories
    pkg_husky_ur3_navigation = get_package_share_directory('husky_ur3_navigation')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(pkg_husky_ur3_navigation, 'config', 'slam_toolbox_params.yaml'),
        description='Full path to the SLAM parameters file'
    )

    # SLAM Toolbox node (async mode for online SLAM)
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_file,
            {'use_sim_time': use_sim_time}
        ],
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params_file,
        slam_toolbox_node,
    ])
