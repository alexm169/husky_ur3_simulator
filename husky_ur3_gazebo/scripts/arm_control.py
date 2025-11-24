#!/usr/bin/env python3
"""
ROS2 Humble - UR3 Arm Control Node
Simple interface to control the UR3 arm with predefined poses

Usage:
  ros2 run husky_ur3_gazebo arm_control.py --home
  ros2 run husky_ur3_gazebo arm_control.py --ready
  ros2 run husky_ur3_gazebo arm_control.py --pose j1 j2 j3 j4 j5 j6
  ros2 run husky_ur3_gazebo arm_control.py  (interactive mode)
"""

import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class ArmController(Node):
    """Node to control the UR3 arm."""

    # Arm joint names
    ARM_JOINTS = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'elbow_joint',
        'wrist_1_joint',
        'wrist_2_joint',
        'wrist_3_joint'
    ]

    # Predefined poses (in radians)
    POSES = {
        'home': [0.0, -1.57, 0.0, -1.57, 0.0, 0.0],
        'ready': [0.0, -1.0, 1.0, -1.57, -1.57, 0.0],
        'up': [0.0, -1.57, -1.57, -1.57, 1.57, 0.0],
        'forward': [0.0, -0.5, 0.5, -1.57, -1.57, 0.0],
    }

    def __init__(self):
        super().__init__('arm_controller')

        # Action client for arm controller
        self.arm_action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/ur3_arm_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Waiting for UR3 arm controller action server...')
        if not self.arm_action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('UR3 arm controller action server not available!')
            return

        self.get_logger().info('Connected to UR3 arm controller')

    def send_arm_goal(self, positions, duration_sec=3.0):
        """Send an arm position goal.

        Args:
            positions: List of 6 joint positions in radians
            duration_sec: Time to reach goal position
        """
        goal_msg = FollowJointTrajectory.Goal()

        trajectory = JointTrajectory()
        trajectory.joint_names = self.ARM_JOINTS

        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * 6
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9)
        )

        trajectory.points.append(point)
        goal_msg.trajectory = trajectory

        positions_deg = [math.degrees(p) for p in positions]
        self.get_logger().info(f'Sending arm goal (degrees): {positions_deg}')

        future = self.arm_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

        return future

    def feedback_callback(self, feedback_msg):
        """Handle feedback from the action server."""
        pass

    def goal_response_callback(self, future):
        """Handle goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Arm goal was rejected')
            return

        self.get_logger().info('Arm goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        """Handle result from the action server."""
        result = future.result()
        self.get_logger().info('Arm motion completed')

    def go_to_pose(self, pose_name):
        """Move arm to a predefined pose.

        Args:
            pose_name: Name of the pose ('home', 'ready', 'up', 'forward')
        """
        if pose_name not in self.POSES:
            self.get_logger().error(f'Unknown pose: {pose_name}')
            self.get_logger().info(f'Available poses: {list(self.POSES.keys())}')
            return None

        self.get_logger().info(f'Moving to pose: {pose_name}')
        return self.send_arm_goal(self.POSES[pose_name])


def print_help():
    """Print usage instructions."""
    print("""
UR3 Arm Control for Husky UR3
=============================

Command line options:
  --home      Move arm to home position
  --ready     Move arm to ready position
  --up        Move arm to up position
  --forward   Move arm to forward position
  --pose j1 j2 j3 j4 j5 j6   Set specific joint angles (degrees)
  --help      Show this help message

Interactive mode (no arguments):
  Type pose name (home/ready/up/forward) or 6 space-separated angles (degrees)
  Type 'q' to quit

Predefined poses (in degrees):
  home:    [0, -90, 0, -90, 0, 0]
  ready:   [0, -57, 57, -90, -90, 0]
  up:      [0, -90, -90, -90, 90, 0]
  forward: [0, -29, 29, -90, -90, 0]
""")


def main(args=None):
    rclpy.init(args=args)

    node = ArmController()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if '--help' in sys.argv or '-h' in sys.argv:
            print_help()
            return
        elif '--home' in sys.argv:
            future = node.go_to_pose('home')
            if future:
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(4.0)
        elif '--ready' in sys.argv:
            future = node.go_to_pose('ready')
            if future:
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(4.0)
        elif '--up' in sys.argv:
            future = node.go_to_pose('up')
            if future:
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(4.0)
        elif '--forward' in sys.argv:
            future = node.go_to_pose('forward')
            if future:
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(4.0)
        elif '--pose' in sys.argv:
            try:
                idx = sys.argv.index('--pose')
                angles_deg = [float(sys.argv[idx + i + 1]) for i in range(6)]
                angles_rad = [math.radians(a) for a in angles_deg]
                future = node.send_arm_goal(angles_rad)
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(4.0)
            except (IndexError, ValueError):
                print('Error: --pose requires 6 joint angles in degrees')
                return
        else:
            print(f'Unknown argument: {sys.argv[1]}')
            print_help()
            return
    else:
        # Interactive mode
        print_help()
        print('Entering interactive mode...')

        import threading
        spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
        spin_thread.start()

        try:
            while True:
                cmd = input('\nArm command (home/ready/up/forward/angles/q): ').strip().lower()

                if cmd == 'q':
                    break
                elif cmd in node.POSES:
                    node.go_to_pose(cmd)
                else:
                    try:
                        parts = cmd.split()
                        if len(parts) == 6:
                            angles_deg = [float(p) for p in parts]
                            angles_rad = [math.radians(a) for a in angles_deg]
                            node.send_arm_goal(angles_rad)
                        else:
                            print('Invalid command. Use pose name or 6 space-separated angles')
                    except ValueError:
                        print('Invalid command. Use pose name or 6 space-separated angles')

                import time
                time.sleep(4.0)  # Wait for motion

        except KeyboardInterrupt:
            pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
