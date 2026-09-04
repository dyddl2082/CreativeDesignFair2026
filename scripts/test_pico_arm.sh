#!/usr/bin/env bash
set -euo pipefail

TOPIC="/pico_debug/cmd"

send_command() {
    local command="$1"
    local wait_sec="${2:-1.0}"
    echo
    echo "TX: ${command}"
    ros2 topic pub --once "${TOPIC}" std_msgs/msg/String "{data: '${command}'}"
    sleep "${wait_sec}"
}

cat <<'EOF'
============================================================
MacRobot corrected-direction arm smoke test
============================================================
Physical conventions:
- CH0 left MG996R: CCW -> arm tilts forward
- CH1 right MG996R: CW -> independent second arm joint moves
- CH2 MG90S: 0 deg/open, CCW 180 deg/closed
- Pulse calibration: 0/90/180 deg = 500/1500/2500 us

The first tests use q deltas of 0.15 rad. Through 1:2 gearing,
this is about 17.19 degrees at the servo shaft.
EOF

read -r -p "서보 기구를 지지하고 비상 전원 차단을 준비했다면 YES 입력: " answer
[[ "${answer}" == "YES" ]] || { echo "취소함."; exit 1; }

send_command "PING" 0.5
send_command "STATUS?" 0.5
send_command "SERVO_STATE?" 0.5

# q=[0,0,0]: left=90deg, right=90deg, gripper=0deg(open)
read -r -p "HOME/OPEN (1500,1500,500)을 보내려면 Enter: "
send_command "ARM_US 1500 1500 500" 2.0

# q1=+0.15: only the first arm servo moves; q2 remains zero.
read -r -p "q1 +0.15: 팔 앞쪽 기울기 시험을 하려면 Enter: "
send_command "ARM_US 1691 1500 500" 2.0
send_command "ARM_US 1500 1500 500" 2.0

# q2=+0.15 with q1=0: the independent second servo turns CW.
read -r -p "q2 +0.15: 두 번째 직렬 관절 시험을 하려면 Enter: "
send_command "ARM_US 1500 1309 500" 2.0
send_command "ARM_US 1500 1500 500" 2.0

# q3=+0.15: gripper servo CCW (+17.19deg), closes slightly.
read -r -p "q3 +0.15: 그리퍼 닫힘 시험을 하려면 Enter: "
send_command "ARM_US 1500 1500 691" 2.0
send_command "ARM_US 1500 1500 500" 2.0

read -r -p "팔을 손으로 지지한 상태에서 ARM_OFF를 실행하려면 OFF 입력: " answer
if [[ "${answer}" == "OFF" ]]; then
    send_command "ARM_OFF" 0.5
fi

echo "시험 완료."
