import threading
import logging
import pystray
from PIL import Image

from constants import LOGGER
from helpers import resource_path

logger = logging.getLogger(LOGGER)


class SystemTray:
    def __init__(self, app):
        self.app = app
        self._icon = None
        self._thread = None

    def _create_icon_image(self):
        return Image.open(resource_path("assets/icon.ico"))

    def _build_menu(self):
        from strings import STRINGS

        return pystray.Menu(
            pystray.MenuItem(STRINGS.TRAY.SHOW_APP, self._on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(STRINGS.TRAY.EXIT, self._on_exit),
        )

    def _on_exit(self, _icon=None, _item=None):
        self.app.after(0, self._exit_app)

    def _on_show(self, _icon=None, _item=None):
        self.app.after(0, self._restore_window)

    def _exit_app(self):
        self.app._on_close(force_exit=True)

    def _restore_window(self):
        self.app.deiconify()
        self.app.lift()
        self.app.focus_force()

    def show(self):
        if self._icon is not None:
            return

        try:
            self._icon = pystray.Icon(
                "Vox Launcher",
                self._create_icon_image(),
                "Vox Launcher",
                menu=self._build_menu(),
            )

            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()

            logger.info("System tray icon created.")
        except Exception as e:
            logger.error("Failed to create system tray icon: %s", e)
            self._icon = None

    def hide(self):
        if self._icon is None:
            return

        try:
            self._icon.stop()
        except Exception as e:
            logger.debug("Error stopping tray icon: %s", e)
        finally:
            self._icon = None
            self._thread = None
