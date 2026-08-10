#!/usr/bin/env bash
set -euo pipefail
WS="${1:-$HOME/MacRobot}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$WS/src"
PKG=macrobot_object_finder

mkdir -p "$SRC"
if [[ -e "$SRC/$PKG" ]]; then
  stamp="$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$WS/archive/object_finder_stage_$stamp"
  mv "$SRC/$PKG" "$WS/archive/object_finder_stage_$stamp/"
fi
cp -a "$HERE/$PKG" "$SRC/"
mkdir -p "$WS/scripts"
cp -a "$HERE/scripts/." "$WS/scripts/"

rm -rf "$WS/build/$PKG" "$WS/install/$PKG"
find "$SRC/$PKG" -maxdepth 3 \( -name '*.egg-info' -o -name '*.dist-info' \) -exec rm -rf {} + 2>/dev/null || true

source /opt/ros/jazzy/setup.bash
cd "$WS"
colcon build --symlink-install --packages-up-to "$PKG" --event-handlers console_direct+

echo
echo "Installed $PKG. Open a new terminal or run:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source $WS/install/setup.bash"
