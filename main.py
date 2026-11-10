import os
import sys
import time
import socket
import threading
from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

from config import Config, GAMES, is_autostart_enabled, set_autostart
from audio_player import AudioPlayer
from weather import get_current_weather
from downloader import is_game_downloaded, resolve_track_file
from ui import open_settings_dialog, open_download_dialog, get_app_icon, apply_app_theme

_instance_socket = None


def ensure_single_instance(port=42871) -> bool:
    global _instance_socket
    try:
        _instance_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _instance_socket.bind(("127.0.0.1", port))
        _instance_socket.listen(1)
        return True
    except socket.error:
        return False


class WeatherSignals(QObject):
    weather_updated = pyqtSignal(dict)


class ACDPApp(QObject):
    def __init__(self, qapp: QtWidgets.QApplication):
        super().__init__()
        self.qapp = qapp
        self.config = Config()
        self.player = AudioPlayer()
        self.player.set_volume(self.config.get("volume", 75))

        self.last_hour = None
        self.last_weather = None
        self.current_weather_info = None
        self.status_text = "Initializing..."
        self.weather_fetching = False

        self.weather_signals = WeatherSignals()
        self.weather_signals.weather_updated.connect(self._on_weather_received)

        self._init_tray()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(2000)

        QTimer.singleShot(300, self._initial_startup)

    def _init_tray(self):
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(get_app_icon())
        self.tray.setToolTip("Animal Crossing Dynamic Clock")

        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet("""
            QMenu::item:disabled {
                font-weight: bold;
                opacity: 0.9;
            }
        """)

        self.status_action = QtGui.QAction(self.status_text, self)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)

        self.menu.addSeparator()

        self.pause_action = QtGui.QAction("Pause", self)
        self.pause_action.triggered.connect(self._toggle_pause)
        self.menu.addAction(self.pause_action)

        self.game_menu = self.menu.addMenu("Select game")
        self.game_action_group = QtGui.QActionGroup(self)
        self.game_action_group.setExclusive(True)
        self.game_actions = {}

        cur_game = self.config.get("game", "acnh")
        for g in GAMES:
            act = QtGui.QAction(g["shortname"], self)
            act.setCheckable(True)
            act.setChecked(cur_game == g["code"])
            act.triggered.connect(lambda checked, code=g["code"]: self._set_game(code))
            self.game_action_group.addAction(act)
            self.game_menu.addAction(act)
            self.game_actions[g["code"]] = act

        self.menu.addSeparator()

        self.dl_action = QtGui.QAction("Download music...", self)
        self.dl_action.triggered.connect(self._open_downloader)
        self.menu.addAction(self.dl_action)

        self.settings_action = QtGui.QAction("Settings...", self)
        self.settings_action.triggered.connect(self._open_settings)
        self.menu.addAction(self.settings_action)

        self.refresh_weather_action = QtGui.QAction("Refresh weather", self)
        self.refresh_weather_action.triggered.connect(self._refresh_weather)
        self.menu.addAction(self.refresh_weather_action)

        self.autostart_action = QtGui.QAction("Launch on startup", self)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(is_autostart_enabled())
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.menu.addAction(self.autostart_action)

        self.menu.addSeparator()

        self.quit_action = QtGui.QAction("Quit", self)
        self.quit_action.triggered.connect(self._quit)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _initial_startup(self):
        self._refresh_weather()
        if not is_game_downloaded(self.config.get("game")):
            open_download_dialog(self.config, on_finish=self._on_download_finished)

    def _on_tray_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick, QtWidgets.QSystemTrayIcon.ActivationReason.Trigger):
            open_settings_dialog(self.config, player=self.player, on_config_changed=self._on_config_changed)

    def _toggle_pause(self):
        self.player.toggle_pause()
        self.config.set("paused", self.player.is_paused)
        self._update_status()

    def _set_game(self, code):
        self.config.set("game", code)
        self.last_hour = None
        for c, act in self.game_actions.items():
            act.setChecked(c == code)
        self._update_status()
        self._tick()

    def _toggle_autostart(self):
        new_state = not is_autostart_enabled()
        set_autostart(new_state)
        self.config.set("autostart", new_state)
        self.autostart_action.setChecked(new_state)

    def _refresh_weather(self):
        if self.weather_fetching:
            return
        self.weather_fetching = True

        def _worker():
            w = get_current_weather(self.config.get("city", ""), force=True)
            self.weather_signals.weather_updated.emit(w)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_weather_received(self, weather_info):
        self.weather_fetching = False
        self.current_weather_info = weather_info
        self.last_hour = None
        self._update_status()
        self._tick()

    def _open_settings(self):
        open_settings_dialog(self.config, player=self.player, on_config_changed=self._on_config_changed)

    def _open_downloader(self):
        open_download_dialog(self.config, on_finish=self._on_download_finished)

    def _on_config_changed(self):
        self.player.set_volume(self.config.get("volume", 75))
        self.last_hour = None
        cur = self.config.get("game", "acnh")
        for c, act in self.game_actions.items():
            act.setChecked(c == cur)
        self.autostart_action.setChecked(is_autostart_enabled())
        self._refresh_weather()

    def _on_download_finished(self):
        self.last_hour = None
        self._update_status()
        self._tick()

    def _update_status(self):
        game_info = self.config.get_game_info()
        hour_str = datetime.now().strftime("%H")
        game_name = game_info.get("shortname", game_info.get("name", "Animal Crossing"))

        self.pause_action.setText("Resume music" if self.player.is_paused else "Pause")

        if self.player.is_paused:
            self.status_text = f"{game_name} - {hour_str}h (Paused)"
        elif not is_game_downloaded(self.config.get("game")):
            self.status_text = f"{game_name} - Music not downloaded"
        elif self.current_weather_info:
            weather_desc = self.current_weather_info.get("description", "Clear sky")
            self.status_text = f"{game_name} - {hour_str}h ({weather_desc})"
        else:
            self.status_text = f"{game_name} - {hour_str}h"

        self.status_action.setText(self.status_text)
        self.tray.setToolTip(self.status_text[:128])

    def _tick(self):
        try:
            game_code = self.config.get("game", "acnh")
            game_info = self.config.get_game_info(game_code)
            hour_str = datetime.now().strftime("%H")

            if self.current_weather_info is None or (time.time() - self.current_weather_info.get("timestamp", 0) > 600):
                self._refresh_weather()

            weather_cat = self.current_weather_info.get("category", "clear") if self.current_weather_info else "clear"
            weather_desc = self.current_weather_info.get("description", "Clear sky") if self.current_weather_info else "Clear sky"

            if not is_game_downloaded(game_code):
                if self.player.is_playing():
                    self.player.stop()
                self._update_status()
                return

            if (hour_str != self.last_hour) or (weather_cat != self.last_weather):
                track_file = resolve_track_file(
                    game_code=game_code,
                    weather=weather_cat,
                    hour_str=hour_str,
                    roost=self.config.get("roost", False)
                )

                if track_file and os.path.exists(track_file):
                    if not self.config.get("paused", False):
                        self.player.play_track(track_file, loop=True)

                    if self.last_hour is not None and self.config.get("notifications", True):
                        self.tray.showMessage(
                            f"It's {hour_str}:00 ({weather_desc})",
                            f"Music: {game_info['name']}",
                            QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                            4000
                        )

                    self.last_hour = hour_str
                    self.last_weather = weather_cat
                else:
                    print(f"Track not found for {game_code} / {weather_cat} / {hour_str}")

            self._update_status()

        except Exception as e:
            print(f"Error in tick: {e}")

    def _quit(self):
        self.timer.stop()
        self.player.stop()
        self.tray.hide()
        self.qapp.quit()


def main():
    if not ensure_single_instance():
        dummy_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMessageBox.information(
            None,
            "Animal Crossing Dynamic Clock",
            "The application is already running in the system tray."
        )
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Animal Crossing Dynamic Clock")
    app.setOrganizationName("ACDC")
    app.setQuitOnLastWindowClosed(False)
    apply_app_theme(app)

    acdp_app = ACDPApp(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
