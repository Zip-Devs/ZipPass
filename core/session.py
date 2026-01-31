from __future__ import annotations

import time
from typing import Callable, Optional


class Session:
    """
    Manages vault session state and auto-lock.
    UI must only notify about events.
    """

    def __init__(self):
        self.vault: dict | None = None
        self.master_password: str | None = None
        self.vault_path: str | None = None
        self.is_unlocked: bool = False

        # ===== Auto-lock =====
        self.auto_lock_minutes: int = 5
        self._last_activity: float = time.time()

        # Callback called on lock(reason)
        self.on_lock: Optional[Callable[[str], None]] = None

    # =========================
    # Unlock / Lock
    # =========================

    def unlock(self, vault: dict, master_password: str, vault_path: str):
        """
        Activates session after successful master password entry.
        """
        self.vault = vault
        self.master_password = master_password
        self.vault_path = vault_path
        self.is_unlocked = True
        self._last_activity = time.time()

    def lock(self, reason: str = "manual"):
        """
        Locks session and clears sensitive data.
        """
        if not self.is_unlocked:
            return

        self.vault = None
        self.master_password = None
        self.vault_path = None
        self.is_unlocked = False

        if self.on_lock:
            self.on_lock(reason)

    # =========================
    # Activity tracking
    # =========================

    def notify_activity(self):
        """
        Call on any user interaction.
        """
        if self.is_unlocked:
            self._last_activity = time.time()

    def notify_focus_lost(self):
        """
        Call when window loses focus.
        """
        if self.is_unlocked:
            self.lock(reason="focus_lost")

    def notify_minimized(self):
        """
        Call when window is minimized.
        """
        if self.is_unlocked:
            self.lock(reason="minimized")

    # =========================
    # Auto-lock check
    # =========================

    def check_inactivity(self):
        """
        Call periodically (e.g. by QTimer).
        """
        if not self.is_unlocked:
            return

        idle_seconds = time.time() - self._last_activity
        if idle_seconds >= self.auto_lock_minutes * 60:
            self.lock(reason="timeout")
