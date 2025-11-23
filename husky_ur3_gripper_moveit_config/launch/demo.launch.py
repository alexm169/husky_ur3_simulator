#!/usr/bin/env python3
"""
ROS2 Humble MoveIt2 Demo Launch file for Husky UR3 Gripper
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    # Get package directories
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')
    pkg_moveit_config = get_package_share_directory('husky_ur3_gripper_moveit_config')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    # Path to URDF file
    urdf_file = os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro')

    # Robot description
    robot_description = Command(['xacro ', urdf_file])

    # SRDF file
    srdf_file = os.path.join(pkg_moveit_config, 'config', 'husky_ur3_gripper.srdf')
    with open(srdf_file, 'r') as f:
        robot_description_semantic = f.read()

    # Kinematics config
    kinematics_yaml = os.path.join(pkg_moveit_config, 'config', 'kinematics.yaml')

    # Joint limits config
    joint_limits_yaml = os.path.join(pkg_moveit_config, 'config', 'joint_limits.yaml')

    # Controllers config
    controllers_yaml = os.path.join(pkg_moveit_config, 'config', 'ros2_controllers.yaml')

    # OMPL planning config
    ompl_planning_yaml = os.path.join(pkg_moveit_config, 'config', 'ompl_planning.yaml')

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

    # MoveIt move_group node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description,
                'robot_description_semantic': robot_description_semantic,
                'use_sim_time': use_sim_time,
                'publish_robot_description_semantic': True,
            },
            kinematics_yaml,
            joint_limits_yaml,
            ompl_planning_yaml,
        ],
    )

    # RViz2 with MoveIt plugin
    rviz_config_file = os.path.join(pkg_moveit_config, 'launch', 'moveit.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[
            {
                'robot_description': robot_description,
                'robot_description_semantic': robot_description_semantic,
                'use_sim_time': use_sim_time,
            },
            kinematics_yaml,
        ],
    )

    # Joint State Publisher GUI
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        declare_use_sim_time,
        robot_state_publisher,
        joint_state_publisher_gui,
        move_group_node,
        rviz_node,
    ])
