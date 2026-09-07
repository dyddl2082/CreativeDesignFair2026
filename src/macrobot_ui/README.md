# macrobot_ui

MacRobot의 자연어 작업 생성 UI를 ROS 2 패키지로 재구성한 버전이다.

- WSL2/노트북: `macrobot_ui` GUI 실행
- Raspberry Pi: `macrobot_ui_backend` 실행
- Pi backend: 승인된 정확한 코드 hash를 다시 확인한 뒤 기존
  `macrobot_action_gateway.code_runner`에 위임
- UI는 `/pico_debug/cmd`나 `/macrobot/arm/joint_goal`을 직접 발행하지 않는다.

상세 설치와 운용 순서는 번들 상위의 `README_KO.md`를 참고한다.

## Korean font handling

The GUI resolves an installed Korean-capable Qt font at runtime instead of
relying on a stylesheet-only family name. Recommended WSL2 packages:

```bash
sudo apt install -y fontconfig fonts-noto-cjk fonts-nanum
fc-cache -f
```

After sourcing the workspace, verify the selected UI and code fonts:

```bash
ros2 run macrobot_ui macrobot_ui_font_check
```

No font binaries are bundled with this ROS 2 package.

## Korean input on WSLg

The UI bootstrap prepares IBus before importing Qt and uses XWayland by default:

```text
QT_QPA_PLATFORM=xcb
QT_IM_MODULE=ibus
QT_IM_MODULES=ibus;compose
GTK_IM_MODULE=ibus
XMODIFIERS=@im=ibus
```

Install the WSL-side input method and verify it:

```bash
./install_wsl_ui_ime.sh --install --activate-hangul
ros2 run macrobot_ui macrobot_ui_ime_check
```

The editable message widget explicitly enables Qt input-method events. The UI does
not implement a custom key event handler that could discard Korean pre-edit text.
