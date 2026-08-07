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

echo "MacRobot Pico arm smoke test"
echo "Run only with the arm supported and, for first test, servo gears detached."
read -r -p "Type YES to continue: " answer
[[ "$answer" == "YES" ]] || exit 1

send_command "PING" 0.5
send_command "STATUS?" 0.5
send_command "SERVO_STATE?" 0.5

read -r -p "Press Enter to send home/open pulses: " _
send_command "ARM_US 1500 1500 1898" 2.0

read -r -p "Press Enter for q1 +0.05 rad direction test: " _
send_command "ARM_US 1468 1532 1898" 2.0
send_command "ARM_US 1500 1500 1898" 2.0

read -r -p "Press Enter for q2 +0.05 rad direction test: " _
send_command "ARM_US 1500 1532 1898" 2.0
send_command "ARM_US 1500 1500 1898" 2.0

read -r -p "Press Enter for q3 -0.05 rad close-direction test: " _
send_command "ARM_US 1500 1500 1866" 2.0
send_command "ARM_US 1500 1500 1898" 2.0

read -r -p "Support the arm and type OFF to release PWM: " answer
if [[ "$answer" == "OFF" ]]; then
  send_command "ARM_OFF" 0.5
fi

echo "Done."
