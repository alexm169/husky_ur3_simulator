#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS2 Humble - Check Robot Current Pose
Migrated from ROS1 Noetic

This script demonstrates how to:
- Get the current robot arm pose using MoveIt2
- Subscribe to AMCL pose for navigation
- Use Nav2 action server for navigation goals
"""

import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup

import math
from math import pi, radians, degrees

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Quaternion
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from nav2_msgs.action import NavigateToPose

# For quaternion conversions
from tf_transformations import euler_from_quaternion, quaternion_from_euler

# MoveIt2 imports
try:
    from moveit.planning import MoveItPy
    from moveit.core.robot_state import RobotState
    MOVEIT_AVAILABLE = True
except ImportError:
    MOVEIT_AVAILABLE = False
    print("MoveIt2 Python bindings not available. Install moveit2 for full functionality.")


GROUP_NAME_ARM = "ur3_manipulator"
FIXED_FRAME = 'world'


class CheckRobotPose(Node):
    """Node to check current robot pose and demonstrate navigation."""

    def __init__(self):
        super().__init__('check_robot_pose')

        self.callback_group = ReentrantCallbackGroup()

        # Initialize MoveIt2 if available
        if MOVEIT_AVAILABLE:
            try:
                self.moveit = MoveItPy(node_name="moveit_py")
                self.arm = self.moveit.get_planning_component(GROUP_NAME_ARM)
                self.get_logger().info("MoveIt2 initialized successfully")
            except Exception as e:
                self.get_logger().warn(f"Could not initialize MoveIt2: {e}")
                self.moveit = None
                self.arm = None
        else:
            self.moveit = None
            self.arm = None

        # Subscriber for AMCL pose (Nav2)
        self.amcl_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_pose_callback,
            10,
            callback_group=self.callback_group
        )

        # Action client for Nav2 navigation
        self.nav_action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose',
            callback_group=self.callback_group
        )

        self.get_logger().info("Waiting for Nav2 action server...")
        if self.nav_action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().info("Connected to Nav2 action server")
        else:
            self.get_logger().warn("Nav2 action server not available")

        # Print current arm pose if MoveIt2 is available
        if self.arm is not None:
            self.get_arm_pose()

    def get_arm_pose(self):
        """Get and print current arm pose using MoveIt2."""
        if self.arm is None:
            self.get_logger().warn("MoveIt2 not available, cannot get arm pose")
            return

        try:
            robot_state = self.arm.get_start_state()
            joint_positions = robot_state.get_joint_group_positions(GROUP_NAME_ARM)

            self.get_logger().info("===== Current Robot Arm State =====")
            self.get_logger().info(f"Joint positions: {list(joint_positions)}")

            # Get end effector pose
            ee_pose = robot_state.get_global_link_transform("ee_link")
            self.get_logger().info(f"End effector pose:\n{ee_pose}")

        except Exception as e:
            self.get_logger().error(f"Error getting arm pose: {e}")

    def amcl_pose_callback(self, msg):
        """Callback for AMCL pose topic."""
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Convert quaternion to euler angles
        orientation = msg.pose.pose.orientation
        roll, pitch, yaw = euler_from_quaternion([
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w
        ])

        self.get_logger().info(
            f"Current robot pose: x={x:.3f}, y={y:.3f}, yaw={degrees(yaw):.2f}°"
        )

    def create_nav_goal(self, x, y, yaw_degrees):
        """Create a NavigateToPose goal message.

        Args:
            x: Target x position
            y: Target y position
            yaw_degrees: Target yaw orientation in degrees

        Returns:
            NavigateToPose.Goal message
        """
        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0

        # Convert yaw angle to quaternion
        angle = radians(yaw_degrees)
        quat = quaternion_from_euler(0.0, 0.0, angle)
        goal_msg.pose.pose.orientation = Quaternion(
            x=quat[0], y=quat[1], z=quat[2], w=quat[3]
        )

        return goal_msg

    def send_nav_goal(self, x, y, yaw_degrees):
        """Send a navigation goal to Nav2.

        Args:
            x: Target x position
            y: Target y position
            yaw_degrees: Target yaw orientation in degrees
        """
        goal_msg = self.create_nav_goal(x, y, yaw_degrees)

        self.get_logger().info(f"Sending navigation goal: x={x}, y={y}, yaw={yaw_degrees}°")

        send_goal_future = self.nav_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.nav_feedback_callback
        )
        send_goal_future.add_done_callback(self.nav_goal_response_callback)

    def nav_goal_response_callback(self, future):
        """Callback for navigation goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Navigation goal was rejected")
            return

        self.get_logger().info("Navigation goal accepted")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.nav_result_callback)

    def nav_result_callback(self, future):
        """Callback for navigation result."""
        result = future.result().result
        self.get_logger().info("Navigation completed")

    def nav_feedback_callback(self, feedback_msg):
        """Callback for navigation feedback."""
        feedback = feedback_msg.feedback
        # Log progress periodically
        pass


def main(args=None):
    rclpy.init(args=args)

    try:
        node = CheckRobotPose()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
