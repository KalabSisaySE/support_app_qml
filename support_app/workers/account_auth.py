"""Web based account authentication worker."""

import json
import urllib.request
import uuid
import webbrowser

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from support_app.app_config import (
    DESKTOP_AUTH_CHECK_URL,
    DESKTOP_AUTH_URL,
    get_cloudflare_headers,
)


class AccountAuthWorker(QObject):
    """
    Manages the web authentication flow.
    """
    log = Signal(str)
    finished = Signal(dict) # Emits a dict with new user info on success

    def __init__(self):
        super().__init__()
        self.token = str(uuid.uuid4())
        self.polling_timer = QTimer(self)
        self.polling_timer.setInterval(3000) # Poll every 3 seconds
        self.polling_timer.timeout.connect(self.poll_for_token_status)
        self.attempts = 0
        self.max_attempts = 100 # 5 minutes (100 * 3s)

    @Slot()
    def start_auth_flow(self):
        """Opens the browser and starts polling."""
        self.log.emit("Otváranie prehliadača pre overenie identity...")
        url = f"{DESKTOP_AUTH_URL}?token={self.token}"
        try:
            webbrowser.open(url)
            self.log.emit("Prosím, dokončite prihlásenie vo vašom webovom prehliadači.")
            self.polling_timer.start()
        except Exception as e:
            self.log.emit(f"Nepodarilo sa otvoriť prehliadač: {e}")
            self.finished.emit({}) # Emit empty dict on failure

    def poll_for_token_status(self):
        """Makes an API call to check the token's status."""
        self.attempts += 1
        if self.attempts > self.max_attempts:
            self.log.emit("Časový limit pre prihlásenie vypršal.")
            self.polling_timer.stop()
            self.finished.emit({})
            return

        try:
            url = f"{DESKTOP_AUTH_CHECK_URL}{self.token}/"
            req = urllib.request.Request(url, headers=get_cloudflare_headers())
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get('status') == 'success':
                        self.log.emit("Identita úspešne overená.")
                        self.polling_timer.stop()
                        self.finished.emit(data) # Success!
                # If status is 202 (Pending) or 404 (Not Found yet), we just wait for the next poll.

        except Exception:
            # Don't log every failed poll attempt unless it's a major error
            pass
