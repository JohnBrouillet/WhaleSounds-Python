import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QIcon

class AudioPlayerWidget(QWidget):
    _active_player = None  # Pour garantir qu'un seul son joue à la fois

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)
        self.player.setSource(QUrl.fromLocalFile(os.path.abspath(audio_path)))
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self._update_time_label)

        layout = QHBoxLayout(self)
        # Chemin absolu vers le dossier d'icônes
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "whalesounds", "32x32")
        self.play_icon = QIcon(os.path.join(icon_path, "play.png"))
        self.pause_icon = QIcon(os.path.join(icon_path, "pause.png"))
        self.stop_icon = QIcon(os.path.join(icon_path, "stop.png"))
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.play_icon)
        self.play_btn.setFixedWidth(36)
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.stop_icon)
        self.stop_btn.setFixedWidth(36)
        self.stop_btn.clicked.connect(self.stop)
        layout.addWidget(self.stop_btn)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self._on_slider_moved)
        layout.addWidget(self.slider, stretch=1)
        self.time_label = QLabel("0:00")
        self.time_label.setFixedWidth(50)
        layout.addWidget(self.time_label)
        self.setLayout(layout)
        self._duration = 0
        self._user_is_moving_slider = False

    def toggle_play(self):
        ap = AudioPlayerWidget._active_player
        if ap and ap is not self:
            # Vérifie que l'objet n'est pas déjà détruit
            try:
                if hasattr(ap, 'stop'):
                    ap.stop()
            except RuntimeError:
                # L'objet a été détruit, on ignore
                AudioPlayerWidget._active_player = None
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.timer.stop()
        else:
            AudioPlayerWidget._active_player = self
            self.player.play()
            self.timer.start()

    def stop(self):
        self.player.stop()
        self.timer.stop()
        self.play_btn.setIcon(self.play_icon)
        if AudioPlayerWidget._active_player is self:
            AudioPlayerWidget._active_player = None

    def _on_position_changed(self, pos):
        if not self._user_is_moving_slider and self._duration > 0:
            self.slider.setValue(int(pos * 100 / self._duration))
        self._update_time_label()

    def _on_duration_changed(self, duration):
        self._duration = duration
        self.slider.setValue(0)
        self._update_time_label()

    def _on_slider_moved(self, value):
        if self._duration > 0:
            self._user_is_moving_slider = True
            self.player.setPosition(int(value * self._duration / 100))
            self._user_is_moving_slider = False

    def _on_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            self.timer.stop()
            self.slider.setValue(0)
            self._update_time_label()
            self.play_btn.setIcon(self.play_icon)
            if AudioPlayerWidget._active_player is self:
                AudioPlayerWidget._active_player = None
        elif state == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.pause_icon)
        else:
            self.play_btn.setIcon(self.play_icon)

    def _update_time_label(self):
        pos = self.player.position() // 1000
        mins = pos // 60
        secs = pos % 60
        self.time_label.setText(f"{mins}:{secs:02d}")
