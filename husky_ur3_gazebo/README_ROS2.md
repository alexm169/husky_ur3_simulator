# Husky UR3 Simulator - ROS2 Humble

This package provides a Gazebo simulation of a Husky mobile robot with UR3 manipulator arm and RH-P12-RN gripper for ROS2 Humble.

## System Configuration
- **Mobile Base**: Clearpath Husky (differential drive, 4 wheels)
- **Manipulator**: Universal Robots UR3 (6-DOF arm)
- **Gripper**: Robotis RH-P12-RN (1-DOF parallel gripper)
- **Total DOF**: 13 (6 base SE(3) + 6 arm + 1 gripper)

## Prerequisites

Install ROS2 Humble and required packages:

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-controller-manager ros-humble-joint-state-broadcaster \
  ros-humble-diff-drive-controller ros-humble-joint-trajectory-controller \
  ros-humble-robot-state-publisher ros-humble-xacro \
  ros-humble-teleop-twist-keyboard ros-humble-control-msgs
```

## Building the Package

```bash
# Create workspace (if not existing)
mkdir -p ~/husky_ws/src
cd ~/husky_ws/src

# Clone or copy the package
# cp -r /path/to/husky_ur3_simulator .

# Build
cd ~/husky_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launching the Simulation

### 1. Start Gazebo with Robot

```bash
# Terminal 1: Launch Gazebo simulation
ros2 launch husky_ur3_gazebo husky_ur3_gazebo.launch.py
```

Wait for Gazebo to fully load and the robot to spawn (approximately 10-15 seconds).

### 2. Teleop Control (Mobile Base)

```bash
# Terminal 2: Launch teleop for base control
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

Or use the launch file:
```bash
ros2 launch husky_ur3_gazebo teleop.launch.py
```

**Teleop Controls:**
- `i` - Forward
- `k` - Stop
- `j` - Turn left
- `l` - Turn right
- `,` - Backward
- `u`/`o` - Forward turn left/right
- `m`/`.` - Backward turn left/right

### 3. Gripper Control

```bash
# Terminal 3: Control gripper
ros2 run husky_ur3_gazebo gripper_control.py --open   # Open gripper
ros2 run husky_ur3_gazebo gripper_control.py --close  # Close gripper
ros2 run husky_ur3_gazebo gripper_control.py --position 0.5  # Half closed

# Or interactive mode:
ros2 run husky_ur3_gazebo gripper_control.py
```

### 4. Arm Control

```bash
# Terminal 4: Control UR3 arm
ros2 run husky_ur3_gazebo arm_control.py --home      # Home position
ros2 run husky_ur3_gazebo arm_control.py --ready     # Ready position
ros2 run husky_ur3_gazebo arm_control.py --up        # Up position
ros2 run husky_ur3_gazebo arm_control.py --forward   # Forward position

# Or custom pose (in degrees):
ros2 run husky_ur3_gazebo arm_control.py --pose 0 -90 90 -90 -90 0

# Or interactive mode:
ros2 run husky_ur3_gazebo arm_control.py
```

## Recording Rosbag Data (30 seconds)

### Record All Topics

```bash
# Terminal: Record all topics for 30 seconds
ros2 bag record -a -o husky_ur3_recording --max-cache-size 0 --duration 30
```

### Record Specific Topics

```bash
# Record only essential topics
ros2 bag record -o husky_ur3_recording --duration 30 \
  /joint_states \
  /diff_drive_controller/cmd_vel_unstamped \
  /diff_drive_controller/odom \
  /ur3_arm_controller/joint_trajectory \
  /gripper_controller/joint_trajectory \
  /tf \
  /tf_static \
  /clock
```

### Playback Recorded Data

```bash
ros2 bag play husky_ur3_recording
```

### View Bag Info

```bash
ros2 bag info husky_ur3_recording
```

## Screen Recording

For the assignment requirement, use a screen recorder like:

```bash
# Install OBS Studio or SimpleScreenRecorder
sudo apt install simplescreenrecorder

# Or use ffmpeg directly
ffmpeg -video_size 1920x1080 -framerate 30 -f x11grab -i :0.0 -t 30 output.mp4
```

## Complete Demo Sequence (for Assignment)

Run this sequence for the 30-second screen recording:

```bash
# Terminal 1: Start simulation
ros2 launch husky_ur3_gazebo husky_ur3_gazebo.launch.py

# Terminal 2: Start rosbag recording (when ready)
ros2 bag record -a -o husky_ur3_demo --duration 30

# Terminal 3: During first 10 seconds - teleop mobile base
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
# Drive the robot around using i,j,k,l keys

# Terminal 4: After 10 seconds - actuate gripper and arm
ros2 run husky_ur3_gazebo gripper_control.py --close
# Wait 5 seconds
ros2 run husky_ur3_gazebo gripper_control.py --open
# Wait 5 seconds
ros2 run husky_ur3_gazebo arm_control.py --ready
# Wait 5 seconds
ros2 run husky_ur3_gazebo arm_control.py --home
```

## Available Topics

```bash
# List all topics
ros2 topic list

# Key topics:
/joint_states                              # All joint states
/diff_drive_controller/cmd_vel_unstamped   # Base velocity commands
/diff_drive_controller/odom                # Odometry
/ur3_arm_controller/joint_trajectory       # Arm trajectory commands
/gripper_controller/joint_trajectory       # Gripper commands
/tf                                        # Transform tree
/clock                                     # Simulation time
```

## Troubleshooting

### Robot not spawning
- Wait longer for Gazebo to fully load
- Check for errors in terminal
- Ensure world file has ROS2 factory plugin

### Controllers not starting
- Wait for controller manager to initialize (10+ seconds)
- Check: `ros2 control list_controllers`

### Teleop not working
- Ensure correct topic remapping
- Check: `ros2 topic echo /diff_drive_controller/cmd_vel_unstamped`
