/*******************************************************************************
* Copyright 2018 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

// ROS2 Humble Migration

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64.hpp>
#include <memory>

class GazeboGripperPublisher : public rclcpp::Node
{
public:
  GazeboGripperPublisher()
  : Node("gazebo_gripper_publisher")
  {
    // Create publishers
    rh_r2_joint_pub_ = this->create_publisher<std_msgs::msg::Float64>(
      "/rh_r2_position/command", 10);
    rh_l1_joint_pub_ = this->create_publisher<std_msgs::msg::Float64>(
      "/rh_l1_position/command", 10);
    rh_l2_joint_pub_ = this->create_publisher<std_msgs::msg::Float64>(
      "/rh_l2_position/command", 10);

    // Create subscriber
    rh_joint_sub_ = this->create_subscription<std_msgs::msg::Float64>(
      "/rh_p12_rn_position/command", 10,
      std::bind(&GazeboGripperPublisher::rh_joint_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "Gazebo Gripper Publisher node started");
  }

private:
  void rh_joint_callback(const std_msgs::msg::Float64::SharedPtr msg)
  {
    auto grip_joint_msg = std_msgs::msg::Float64();
    auto grip_joint_msg_2 = std_msgs::msg::Float64();

    grip_joint_msg.data = msg->data;
    if (grip_joint_msg.data > 1.05) {
      grip_joint_msg.data = 1.05;
    }
    grip_joint_msg_2.data = msg->data * (1.0 / 1.1);

    rh_r2_joint_pub_->publish(grip_joint_msg_2);
    rh_l1_joint_pub_->publish(grip_joint_msg);
    rh_l2_joint_pub_->publish(grip_joint_msg_2);
  }

  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr rh_r2_joint_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr rh_l1_joint_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr rh_l2_joint_pub_;
  rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr rh_joint_sub_;
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<GazeboGripperPublisher>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
