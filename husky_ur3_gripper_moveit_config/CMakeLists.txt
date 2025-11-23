cmake_minimum_required(VERSION 3.8)
project(husky_ur3_gripper_moveit_config)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install directories
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

# Install Python scripts
install(PROGRAMS
  scripts/control_Husky_UR3.py
  scripts/control_Husky_UR3_2.py
  scripts/control_Husky_UR3_3.py
  scripts/control_Husky_UR3_4.py
  scripts/control_Husky_UR3_5.py
  scripts/control_Husky_UR3_6.py
  scripts/control_Husky_UR3_7.py
  scripts/control_Husky_UR3_8.py
  scripts/control_Husky_UR3_9.py
  scripts/control_Husky_UR3_10.py
  scripts/AR_marker_manip.py
  scripts/AR_marker_manip_2.py
  scripts/AR_marker_manip_3.py
  scripts/4_orient_grasping.py
  scripts/check_robot_current_pose.py
  scripts/control_simultaneously.py
  scripts/lidar.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
