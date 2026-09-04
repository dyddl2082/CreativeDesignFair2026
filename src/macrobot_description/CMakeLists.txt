cmake_minimum_required(VERSION 3.8)
project(macrobot_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes launch rviz config docs images validation
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/validate_description.py
  scripts/print_joint_direction_report.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
