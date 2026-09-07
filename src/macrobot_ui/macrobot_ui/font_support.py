from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Iterable

from PySide6.QtGui import QFont, QFontDatabase, QFontInfo, QRawFont
from PySide6.QtWidgets import QApplication


# Use both precomposed Hangul syllables and ASCII so that a selected family is
# useful throughout the UI, including Python comments and generated strings.
KOREAN_PROBE_TEXT = "한글가나다라마바사아자차카타파하 ABCxyz0123"

UI_FONT_CANDIDATES = (
    "Noto Sans CJK KR",
    "Noto Sans KR",
    "NanumBarunGothic",
    "NanumGothic",
    "UnDotum",
    "Baekmuk Dotum",
    "Malgun Gothic",
    "맑은 고딕",
    "Apple SD Gothic Neo",
)

CODE_FONT_CANDIDATES = (
    "Noto Sans Mono CJK KR",
    "NanumGothicCoding",
    "나눔고딕코딩",
    "D2Coding",
    "Noto Sans CJK KR",
    "NanumGothic",
    "Malgun Gothic",
    "맑은 고딕",
)

# No font bytes are bundled with macrobot_ui. These are only well-known paths
# that may already exist on the user's Ubuntu/WSL2 installation. Registering an
# existing local file with Qt avoids stale fontconfig caches and also allows
# WSL2 to use the host Windows Korean font without copying or redistributing it.
LINUX_FONT_FILES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicCodingBold.ttf",
    "/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf",
    "/usr/share/fonts/truetype/unfonts-core/UnDotumBold.ttf",
)

WINDOWS_FONT_FILES = (
    "/mnt/c/Windows/Fonts/malgun.ttf",
    "/mnt/c/Windows/Fonts/malgunbd.ttf",
    "/mnt/c/Windows/Fonts/malgunsl.ttf",
)


class FontConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class FontSelection:
    ui_family: str
    code_family: str
    code_fixed_pitch: bool
    registered_files: tuple[str, ...]
    registered_families: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def code_font(self, point_size: float | None = None) -> QFont:
        font = QFont(self.code_family)
        if point_size is not None and point_size > 0:
            font.setPointSizeF(float(point_size))
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(bool(self.code_fixed_pitch))
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _split_font_names(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    normalized = raw.replace(";", ",")
    return tuple(item.strip() for item in normalized.split(",") if item.strip())


def _is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    for path in (Path("/proc/sys/kernel/osrelease"), Path("/proc/version")):
        try:
            if "microsoft" in path.read_text(encoding="utf-8").lower():
                return True
        except OSError:
            continue
    return False


def _register_existing_fonts(paths: Iterable[str]) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    registered_files: list[str] = []
    registered_families: list[str] = []
    warnings: list[str] = []

    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            warnings.append(f"Qt could not register local font file: {path}")
            continue
        families = [str(item) for item in QFontDatabase.applicationFontFamilies(font_id)]
        registered_files.append(str(path))
        registered_families.extend(families)

    # Preserve order while removing duplicates.
    files = tuple(dict.fromkeys(registered_files))
    families = tuple(dict.fromkeys(registered_families))
    return files, families, tuple(warnings)


def _family_map() -> dict[str, str]:
    return {str(family).casefold(): str(family) for family in QFontDatabase.families()}


def _canonical_family(name: str, families: dict[str, str]) -> str | None:
    return families.get(name.casefold())


def family_supports_text(family: str, text: str = KOREAN_PROBE_TEXT) -> bool:
    """Return True only when the selected face itself contains all probe glyphs.

    Checking QRawFont prevents a false positive where QFont silently substitutes
    an unrelated fallback family after a missing family name is requested.
    """

    if not family:
        return False
    raw = QRawFont.fromFont(QFont(family))
    if not raw.isValid():
        return False
    try:
        return all(raw.supportsCharacter(ord(character)) for character in text)
    except TypeError:
        # Some PySide6 builds expose the str overload instead of the UCS-4 one.
        return all(raw.supportsCharacter(character) for character in text)


def _is_fixed_pitch(family: str) -> bool:
    try:
        return bool(QFontDatabase.isFixedPitch(family))
    except (AttributeError, TypeError):
        return bool(QFontInfo(QFont(family)).fixedPitch())


def _select_family(
    preferred: Iterable[str],
    *,
    require_fixed_pitch: bool,
    allow_any_korean_fallback: bool,
) -> tuple[str | None, bool]:
    families = _family_map()

    for requested in preferred:
        actual = _canonical_family(requested, families)
        if actual is None or not family_supports_text(actual):
            continue
        fixed = _is_fixed_pitch(actual)
        if require_fixed_pitch and not fixed:
            continue
        return actual, fixed

    if allow_any_korean_fallback:
        for actual in sorted(families.values(), key=str.casefold):
            if not family_supports_text(actual):
                continue
            fixed = _is_fixed_pitch(actual)
            if require_fixed_pitch and not fixed:
                continue
            return actual, fixed

    return None, False


def _missing_font_message(available_count: int, warnings: Iterable[str]) -> str:
    details = "\n".join(f"- {item}" for item in warnings)
    if details:
        details = "\nQt font registration warnings:\n" + details
    return (
        "MacRobot UI could not find a Korean-capable font.\n\n"
        "On Ubuntu/WSL2 install the recommended fonts, rebuild the font cache, "
        "and restart the UI:\n\n"
        "  sudo apt update\n"
        "  sudo apt install -y fontconfig fonts-noto-cjk fonts-nanum\n"
        "  fc-cache -f\n\n"
        "Then verify:\n\n"
        "  fc-match 'Noto Sans CJK KR:lang=ko'\n"
        "  fc-list :lang=ko family | head\n\n"
        f"Qt currently reports {available_count} font families."
        f"{details}"
    )


def configure_application_fonts(app: QApplication) -> FontSelection:
    """Resolve real Korean-capable UI/code fonts and apply the UI font globally."""

    register_fonts = _env_bool("MACROBOT_UI_REGISTER_SYSTEM_FONTS", True)
    use_windows_fonts = _env_bool("MACROBOT_UI_USE_WINDOWS_FONTS", True)
    strict = _env_bool("MACROBOT_UI_STRICT_FONT_CHECK", True)

    registered_files: tuple[str, ...] = ()
    registered_families: tuple[str, ...] = ()
    warnings: list[str] = []

    if register_fonts:
        paths = list(LINUX_FONT_FILES)
        if use_windows_fonts and _is_wsl():
            paths.extend(WINDOWS_FONT_FILES)
        registered_files, registered_families, registration_warnings = (
            _register_existing_fonts(paths)
        )
        warnings.extend(registration_warnings)

    ui_override = _split_font_names(os.environ.get("MACROBOT_UI_FONT_FAMILY"))
    code_override = _split_font_names(os.environ.get("MACROBOT_CODE_FONT_FAMILY"))

    ui_family, _ = _select_family(
        (*ui_override, *UI_FONT_CANDIDATES),
        require_fixed_pitch=False,
        allow_any_korean_fallback=True,
    )

    if ui_family is None:
        message = _missing_font_message(len(QFontDatabase.families()), warnings)
        if strict:
            raise FontConfigurationError(message)
        fallback = QFontInfo(app.font()).family()
        ui_family = fallback or "Sans Serif"
        warnings.append("No Korean-capable UI font found; using Qt fallback family.")

    code_family, code_fixed_pitch = _select_family(
        (*code_override, *CODE_FONT_CANDIDATES),
        require_fixed_pitch=True,
        allow_any_korean_fallback=True,
    )
    if code_family is None:
        # Readable Korean is more important than fixed-pitch alignment.
        code_family = ui_family
        code_fixed_pitch = _is_fixed_pitch(code_family)
        warnings.append(
            "No Korean-capable fixed-pitch font found; code editor uses the UI font."
        )

    application_font = QFont(app.font())
    application_font.setFamily(ui_family)
    application_font.setStyleHint(QFont.StyleHint.SansSerif)
    application_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(application_font)
    app.setProperty("macrobotUiFontFamily", ui_family)
    app.setProperty("macrobotCodeFontFamily", code_family)

    selection = FontSelection(
        ui_family=ui_family,
        code_family=code_family,
        code_fixed_pitch=code_fixed_pitch,
        registered_files=registered_files,
        registered_families=registered_families,
        warnings=tuple(warnings),
    )
    return selection


def diagnostic_main() -> int:
    """Run a Qt font check without starting ROS or the MacRobot window."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication(["macrobot-ui-font-check"])
    try:
        selection = configure_application_fonts(app)
    except FontConfigurationError as error:
        payload = {
            "ok": False,
            "error": str(error),
            "wsl": _is_wsl(),
            "qt_family_count": len(QFontDatabase.families()),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    payload = {
        "ok": True,
        "selection": selection.to_dict(),
        "ui_probe_supported": family_supports_text(selection.ui_family),
        "code_probe_supported": family_supports_text(selection.code_family),
        "wsl": _is_wsl(),
        "qt_family_count": len(QFontDatabase.families()),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(diagnostic_main())
