cmake_minimum_required(VERSION 3.8)
project(husky_ur3_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Build the gripper publisher node
add_executable(gazebo_rh_pub src/gazebo_rh_pub.cpp)
ament_target_dependencies(gazebo_rh_pub
  rclcpp
  std_msgs
)

# Install targets
install(TARGETS
  gazebo_rh_pub
  DESTINATION lib/${PROJECT_NAME}
)

# Install directories
install(DIRECTORY
  launch
  config
  urdf
  meshes
  worlds
  DESTINATION share/${PROJECT_NAME}
)

# Install Python scripts
install(PROGRAMS
  src/husky_ur3_control_joint.py
  src/ur3_control_joint.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
