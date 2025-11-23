#!/usr/bin/env python3
"""
ROS2 Humble - Husky UR3 Joint Control Node
Migrated from ROS1 Noetic
"""

import rclpy
from rclpy.node import Node
import math
import time

from std_msgs.msg import Float64
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Twist
from builtin_interfaces.msg import Duration


class HuskyUR3JointControl(Node):
    def __init__(self):
        super().__init__('husky_ur3_joint_control')

        # Wait for clock to be ready
        self.get_logger().info(f'Current time: {self.get_clock().now().nanoseconds / 1e9}')
        while self.get_clock().now().nanoseconds == 0:
            time.sleep(0.1)
            self.get_logger().info(f'Waiting for clock... {self.get_clock().now().nanoseconds / 1e9}')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.arm_controller_pub = self.create_publisher(
            JointTrajectory,
            '/ur3_arm_controller/joint_trajectory',
            10
        )

        # Create and publish trajectory
        self.publish_trajectory()

    def publish_trajectory(self):
        ur3_ctrl = JointTrajectory()
        ur3_ctrl.header.frame_id = 'base_link'
        ur3_ctrl.header.stamp = self.get_clock().now().to_msg()

        # Joint names (without namespace prefix for ROS2)
        ur3_ctrl.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        n = 1500
        dt = 0.01
        rps = 0.05

        for i in range(n):
            p = JointTrajectoryPoint()
            theta = rps * 2.0 * math.pi * i * dt
            x1 = -0.5 * math.sin(2 * theta)
            x2 = 0.5 * math.sin(1 * theta)

            p.positions = [x1, x2, x2, x2, x2, x2]
            p.velocities = []
            p.accelerations = []

            # Set duration
            duration_sec = int(dt * (i + 1))
            duration_nanosec = int((dt * (i + 1) - duration_sec) * 1e9)
            p.time_from_start = Duration(sec=duration_sec, nanosec=duration_nanosec)

            ur3_ctrl.points.append(p)

            if i % 100 == 0:
                self.get_logger().info(f'Point {i}: angles [{x1:.4f}, {x2:.4f}]')

        # Publish the trajectory
        self.arm_controller_pub.publish(ur3_ctrl)
        self.get_logger().info('Published joint trajectory')


def main(args=None):
    rclpy.init(args=args)

    try:
        node = HuskyUR3JointControl()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
