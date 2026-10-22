from pathlib import Path
import shutil

from django.conf import settings
from journal import models as journal_models


THEME_NAME = "gold"

THEME_DIR = Path(settings.BASE_DIR) / "themes" / THEME_NAME
STATIC_DIR = Path(settings.BASE_DIR) / "static" / THEME_NAME

EXCLUDED_SUFFIXES = (".bak", ".backup", ".pyc")
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}


def should_copy(path):
    """Exclude temporary, backup and development files."""
    if path.name in EXCLUDED_NAMES:
        return False

    if path.name.endswith(EXCLUDED_SUFFIXES):
        return False

    if path.name.endswith("-test.css"):
        return False

    if "__pycache__" in path.parts:
        return False

    return True


def copy_directory(source, destination):
    """Copy assets recursively while preserving directory structure."""
    if not source.is_dir():
        return

    for file in source.rglob("*"):
        if not file.is_file() or not should_copy(file):
            continue

        target = destination / file.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)


def create_paths():
    """Create Gold static directories."""
    for folder in ("css", "js", "imgs", "fonts"):
        (STATIC_DIR / folder).mkdir(parents=True, exist_ok=True)


def process_journals():
    """Copy journal-specific Gold CSS overrides."""
    for journal in journal_models.Journal.objects.all():
        for file in journal.scss_files:
            if file.endswith("gold_override.css"):
                source = Path(settings.BASE_DIR) / file
                destination = (
                    STATIC_DIR
                    / "css"
                    / f"journal{journal.id}_override.css"
                )

                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)


def build():
    """Build Gold theme static assets."""
    create_paths()

    copy_directory(
        THEME_DIR / "assets",
        STATIC_DIR,
    )

    copy_directory(
        THEME_DIR / "imgs",
        STATIC_DIR / "imgs",
    )

    process_journals()
