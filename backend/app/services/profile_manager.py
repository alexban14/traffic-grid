"""
Manages persistent browser profiles (cookies + localStorage) per identity.

Profiles are stored as JSON files on disk, one directory per identity.
Playwright's context.storage_state() / browser.new_context(storage_state=)
handles the serialization.
"""

import os
import json
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

PROFILES_DIR = os.environ.get("TG_PROFILES_DIR", "/app/profiles")


class ProfileManager:
    def __init__(self, base_dir: str = PROFILES_DIR):
        self.base_dir = Path(base_dir)

    def _profile_path(self, platform: str, username: str) -> Path:
        return self.base_dir / platform / username

    def _state_file(self, platform: str, username: str) -> Path:
        return self._profile_path(platform, username) / "state.json"

    def _metadata_file(self, platform: str, username: str) -> Path:
        return self._profile_path(platform, username) / "metadata.json"

    def has_profile(self, platform: str, username: str) -> bool:
        return self._state_file(platform, username).exists()

    def get_storage_state_path(self, platform: str, username: str) -> Optional[str]:
        """Return the path to the Playwright storage state file, or None if not warmed up."""
        state_file = self._state_file(platform, username)
        if state_file.exists():
            return str(state_file)
        return None

    async def save_context_state(self, context, platform: str, username: str) -> str:
        """Save browser context state (cookies + localStorage) to disk."""
        profile_dir = self._profile_path(platform, username)
        profile_dir.mkdir(parents=True, exist_ok=True)

        state_file = self._state_file(platform, username)
        await context.storage_state(path=str(state_file))

        # Save metadata
        metadata = {
            "platform": platform,
            "username": username,
            "last_saved": __import__("datetime").datetime.utcnow().isoformat(),
        }
        self._metadata_file(platform, username).write_text(json.dumps(metadata, indent=2))

        logger.info(f"Saved profile for {username} ({platform}) → {state_file}")
        return str(state_file)

    def get_metadata(self, platform: str, username: str) -> Optional[dict]:
        meta_file = self._metadata_file(platform, username)
        if meta_file.exists():
            return json.loads(meta_file.read_text())
        return None
