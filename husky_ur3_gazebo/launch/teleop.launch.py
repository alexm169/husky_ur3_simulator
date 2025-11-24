#!/usr/bin/env python3
"""
ROS2 Humble Launch file for teleop control of Husky UR3
Allows keyboard control of the mobile base
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    # Teleop twist keyboard node
    # This allows keyboard control of the mobile base via /cmd_vel
    teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',  # Opens in new terminal
        remappings=[
            ('cmd_vel', '/diff_drive_controller/cmd_vel_unstamped')
        ],
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    return LaunchDescription([
        declare_use_sim_time,
        teleop_node,
    ])
