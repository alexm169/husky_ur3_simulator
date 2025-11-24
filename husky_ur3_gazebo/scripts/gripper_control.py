#!/usr/bin/env python3
"""
ROS2 Humble - Gripper Control Node
Simple interface to open/close the RH-P12-RN gripper

Usage:
  ros2 run husky_ur3_gazebo gripper_control.py --open
  ros2 run husky_ur3_gazebo gripper_control.py --close
  ros2 run husky_ur3_gazebo gripper_control.py --position 0.5
  ros2 run husky_ur3_gazebo gripper_control.py  (interactive mode)
"""

import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class GripperController(Node):
    """Node to control the RH-P12-RN gripper."""

    # Gripper joint names
    GRIPPER_JOINTS = ['rh_p12_rn', 'rh_r2', 'rh_l1', 'rh_l2']

    # Position limits
    GRIPPER_OPEN = [0.0, 0.0, 0.0, 0.0]
    GRIPPER_CLOSED = [1.0, 0.8, 1.0, 0.8]

    def __init__(self):
        super().__init__('gripper_controller')

        # Action client for gripper controller
        self.gripper_action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/gripper_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Waiting for gripper controller action server...')
        if not self.gripper_action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Gripper controller action server not available!')
            return

        self.get_logger().info('Connected to gripper controller')

    def send_gripper_goal(self, positions, duration_sec=1.0):
        """Send a gripper position goal.

        Args:
            positions: List of 4 joint positions [rh_p12_rn, rh_r2, rh_l1, rh_l2]
            duration_sec: Time to reach goal position
        """
        goal_msg = FollowJointTrajectory.Goal()

        trajectory = JointTrajectory()
        trajectory.joint_names = self.GRIPPER_JOINTS

        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * 4
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9)
        )

        trajectory.points.append(point)
        goal_msg.trajectory = trajectory

        self.get_logger().info(f'Sending gripper goal: {positions}')

        future = self.gripper_action_client.send_goal_async(
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
            self.get_logger().error('Gripper goal was rejected')
            return

        self.get_logger().info('Gripper goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        """Handle result from the action server."""
        result = future.result()
        self.get_logger().info('Gripper motion completed')

    def open_gripper(self):
        """Open the gripper fully."""
        self.get_logger().info('Opening gripper...')
        return self.send_gripper_goal(self.GRIPPER_OPEN)

    def close_gripper(self):
        """Close the gripper fully."""
        self.get_logger().info('Closing gripper...')
        return self.send_gripper_goal(self.GRIPPER_CLOSED)

    def set_gripper_position(self, position):
        """Set gripper to a specific position (0.0 = open, 1.0 = closed).

        Args:
            position: Value between 0.0 (open) and 1.0 (closed)
        """
        position = max(0.0, min(1.0, position))  # Clamp to valid range

        # Interpolate between open and closed positions
        positions = [
            self.GRIPPER_OPEN[i] + position * (self.GRIPPER_CLOSED[i] - self.GRIPPER_OPEN[i])
            for i in range(4)
        ]

        self.get_logger().info(f'Setting gripper to position {position}')
        return self.send_gripper_goal(positions)


def print_help():
    """Print usage instructions."""
    print("""
Gripper Control for Husky UR3
============================

Command line options:
  --open       Open the gripper fully
  --close      Close the gripper fully
  --position N Set gripper position (0.0=open, 1.0=closed)
  --help       Show this help message

Interactive mode (no arguments):
  Type 'o' to open, 'c' to close, or a number (0.0-1.0) for position
  Type 'q' to quit
""")


def main(args=None):
    rclpy.init(args=args)

    node = GripperController()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if '--help' in sys.argv or '-h' in sys.argv:
            print_help()
            return
        elif '--open' in sys.argv:
            future = node.open_gripper()
            rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
            # Wait for result
            import time
            time.sleep(2.0)
        elif '--close' in sys.argv:
            future = node.close_gripper()
            rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
            import time
            time.sleep(2.0)
        elif '--position' in sys.argv:
            try:
                idx = sys.argv.index('--position')
                position = float(sys.argv[idx + 1])
                future = node.set_gripper_position(position)
                rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
                import time
                time.sleep(2.0)
            except (IndexError, ValueError):
                print('Error: --position requires a number between 0.0 and 1.0')
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
                cmd = input('\nGripper command (o/c/0.0-1.0/q): ').strip().lower()

                if cmd == 'q':
                    break
                elif cmd == 'o':
                    node.open_gripper()
                elif cmd == 'c':
                    node.close_gripper()
                else:
                    try:
                        position = float(cmd)
                        node.set_gripper_position(position)
                    except ValueError:
                        print('Invalid command. Use o/c/number/q')

                import time
                time.sleep(1.5)  # Wait for motion

        except KeyboardInterrupt:
            pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
