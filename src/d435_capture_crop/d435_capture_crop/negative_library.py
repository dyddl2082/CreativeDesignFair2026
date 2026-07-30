"""Automatic shared-negative indexing for MacRobot datasets.

Canonical images are stored only once:

* registered object views live in ``curated/objects/<object>``;
* reusable distractors live in ``negative/library/<label>``;
* backgrounds live in ``negative/backgrounds/<label>``.

The existing embedding node already reads ``negative/confusers/<target>``.  To
keep that interface stable, this module builds a lightweight ``_auto`` view for
each target using relative symbolic links.  Manual target-specific negatives
outside ``_auto`` are never changed.
"""

from __future__ import annotations

import os
import shutil
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class NegativeSyncSummary:
    """Result of one automatic per-target negative-view rebuild."""

    target_count: int = 0
    registered_source_count: int = 0
    library_source_count: int = 0
    created_symlinks: int = 0
    created_hardlinks: int = 0
    copied_fallbacks: int = 0
    skipped_same_identity: int = 0
    removed_auto_directories: int = 0
    total_managed_files: int = 0

    def as_dict(self) -> dict[str, int]:
        return {key: int(value) for key, value in asdict(self).items()}


def identity_key(value: str) -> str:
    """Return a punctuation-insensitive, Unicode-safe identity key."""

    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return "".join(character for character in normalized if character.isalnum())


def is_supported_image(path: Path) -> bool:
    """Return True for an image that may enter an embedding reference bank."""

    name = path.name.casefold()
    if name.startswith(".") or ".bak" in name:
        return False
    if "_depth." in name or name.endswith("_mask.png"):
        return False
    return path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS


def iter_image_files(root: Path) -> list[Path]:
    """Return supported images recursively in deterministic order."""

    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(
        (path for path in root.rglob("*") if is_supported_image(path)),
        key=lambda path: str(path).casefold(),
    )


def visible_directories(root: Path, *, reserved_name: str = "_auto") -> list[Path]:
    """Return non-hidden child directories, excluding the generated directory."""

    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(
        (
            path
            for path in root.iterdir()
            if path.is_dir()
            and not path.name.startswith(".")
            and path.name != reserved_name
        ),
        key=lambda path: path.name.casefold(),
    )


def _remove_generated_directory(path: Path) -> bool:
    """Remove only a reserved generated path and leave manual data untouched."""

    if not os.path.lexists(path):
        return False
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)
    return True


def _link_or_fallback(source: Path, destination: Path) -> str:
    """Create a relative symlink, then hardlink/copy only when unavailable."""

    source = source.resolve(strict=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(destination):
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    relative_source = os.path.relpath(source, start=destination.parent.resolve())
    try:
        destination.symlink_to(relative_source)
        return "symlink"
    except OSError:
        try:
            os.link(source, destination)
            return "hardlink"
        except OSError:
            shutil.copy2(source, destination)
            return "copy"


def _add_source_tree(
    *,
    source_root: Path,
    destination_root: Path,
    summary: NegativeSyncSummary,
    source_kind: str,
) -> None:
    images = iter_image_files(source_root)
    if source_kind == "registered":
        summary.registered_source_count += len(images)
    else:
        summary.library_source_count += len(images)

    for source in images:
        relative = source.relative_to(source_root)
        destination = destination_root / relative
        mode = _link_or_fallback(source, destination)
        if mode == "symlink":
            summary.created_symlinks += 1
        elif mode == "hardlink":
            summary.created_hardlinks += 1
        else:
            summary.copied_fallbacks += 1
        summary.total_managed_files += 1


def sync_negative_views(
    *,
    curated_root: Path,
    library_root: Path,
    confusers_root: Path,
    auto_directory_name: str = "_auto",
) -> NegativeSyncSummary:
    """Rebuild automatic per-target negatives without duplicating captures.

    For every registered target in ``curated_root``:

    * views of every *other* registered object are linked as negatives;
    * images captured once in ``library_root`` are linked as reusable negatives;
    * a library category whose name identifies the current target is skipped;
    * only ``confusers/<target>/<auto_directory_name>`` is replaced, preserving
      all manual hard negatives.

    Backgrounds are not linked because the embedding node already reads the
    global ``negative/backgrounds`` directory directly.
    """

    auto_name = str(auto_directory_name or "_auto").strip()
    if not auto_name or "/" in auto_name or "\\" in auto_name or auto_name in {".", ".."}:
        raise ValueError("auto_directory_name must be one safe directory name")

    curated_root = Path(curated_root).expanduser().resolve()
    library_root = Path(library_root).expanduser().resolve()
    confusers_root = Path(confusers_root).expanduser().resolve()
    curated_root.mkdir(parents=True, exist_ok=True)
    library_root.mkdir(parents=True, exist_ok=True)
    confusers_root.mkdir(parents=True, exist_ok=True)

    targets = visible_directories(curated_root, reserved_name=auto_name)
    library_categories = visible_directories(library_root, reserved_name=auto_name)
    summary = NegativeSyncSummary(target_count=len(targets))
    target_identities = {identity_key(target.name): target for target in targets}

    # Remove generated views for targets that no longer exist, preserving every
    # other file or directory under negative/confusers.
    for target_dir in visible_directories(confusers_root, reserved_name=auto_name):
        if identity_key(target_dir.name) not in target_identities:
            if _remove_generated_directory(target_dir / auto_name):
                summary.removed_auto_directories += 1

    for target in targets:
        auto_root = confusers_root / target.name / auto_name
        if _remove_generated_directory(auto_root):
            summary.removed_auto_directories += 1
        auto_root.mkdir(parents=True, exist_ok=True)
        target_identity = identity_key(target.name)

        # A registered object is photographed once as a positive.  Its views
        # become negatives automatically for every other target.
        for other_target in targets:
            if identity_key(other_target.name) == target_identity:
                continue
            _add_source_tree(
                source_root=other_target,
                destination_root=auto_root / "registered" / other_target.name,
                summary=summary,
                source_kind="registered",
            )

        # A non-target distractor is photographed once in negative/library and
        # reused for all targets.  Matching labels are excluded defensively.
        for category in library_categories:
            if identity_key(category.name) == target_identity:
                summary.skipped_same_identity += len(iter_image_files(category))
                continue
            _add_source_tree(
                source_root=category,
                destination_root=auto_root / "library" / category.name,
                summary=summary,
                source_kind="library",
            )

    return summary
