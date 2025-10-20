import sys
import os

# Utilitaire pour accès aux ressources packagées avec PyInstaller
def resource_path(relative_path):
    # Cherche d'abord à côté de l'exe
    base = getattr(sys, 'frozen', False) and os.path.dirname(sys.executable) or os.path.abspath('.')
    abs_path = os.path.join(base, relative_path)
    if os.path.exists(abs_path):
        return abs_path
    # Fallback PyInstaller _MEIPASS (pour icons intégrés)
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return abs_path
import os
import numpy as np
import pyqtgraph as pg
import yaml
from whale_utils import load_audio, compute_spectrogram

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QListWidget,
    QSlider,
    QLabel,
    QSizePolicy,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl, Slot, QSize
from PySide6.QtGui import QPixmap, QIcon


class WhaleMainWindow(QMainWindow):
    def __init__(self, yaml_path: str):
        super().__init__()
        self.setWindowTitle("WhaleSounds - Python demo")
        # self.resize(1400, 800)
        from PySide6.QtGui import QFont
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("background: #f4f6fb;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # --- Ligne 1 : HBox (colonne gauche + waveform) ---
        top_row_widget = QWidget()
        top_row_layout = QHBoxLayout(top_row_widget)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(0)
        # Colonne gauche (grille 2x2)
        left_widget = QWidget()
        left_grid = QGridLayout(left_widget)
        # (0,0) : boutons étages
        self.btn_layout = QGridLayout()
        self.btn_layout.setSpacing(4)
        self.btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_widget = QWidget()
        btn_widget.setLayout(self.btn_layout)
        btn_widget.setContentsMargins(0, 0, 0, 0)
        left_grid.addWidget(btn_widget, 0, 0)
        # (0,1) : image + crédits
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMaximumHeight(400)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.credits_label = QLabel()
        self.credits_label.setWordWrap(True)
        info_widget.setStyleSheet('''
            background: #fff;
            border-radius: 20px;
            border: none;
            padding: 24px 18px 18px 18px;
            margin: 8px 8px 8px 8px;
            max-height: 420px;
        ''')
        self.image_label.setStyleSheet('border-radius: 16px; margin-bottom: -4px;')
        self.credits_label.setStyleSheet('color: #888; font-size: 12px; margin-top: -20px;')
        info_layout.addWidget(self.image_label)
        info_layout.addWidget(self.credits_label)
        left_grid.addWidget(info_widget, 0, 1)
        # (1,0) : QListWidget animaux
        self.animal_list = QListWidget()
        self.animal_list.setStyleSheet('''
            QListWidget {
                background: #fff;
                border-radius: 14px;
                padding: 10px 6px;
                font-size: 14px;
                color: #222;
                border: none;
            }
            QListWidget::item {
                border-radius: 10px;
                margin: 2px 0;
                padding: 0px 12px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
            QListWidget::item:hover {
                background: #f0f7fa;
                color: #1976d2;
            }
        ''')
        self.animal_list.currentRowChanged.connect(self.on_animal_selected)
        left_grid.addWidget(self.animal_list, 1, 0)
        # (1,1) : time_slider + boutons
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        # Label du nom de l'animal (centré, gras)
        name_row = QHBoxLayout()
        self.animal_name_label = QLabel("")
        self.animal_name_label.setAlignment(Qt.AlignCenter)
        self.animal_name_label.setStyleSheet("font-weight: 500; font-size: 17px; color: #222; letter-spacing: 0.5px; margin-bottom: 6px;")
        name_row.addWidget(self.animal_name_label)
        self.attachment_button = QPushButton()
        self.attachment_button.setIcon(QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "attachement.png"))))
        self.attachment_button.setIconSize(QSize(32, 32))
        self.attachment_button.setStyleSheet("border: none; background: transparent; margin-left: 8px;")
        self.attachment_button.setVisible(False)
        name_row.addWidget(self.attachment_button)
        controls_layout.addLayout(name_row)
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.sliderMoved.connect(self.on_slider_moved)
        controls_layout.addWidget(self.time_slider)
        nav_layout = QHBoxLayout()
        btn_style = '''
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 18px;
                min-width: 36px;
                min-height: 36px;
                max-width: 50px;
                max-height: 50px;
                color: #1976d2;
            }
            QPushButton:disabled {
                color: #bdbdbd;
            }
            QPushButton:hover {
                background: #e3f2fd;
                color: #1565c0;
            }
        '''
        self.attachment_button.setStyleSheet(btn_style)
        self.prev_button = QPushButton()
        self.prev_button.setIcon(QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "previous.png"))))
        self.prev_button.setToolTip("Fichier précédent")
        self.prev_button.setStyleSheet(btn_style)
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "next.png"))))
        self.next_button.setToolTip("Fichier suivant")
        self.next_button.setStyleSheet(btn_style)
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "play.png"))))
        self.play_button.setToolTip("Play/Pause")
        self.play_button.setStyleSheet(btn_style)
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "stop.png"))))
        self.stop_button.setToolTip("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(btn_style)

        ICONESIZE = 64
        self.play_button.setIconSize(QSize(ICONESIZE, ICONESIZE)) 
        self.stop_button.setIconSize(QSize(ICONESIZE, ICONESIZE))
        self.prev_button.setIconSize(QSize(ICONESIZE, ICONESIZE))
        self.next_button.setIconSize(QSize(ICONESIZE, ICONESIZE))

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.play_button)
        nav_layout.addWidget(self.stop_button)
        nav_layout.addWidget(self.next_button)
        controls_layout.addLayout(nav_layout)
        left_grid.addWidget(controls_widget, 1, 1)
        top_row_layout.addWidget(left_widget, stretch=1)
        self.waveform = pg.PlotWidget(title="Waveform")
        self.waveform.setLabel("bottom", "Time", units="s")
        self.waveform.setBackground("w")
        self.waveform.showGrid(x=False, y=True, alpha=0.5)
        top_row_layout.addWidget(self.waveform, stretch=1)
        main_layout.addWidget(top_row_widget, stretch=1)

        # --- Ligne 2 : spectrogramme sur toute la largeur ---
        # On place le spectrogramme et l'histogramme dans un QHBoxLayout
        spec_row_widget = QWidget()
        spec_row_layout = QHBoxLayout(spec_row_widget)
        spec_row_layout.setContentsMargins(0, 0, 0, 0)
        spec_row_layout.setSpacing(0)

        self.spectrogram = pg.PlotWidget()
        self.spectrogram.setBackground("w")
        self.spectrogram.setLabel("left", "Fréquence", units="Hz")
        self.spectrogram.setLabel("bottom", "Temps", units="s", autoSIPrefix=False)
        spec_row_layout.addWidget(self.spectrogram, stretch=10)
    # Menu contextuel colormap
        self.spectrogram.setContextMenuPolicy(Qt.CustomContextMenu)
        menu = self.spectrogram.getPlotItem().getViewBox().menu
        # Ajoute un sous-menu pour la colormap
        cmap_menu = menu.addMenu("Colormap")
        cmaps = pg.colormap.listMaps()  # gris pas très joli
        cmaps = [m for m in cmaps if not m.startswith("CET")]
        for cmap_name in cmaps:
            action = cmap_menu.addAction(cmap_name)
            action.triggered.connect(lambda checked, name=cmap_name: self.set_colormap(name))
  

        # Histogramme interactif
        self.spectro_hist = pg.HistogramLUTWidget()
        self.spectro_hist.setFixedWidth(120)
        spec_row_layout.addWidget(self.spectro_hist, stretch=0)
        main_layout.addWidget(spec_row_widget, stretch=2)

        # ImageItem pour le spectrogramme
        self.spectro_img = pg.ImageItem()
        self.spectrogram.addItem(self.spectro_img)
        self.spectro_hist.setImageItem(self.spectro_img)
        # Colormap viridis fixée une fois
        viridis_cmap = pg.colormap.get("viridis")
        self.viridis_lut = viridis_cmap.getLookupTable()
        self.spectro_img.setLookupTable(self.viridis_lut)
        # Applique la colormap viridis à l'histogramme interactif
        self.spectro_hist.gradient.setColorMap(viridis_cmap)
        self.spectro_hist.gradient.loadPreset("viridis")

        # curseurs
        self.cursor_wave = pg.InfiniteLine(angle=90, movable=False, pen="r")
        self.waveform.addItem(self.cursor_wave)
        self.cursor_spec = pg.InfiniteLine(angle=90, movable=False, pen="r")
        self.spectrogram.addItem(self.cursor_spec)


        # état
        self.current_animal = None
        self.current_index = 0
        self.current_etage = None
        self.waveform_curve = None

        # player
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)
        self.player.positionChanged.connect(self.update_cursors)
        self.player.playbackStateChanged.connect(self.update_button_text)

        # charger audio initial supprimé : sera chargé lors de la sélection d'un animal
        self.samples = None
        self.rate = None
        self.duration = None
        self.time = None
        self.waveform_curve = None

        abs_yaml_path = resource_path(yaml_path)
        with open(abs_yaml_path, "r", encoding="utf-8") as f:
            self.yaml_data = yaml.safe_load(f)

        self.etages = list(self.yaml_data.keys())
        # Ajoute les boutons d'étage sur 2 colonnes dynamiques
        for i, etage in enumerate(self.etages):
            b = QPushButton(etage)
            b.clicked.connect(lambda checked, e=etage: self.load_etage(e))
            row = i // 2
            col = i % 2
            self.btn_layout.addWidget(b, row, col)

        if self.etages:
            self.load_etage(self.etages[0])
            self.on_animal_selected(0)

        self.prev_button.clicked.connect(self.load_prev_file)
        self.next_button.clicked.connect(self.load_next_file)
        self.play_button.clicked.connect(self.toggle_play)
        self.stop_button.clicked.connect(self.stop_playback)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)  

        self.showMaximized()

        
    def set_colormap(self, cmap_name):
        cmap = pg.colormap.get(cmap_name)
        lut = cmap.getLookupTable()
        self.spectro_img.setLookupTable(lut)
        self.spectro_hist.gradient.setColorMap(cmap)
        self.spectro_hist.gradient.loadPreset(cmap_name)

    # --- logique ---
    def on_animal_selected(self, row):
        if row < 0:
            return
        animal_item = self.animal_list.item(row)
        if not animal_item:
            return
        animal = animal_item.text()
        self.animal_name_label.setText(animal)
        etage = self.current_etage
        data = self.yaml_data.get(etage, {})
        info = data.get(animal, {})
        # PDF attachement
        fichier_pdf = None
        if isinstance(info, dict):
            fichier_pdf = info.get("fichier")
        if fichier_pdf:
            abs_pdf_path = resource_path(os.path.join("data", fichier_pdf.lstrip("/")))
            self.attachment_button.setVisible(True)
            self.attachment_button.clicked.disconnect()
            def open_pdf():
                from PySide6.QtWidgets import QDialog, QVBoxLayout
                from PySide6.QtPdfWidgets import QPdfView
                from PySide6.QtPdf import QPdfDocument
                dlg = QDialog(self)
                dlg.setWindowTitle(f"PDF - {animal}")
                layout = QVBoxLayout(dlg)
                pdf_view = QPdfView()
                pdf_doc = QPdfDocument()
                pdf_doc.load(abs_pdf_path)
                pdf_view.setDocument(pdf_doc)
                layout.addWidget(pdf_view)
                dlg.resize(800, 900)
                dlg.exec()
            self.attachment_button.clicked.connect(open_pdf)
        else:
            self.attachment_button.setVisible(False)

        # sons
        files = info.get("sons", []) if isinstance(info, dict) else []
        self.select_animal(animal, files)

        # image
        img_rel = info.get("image")
        if img_rel:
            img_path = os.path.join("data", img_rel.lstrip("/"))
            abs_img_path = resource_path(img_path)
            if os.path.exists(abs_img_path):
                pixmap = QPixmap(abs_img_path)
                self.image_label.setPixmap(
                    pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            else:
                self.image_label.clear()
        # credits
        credits = info.get("credits", "")
        self.credits_label.setText(str(credits))

    def show_spectrogram(self, nfft=1024, noverlap=512):
        S_db, shapes = compute_spectrogram(self.samples, nfft, noverlap)
        # Affichage de l'image dans l'ImageItem
        self.spectro_img.setImage(S_db, autoLevels=True)
        self.spectro_img.setLevels([S_db.min(), S_db.max()])

        # Axes et ticks
        duration = (
            self.duration
            if hasattr(self, "duration") and self.duration
            else len(self.samples) / self.rate
        )
        n_cols = shapes[1]
        n_rows = shapes[0]
        self.spectrogram.setLimits(xMin=0, xMax=n_cols, yMin=0, yMax=n_rows)
        self.spectrogram.setLabel("left", "Fréquence", units="Hz")
        self.spectrogram.setLabel("bottom", "Temps", units="s", autoSIPrefix=False)
        # Force la vue à s'adapter à la nouvelle image
        self.spectrogram.getViewBox().enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        self.spectrogram.getViewBox().setRange(xRange=(0, n_cols), yRange=(0, n_rows), padding=0)

        # Ticks temporels
        tick_count = 10
        x_ticks = []
        for i in range(tick_count + 1):
            t = i * duration / tick_count
            col = int(i * n_cols / tick_count)
            x_ticks.append((col, f"{t:.1f}"))
        self.spectrogram.getAxis("bottom").setTicks([x_ticks])

        # Ticks de fréquences réelles en Y
        if hasattr(self, "rate") and self.rate:
            freqs = np.fft.rfftfreq(nfft, d=1.0/self.rate)
            y_tick_count = 8
            y_ticks = []
            for i in range(y_tick_count + 1):
                idx = int(i * (len(freqs)-1) / y_tick_count)
                freq = freqs[idx]
                y_ticks.append((idx, f"{freq:.0f}"))
            self.spectrogram.getAxis("left").setTicks([y_ticks])

    def select_animal(self, animal, files):
        if isinstance(files, str):
            files = [files]
        self.current_animal = animal
        self.current_files = files
        self.current_index = 0
        if self.current_files:
            self.load_current_file()
        self.update_nav_buttons()

    def load_current_file(self):
        path = os.path.join("data", self.current_files[self.current_index].lstrip("/"))
        self.samples, self.rate, self.duration, self.time = load_audio(path)
        if self.waveform_curve:
            self.waveform_curve.setData(self.time, self.samples)
        else:
            self.waveform_curve = self.waveform.plot(self.time, self.samples, pen="c")
        self.show_spectrogram()
        if not self.cursor_wave.scene():
            self.waveform.addItem(self.cursor_wave)
        if not self.cursor_spec.scene():
            self.spectrogram.addItem(self.cursor_spec)
        self.time_slider.setRange(0, int(self.duration * 1000))
        self.time_slider.setValue(0)
        self.play_file(path)

    def update_nav_buttons(self):
        n = len(self.current_files)
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < n - 1)

    def load_prev_file(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_file()
            self.update_nav_buttons()

    def load_next_file(self):
        if self.current_index < len(self.current_files) - 1:
            self.current_index += 1
            self.load_current_file()
            self.update_nav_buttons()

    def load_etage(self, etage):
        data = self.yaml_data.get(etage, {})
        if not isinstance(data, dict):
            return
        self.animal_list.blockSignals(True)
        self.animal_list.clear()
        for k in data.keys():
            self.animal_list.addItem(str(k))
        self.animal_list.blockSignals(False)
        self.current_etage = etage

    @Slot(int)
    def update_cursors(self, pos_ms):
        if abs(self.time_slider.value() - pos_ms) > 50:
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(pos_ms)
            self.time_slider.blockSignals(False)
        t = pos_ms / 1000.0
        self.cursor_wave.setValue(t)
        # Utilise directement self.spectro_img
        img_item = self.spectro_img
        n_cols = img_item.image.shape[1] if img_item.image is not None else 1
        total_time = (
            len(self.samples) / self.rate
            if self.samples is not None and self.rate
            else 1
        )
        col = t / total_time * (n_cols - 1)
        x0, x1 = img_item.boundingRect().left(), img_item.boundingRect().right()
        cursor_x = x0 - col / (n_cols - 1) * (x0 - x1) if n_cols > 1 else x0
        self.cursor_spec.setValue(cursor_x)

    @Slot()
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
        # Le bouton stop devient cliquable dès qu'on a appuyé sur play
        self.stop_button.setEnabled(True)

    @Slot()
    def stop_playback(self):
        self.player.stop()
        self.stop_button.setEnabled(False)

    @Slot()
    def update_button_text(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "pause.png")))
            )
        else:
            self.play_button.setIcon(
                QIcon(resource_path(os.path.join("icons", "whalesounds", "32x32", "play.png")))
            )

    def play_file(self, path):
        self.player.setSource(QUrl.fromLocalFile(path))

    @Slot(int)
    def on_slider_moved(self, pos_ms):
        was_playing = self.player.playbackState() == QMediaPlayer.PlayingState
        self.player.setPosition(pos_ms)
        self.update_cursors(pos_ms)
        if was_playing:
            self.player.play()


