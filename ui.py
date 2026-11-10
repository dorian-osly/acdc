import os
import sys
import threading
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QThread

from config import Config, GAMES, ASSETS_DIR, set_autostart, is_autostart_enabled, open_music_folder
from downloader import download_game_ost, is_game_downloaded
from weather import detect_city, get_current_weather

QT_STYLESHEET = """
QPushButton#PrimaryButton {
    background-color: #2E7D32;
    color: #FFFFFF;
    font-weight: 600;
    border-radius: 5px;
    padding: 6px 18px;
    min-height: 20px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #388E3C;
}

QPushButton#PrimaryButton:pressed {
    background-color: #1B5E20;
}

QPushButton#DangerButton {
    background-color: #C62828;
    color: #FFFFFF;
    font-weight: 600;
    border-radius: 5px;
    padding: 6px 18px;
    min-height: 20px;
    border: none;
}

QPushButton#DangerButton:hover {
    background-color: #D32F2F;
}

QPushButton#DangerButton:pressed {
    background-color: #B71C1C;
}
"""


def apply_app_theme(app: QtWidgets.QApplication):
    if "windows11" in QtWidgets.QStyleFactory.keys():
        app.setStyle("windows11")
    elif "Fusion" in QtWidgets.QStyleFactory.keys():
        app.setStyle("Fusion")

    palette = app.palette()
    green = QtGui.QColor("#2E7D32")
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, green)
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.white)
    palette.setColor(QtGui.QPalette.ColorRole.Accent, green)
    app.setPalette(palette)
    app.setStyleSheet(QT_STYLESHEET)


def get_app_icon() -> QtGui.QIcon:
    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    if os.path.exists(ico_path):
        return QtGui.QIcon(ico_path)
    if os.path.exists(png_path):
        return QtGui.QIcon(png_path)
    return QtGui.QIcon()


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(bool)

    def __init__(self, game_code: str, cancel_event: threading.Event):
        super().__init__()
        self.game_code = game_code
        self.cancel_event = cancel_event

    def run(self):
        def _cb(curr, total, filename):
            self.progress.emit(curr, total, filename)

        success = download_game_ost(
            self.game_code,
            progress_callback=_cb,
            cancel_event=self.cancel_event
        )
        self.finished.emit(success)


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, config: Config, initial_game: str = None, on_finish=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.on_finish = on_finish
        self.cancel_event = threading.Event()
        self.worker = None

        self.setWindowTitle("ACDC - Download Tracks")
        self.setWindowIcon(get_app_icon())
        self.setMinimumWidth(520)
        self.resize(540, 270)

        self._init_ui(initial_game)

    def _init_ui(self, initial_game):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_lbl = QtWidgets.QLabel("Music Download")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")
        layout.addWidget(title_lbl)

        card = QtWidgets.QGroupBox(" Download Options ")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(14, 16, 14, 16)
        card_layout.setSpacing(12)

        combo_row = QtWidgets.QHBoxLayout()
        combo_row.addWidget(QtWidgets.QLabel("Select game:"))
        self.game_combo = QtWidgets.QComboBox()
        self.game_codes = [g["code"] for g in GAMES]
        for g in GAMES:
            self.game_combo.addItem(f"{g['name']} (~{g['size']})", g["code"])

        target_code = initial_game or self.config.get("game", "acnh")
        if target_code in self.game_codes:
            self.game_combo.setCurrentIndex(self.game_codes.index(target_code))

        self.game_combo.currentIndexChanged.connect(self._on_game_selected)
        combo_row.addWidget(self.game_combo, 1)
        card_layout.addLayout(combo_row)

        self.prog_bar = QtWidgets.QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        card_layout.addWidget(self.prog_bar)

        self.status_lbl = QtWidgets.QLabel("Ready to download.")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #888888;")
        card_layout.addWidget(self.status_lbl)

        layout.addWidget(card)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(10)

        self.folder_btn = QtWidgets.QPushButton("Open Folder")
        self.folder_btn.clicked.connect(self._on_open_folder)
        btn_row.addWidget(self.folder_btn)

        btn_row.addStretch()

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_row.addWidget(self.close_btn)

        self.action_btn = QtWidgets.QPushButton("Start Download")
        self.action_btn.setObjectName("PrimaryButton")
        self.action_btn.clicked.connect(self._toggle_download)
        btn_row.addWidget(self.action_btn)

        layout.addLayout(btn_row)

        self._check_initial_game_state()

    def _check_initial_game_state(self):
        code = self.game_combo.currentData()
        if is_game_downloaded(code):
            self.prog_bar.setValue(100)
            self.status_lbl.setText("Music already downloaded for this game!")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #2E7D32; font-weight: 600;")
        else:
            self.prog_bar.setValue(0)
            self.status_lbl.setText("Ready to download.")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #888888;")

    def _on_game_selected(self):
        if self.worker is None or not self.worker.isRunning():
            self._check_initial_game_state()

    def _on_open_folder(self):
        code = self.game_combo.currentData()
        open_music_folder(code)

    def _toggle_download(self):
        if self.worker and self.worker.isRunning():
            self.cancel_event.set()
            self.status_lbl.setText("Cancelling...")
            self.action_btn.setEnabled(False)
            return

        code = self.game_combo.currentData()
        self.cancel_event.clear()
        self.action_btn.setText("Cancel")
        self.action_btn.setObjectName("DangerButton")
        self.action_btn.setStyle(self.action_btn.style())
        self.game_combo.setEnabled(False)
        self.prog_bar.setValue(0)
        self.status_lbl.setText("Connecting...")

        self.worker = DownloadWorker(code, self.cancel_event)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, curr, total, filename):
        pct = int((curr / total) * 100) if total > 0 else 0
        self.prog_bar.setValue(pct)
        self.status_lbl.setText(f"[{curr}/{total}] Downloading: {filename}")
        self.status_lbl.setStyleSheet("font-size: 11px;")

    def _on_finished(self, success):
        self.game_combo.setEnabled(True)
        self.action_btn.setEnabled(True)
        self.action_btn.setText("Start Download")
        self.action_btn.setObjectName("PrimaryButton")
        self.action_btn.setStyle(self.action_btn.style())

        if success:
            self.prog_bar.setValue(100)
            self.status_lbl.setText("Download completed successfully!")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #2E7D32; font-weight: 600;")
            if self.on_finish:
                self.on_finish()
        else:
            self.status_lbl.setText("Download cancelled or incomplete.")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #C62828;")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.cancel_event.set()
            self.worker.wait(2000)
        event.accept()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, config: Config, player=None, on_config_changed=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.player = player
        self.on_config_changed = on_config_changed

        self.setWindowTitle("ACDC - Settings")
        self.setWindowIcon(get_app_icon())
        self.setMinimumWidth(500)
        self.resize(520, 560)

        self._init_ui()

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        title_lbl = QtWidgets.QLabel("Animal Crossing Dynamic Clock")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")
        main_layout.addWidget(title_lbl)

        game_box = QtWidgets.QGroupBox(" Animal Crossing Game ")
        game_layout = QtWidgets.QVBoxLayout(game_box)
        game_layout.setContentsMargins(14, 16, 14, 16)
        game_layout.setSpacing(8)

        self.game_combo = QtWidgets.QComboBox()
        self.game_codes = [g["code"] for g in GAMES]
        for g in GAMES:
            self.game_combo.addItem(g["name"], g["code"])

        cur_game = self.config.get("game", "acnh")
        if cur_game in self.game_codes:
            self.game_combo.setCurrentIndex(self.game_codes.index(cur_game))

        self.game_status_lbl = QtWidgets.QLabel()
        self.game_status_lbl.setStyleSheet("font-size: 11px;")

        self.game_combo.currentIndexChanged.connect(self._update_game_download_status)
        game_layout.addWidget(self.game_combo)
        game_layout.addWidget(self.game_status_lbl)
        main_layout.addWidget(game_box)

        weather_box = QtWidgets.QGroupBox(" Weather Location ")
        weather_layout = QtWidgets.QVBoxLayout(weather_box)
        weather_layout.setContentsMargins(14, 16, 14, 16)
        weather_layout.setSpacing(8)

        city_row = QtWidgets.QHBoxLayout()
        city_row.setSpacing(8)
        city_row.addWidget(QtWidgets.QLabel("City:"))

        self.city_edit = QtWidgets.QLineEdit()
        self.city_edit.setPlaceholderText("Leave empty for automatic IP geolocation")
        self.city_edit.setText(self.config.get("city", ""))
        city_row.addWidget(self.city_edit, 1)

        self.detect_btn = QtWidgets.QPushButton("Auto-detect")
        self.detect_btn.clicked.connect(self._on_auto_detect)
        city_row.addWidget(self.detect_btn)
        weather_layout.addLayout(city_row)

        self.weather_preview_lbl = QtWidgets.QLabel("Current weather: Loading...")
        self.weather_preview_lbl.setStyleSheet("font-size: 11px; color: #888888;")
        weather_layout.addWidget(self.weather_preview_lbl)
        main_layout.addWidget(weather_box)

        audio_box = QtWidgets.QGroupBox(" Audio ")
        audio_layout = QtWidgets.QVBoxLayout(audio_box)
        audio_layout.setContentsMargins(14, 16, 14, 16)
        audio_layout.setSpacing(10)

        vol_row = QtWidgets.QHBoxLayout()
        vol_row.setSpacing(10)
        vol_row.addWidget(QtWidgets.QLabel("Volume:"))

        self.vol_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        initial_vol = int(self.config.get("volume", 75))
        self.vol_slider.setValue(initial_vol)

        self.vol_val_lbl = QtWidgets.QLabel(f"{initial_vol}%")
        self.vol_val_lbl.setFixedWidth(40)
        self.vol_val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.vol_slider.valueChanged.connect(self._on_volume_changed)
        vol_row.addWidget(self.vol_slider, 1)
        vol_row.addWidget(self.vol_val_lbl)
        audio_layout.addLayout(vol_row)

        self.roost_chk = QtWidgets.QCheckBox("The Roost Café (occasional Brewster's theme)")
        self.roost_chk.setChecked(bool(self.config.get("roost", False)))
        audio_layout.addWidget(self.roost_chk)
        main_layout.addWidget(audio_box)

        sys_box = QtWidgets.QGroupBox(" System ")
        sys_layout = QtWidgets.QVBoxLayout(sys_box)
        sys_layout.setContentsMargins(14, 16, 14, 16)
        sys_layout.setSpacing(8)

        self.autostart_chk = QtWidgets.QCheckBox("Launch automatically on computer startup")
        self.autostart_chk.setChecked(bool(self.config.get("autostart", False) or is_autostart_enabled()))
        sys_layout.addWidget(self.autostart_chk)

        self.notif_chk = QtWidgets.QCheckBox("Show notification on hour change")
        self.notif_chk.setChecked(bool(self.config.get("notifications", True)))
        sys_layout.addWidget(self.notif_chk)
        main_layout.addWidget(sys_box)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(10)

        self.folder_btn = QtWidgets.QPushButton("Open Folder")
        self.folder_btn.clicked.connect(self._on_open_folder)
        btn_row.addWidget(self.folder_btn)

        self.dl_btn = QtWidgets.QPushButton("Download...")
        self.dl_btn.clicked.connect(self._on_open_downloader)
        btn_row.addWidget(self.dl_btn)

        btn_row.addStretch()

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self.save_btn)

        main_layout.addLayout(btn_row)

        credit_lbl = QtWidgets.QLabel("Based on ACDP by oscie57 • Music © Nintendo")
        credit_lbl.setStyleSheet("font-size: 10px; color: #888888;")
        credit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(credit_lbl)

        self._update_game_download_status()
        self._refresh_weather_preview(self.config.get("city", ""))

    def _update_game_download_status(self):
        code = self.game_combo.currentData()
        if is_game_downloaded(code):
            self.game_status_lbl.setText("Music installed for this game")
            self.game_status_lbl.setStyleSheet("font-size: 11px; color: #2E7D32; font-weight: 600;")
        else:
            self.game_status_lbl.setText("Music not downloaded for this game")
            self.game_status_lbl.setStyleSheet("font-size: 11px; color: #C62828;")

    def _on_volume_changed(self, value):
        self.vol_val_lbl.setText(f"{value}%")
        if self.player:
            self.player.set_volume(value)

    def _refresh_weather_preview(self, city_name):
        def _fetch():
            w = get_current_weather(city_name, force=True)
            text = f"Current weather: {w.get('city', '')} - {w.get('temp', '')}, {w.get('description', '')}"
            QtCore.QMetaObject.invokeMethod(
                self.weather_preview_lbl,
                "setText",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, text)
            )
        threading.Thread(target=_fetch, daemon=True).start()

    def _on_auto_detect(self):
        self.weather_preview_lbl.setText("Detecting your location automatically...")
        def _detect():
            detected = detect_city()
            def _update():
                self.city_edit.setText(detected)
                self._refresh_weather_preview(detected)
            QtCore.QTimer.singleShot(0, _update)
        threading.Thread(target=_detect, daemon=True).start()

    def _on_open_folder(self):
        code = self.game_combo.currentData()
        open_music_folder(code)

    def _on_open_downloader(self):
        code = self.game_combo.currentData()
        dl_dialog = DownloadDialog(self.config, initial_game=code, on_finish=self._update_game_download_status, parent=self)
        dl_dialog.exec()

    def _on_save(self):
        code = self.game_combo.currentData()
        self.config.set("game", code)
        self.config.set("city", self.city_edit.text().strip())
        self.config.set("volume", self.vol_slider.value())
        self.config.set("roost", self.roost_chk.isChecked())
        self.config.set("notifications", self.notif_chk.isChecked())

        want_autostart = self.autostart_chk.isChecked()
        self.config.set("autostart", want_autostart)
        set_autostart(want_autostart)

        if self.on_config_changed:
            self.on_config_changed()

        self.accept()


_active_settings_dialog = None
_active_download_dialog = None


def open_settings_dialog(config: Config, player=None, on_config_changed=None):
    global _active_settings_dialog
    if _active_settings_dialog is not None and _active_settings_dialog.isVisible():
        _active_settings_dialog.raise_()
        _active_settings_dialog.activateWindow()
        return

    _active_settings_dialog = SettingsDialog(config, player=player, on_config_changed=on_config_changed)
    _active_settings_dialog.show()
    _active_settings_dialog.raise_()
    _active_settings_dialog.activateWindow()


def open_download_dialog(config: Config, initial_game: str = None, on_finish=None):
    global _active_download_dialog
    if _active_download_dialog is not None and _active_download_dialog.isVisible():
        _active_download_dialog.raise_()
        _active_download_dialog.activateWindow()
        return

    _active_download_dialog = DownloadDialog(config, initial_game=initial_game, on_finish=on_finish)
    _active_download_dialog.show()
    _active_download_dialog.raise_()
    _active_download_dialog.activateWindow()
