#!/usr/bin/env python3
"""
Standalone floating window launcher for Joplin Calendar (GTK3 + WebKit2).
Can load either the local joplin-cal.html file or your self-hosted URL.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gtk, WebKit2


JOPLIN_PROFILE_DIR = os.path.expanduser("~/.config/joplin-desktop")
JOPLIN_IPC_SECRET_FILE = os.path.join(JOPLIN_PROFILE_DIR, "ipc_secret_key.txt")


def open_in_joplin(uri: str) -> None:
    """
    Opens a joplin:// callback URI in the already-running Joplin Desktop instance
    by sending an 'onSecondInstance' IPC message directly to Joplin's local IPC
    server (ports 2658..2667). Only spawns xdg-open if Joplin is not running at all.
    """
    try:
        if os.path.exists(JOPLIN_IPC_SECRET_FILE):
            with open(JOPLIN_IPC_SECRET_FILE, "r", encoding="utf-8") as f:
                secret_key = f.read().strip()

            payload = json.dumps({
                "action": "onSecondInstance",
                "data": {
                    "senderPort": 2667,
                    "profilePath": JOPLIN_PROFILE_DIR,
                    "argv": ["/opt/Joplin/joplin", uri],
                },
                "secretKey": secret_key,
            }).encode("utf-8")

            for port in range(2658, 2667):
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=0.4) as resp:
                        if resp.status == 200:
                            # Activated the single running Joplin instance; stop immediately
                            return
                except (urllib.error.URLError, TimeoutError, OSError):
                    continue
    except Exception:
        pass

    # Fallback: Joplin is not running at all, so launch it
    subprocess.Popen(
        ["xdg-open", uri],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class JoplinCalendarWindow(Gtk.Window):
    def __init__(self, target_url: str):
        super().__init__(title="Joplin Calendar")
        self.set_default_size(980, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.always_on_top = True
        self.set_keep_above(self.always_on_top)

        # HeaderBar with Always-on-Top toggle
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Joplin Calendar"

        pin_btn = Gtk.ToggleButton(label="📌 Always on Top")
        pin_btn.set_active(self.always_on_top)
        pin_btn.connect("toggled", self.on_pin_toggled)
        header.pack_end(pin_btn)
        self.set_titlebar(header)

        # WebKit2 WebView with local storage & file access enabled
        settings = WebKit2.Settings()
        settings.set_enable_write_console_messages_to_stdout(True)
        settings.set_allow_universal_access_from_file_urls(True)
        settings.set_allow_file_access_from_file_urls(True)

        ucm = WebKit2.UserContentManager()
        ucm.add_script(
            WebKit2.UserScript.new(
                "window.__JOPLIN_NATIVE_WRAPPER__ = true;",
                WebKit2.UserContentInjectedFrames.TOP_FRAME,
                WebKit2.UserScriptInjectionTime.START,
                None,
                None,
            )
        )

        self.webview = WebKit2.WebView.new_with_user_content_manager(ucm)
        self.webview.set_settings(settings)
        self.webview.connect("decide-policy", self.on_decide_policy)
        self.add(self.webview)

        if target_url.startswith(("http://", "https://", "file://")):
            self.webview.load_uri(target_url)
        else:
            abs_path = os.path.abspath(target_url)
            self.webview.load_uri(f"file://{abs_path}")

        self.connect("destroy", Gtk.main_quit)

    def on_pin_toggled(self, button: Gtk.ToggleButton):
        self.always_on_top = button.get_active()
        self.set_keep_above(self.always_on_top)

    def on_decide_policy(self, webview, decision, decision_type):
        if decision_type in (
            WebKit2.PolicyDecisionType.NAVIGATION_ACTION,
            WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION,
        ):
            nav_action = decision.get_navigation_action()
            uri = nav_action.get_request().get_uri()
            if uri.startswith("joplin://"):
                decision.ignore()
                open_in_joplin(uri)
                return True
        return False


def main():
    default_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "joplin-cal.html")
    target = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("JOPLIN_CAL_URL", default_html)
    win = JoplinCalendarWindow(target)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()

