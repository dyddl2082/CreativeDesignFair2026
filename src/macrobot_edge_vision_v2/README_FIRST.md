# MacRobot Pi edge vision v2

This bundle updates the two existing packages:

- `macrobot_interfaces` 0.2.0
- `depth_candidate_proposal` 0.2.0

v2 keeps depth proposal generation and RGB crop extraction as **separate ROS 2
nodes in the same package**. Copy both package directories into
`~/MacRobot/src/`, rebuild both packages, and also rebuild the updated
`macrobot_interfaces` package on WSL2 before subscribing to RGB crop messages.

See `depth_candidate_proposal/README.md` for build, run, test, and tuning steps.
