from __future__ import annotations

import sys


def main(args: list[str] | None = None) -> int:
    argv = list(sys.argv if args is None else args)
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        print(
            "ERROR: PySide6 is required on the UI computer. "
            "Install the package's requirements-ui.txt.",
            file=sys.stderr,
        )
        return 2

    import rclpy
    from rclpy.node import Node
    from rclpy.utilities import remove_ros_args

    from .app import MainWindow, stylesheet
    from .font_support import FontConfigurationError, configure_application_fonts
    from .config import AppConfig
    from .ros_qt_bridge import RosExecutorThread, RosUiBridge

    rclpy.init(args=argv)
    node: Node | None = None
    ros_thread: RosExecutorThread | None = None
    try:
        node = Node("macrobot_ui")
        config = AppConfig.from_node(node)
        qt_argv = remove_ros_args(args=argv)
        app = QApplication(qt_argv)
        app.setApplicationName("MacRobot ROS 2 UI")
        try:
            font_selection = configure_application_fonts(app)
        except FontConfigurationError as error:
            print(str(error), file=sys.stderr)
            QMessageBox.critical(None, "MacRobot UI font error", str(error))
            return 3
        print(
            "[MacRobot UI fonts] "
            f"UI={font_selection.ui_family!r}, "
            f"code={font_selection.code_family!r}",
            file=sys.stderr,
        )
        for warning in font_selection.warnings:
            print(f"[MacRobot UI fonts] WARNING: {warning}", file=sys.stderr)
        app.setStyleSheet(stylesheet())

        bridge = RosUiBridge(node)
        ros_thread = RosExecutorThread(node)
        window = MainWindow(config, bridge, font_selection.code_font())
        ros_thread.failed.connect(
            lambda message: QMessageBox.critical(
                window,
                "ROS executor 오류",
                message,
            )
        )
        ros_thread.start()

        def cleanup() -> None:
            if ros_thread is not None:
                ros_thread.stop()
            if node is not None:
                node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()

        app.aboutToQuit.connect(cleanup)
        window.show()
        return int(app.exec())
    finally:
        if ros_thread is not None and ros_thread.isRunning():
            ros_thread.stop()
        if node is not None:
            try:
                node.destroy_node()
            except Exception:
                pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
