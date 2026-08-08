#!/usr/bin/env bash
set -euo pipefail

TOPIC="/pico_debug/cmd"

send_command() {
  local command="$1"
  local wait_sec="${2:-1.0}"
  echo
  echo "TX: ${command}"
  ros2 topic pub --once "$TOPIC" std_msgs/msg/String "{data: '${command}'}"
  sleep "$wait_sec"
}

echo "MacRobot Pico arm visible smoke test, 500-2500us mapping"
echo "This test uses larger visible movements: q1/q2/q3 delta ~= 0.15 rad."
echo "Run only with the arm supported. For first test, keep servo gears/horns detached."
read -r -p "Type YES to continue: " answer
[[ "$answer" == "YES" ]] || exit 1

send_command "PING" 0.5
send_command "STATUS?" 0.5
send_command "SERVO_STATE?" 0.5
send_command "SERVO_CAL?" 0.5

read -r -p "Press Enter to send home/open pulses: " _
# q=[0,0,0], 500-2500us mapping. Gripper open = 161.6197 deg ~= 2296us.
send_command "ARM_US 1500 1500 2296" 2.0

read -r -p "Press Enter for q1 +0.15 rad direction test: " _
# Servo-side delta ~= +/-17.19 deg = +/-191us.
send_command "ARM_US 1309 1691 2296" 2.0
send_command "ARM_US 1500 1500 2296" 2.0

read -r -p "Press Enter for q2 +0.15 rad direction test: " _
send_command "ARM_US 1500 1691 2296" 2.0
send_command "ARM_US 1500 1500 2296" 2.0

read -r -p "Press Enter for q3 -0.15 rad close-direction test: " _
send_command "ARM_US 1500 1500 2105" 2.0
send_command "ARM_US 1500 1500 2296" 2.0

read -r -p "Support the arm and type OFF to release PWM: " answer
if [[ "$answer" == "OFF" ]]; then
  send_command "ARM_OFF" 0.5
fi

echo "Done."
