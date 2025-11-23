#!/usr/bin/env python3
"""
ROS2 Humble Launch file for Husky UR3 Navigation using Nav2
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    # Get package directories
    pkg_husky_ur3_navigation = get_package_share_directory('husky_ur3_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    map_yaml_file = LaunchConfiguration('map')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_husky_ur3_navigation, 'config', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use'
    )

    declare_map_file = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_husky_ur3_navigation, 'map', 'HRI_lab.yaml'),
        description='Full path to map yaml file to load'
    )

    # Create rewritten YAML for parameter substitution
    param_substitutions = {
        'use_sim_time': use_sim_time,
        'yaml_filename': map_yaml_file
    }

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites=param_substitutions,
        convert_types=True
    )

    # Include Nav2 bringup launch
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'params_file': configured_params,
            'map': map_yaml_file
        }.items()
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_autostart,
        declare_params_file,
        declare_map_file,
        nav2_bringup,
    ])
