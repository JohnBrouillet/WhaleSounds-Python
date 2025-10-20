import os
import sys
import yaml
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
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QScrollArea, QVBoxLayout, QGridLayout, QLabel, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class ImageDialog(QDialog):
    def __init__(self, img_path, animal_name, credits, parent=None):
        super().__init__(parent)
        self.setWindowTitle(animal_name)
        layout = QVBoxLayout(self)
        # Titre en haut, grand et centré
        name_label = QLabel(animal_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 16px;")
        layout.addWidget(name_label)

        abs_img_path = resource_path(img_path)
        pixmap = QPixmap(abs_img_path)
        img_label = QLabel()
        img_label.setPixmap(pixmap.scaledToWidth(500, Qt.SmoothTransformation))
        img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_label)

        credits_label = QLabel(str(credits))
        credits_label.setAlignment(Qt.AlignCenter)
        credits_label.setWordWrap(True)
        layout.addWidget(credits_label)

        # Ajout de la liste des fichiers audio (si présents)
        audio_layout = QVBoxLayout()
        audio_files = []
        if parent is not None and hasattr(parent, 'yaml_data'):
            for etage, animals in parent.yaml_data.items():
                if animal_name in animals:
                    info = animals[animal_name]
                    if isinstance(info, dict) and 'sons' in info:
                        sons = info['sons']
                        if isinstance(sons, str):
                            audio_files = [sons]
                        else:
                            audio_files = list(sons)
                    break
        if audio_files:
            from audio_player_widget import AudioPlayerWidget
            for audio_path in audio_files:
                full_path = os.path.join('data', audio_path.lstrip('/'))
                abs_path = resource_path(full_path)
                if os.path.exists(abs_path):
                    audio_layout.addWidget(AudioPlayerWidget(abs_path, self))
                else:
                    missing = QLabel(f"Fichier manquant : {audio_path}")
                    missing.setStyleSheet("color: #a00; font-style: italic;")
                    audio_layout.addWidget(missing)
            layout.addLayout(audio_layout)
        #btns = QDialogButtonBox(QDialogButtonBox.Close)
        #btns.rejected.connect(self.reject)
        #layout.addWidget(btns)

class SimpleViewer(QMainWindow):
    IMAGE_BOX_SIZE = 300  # Taille du carré contenant l'image
    IMAGE_MAX_SIZE = 270  # Taille max du côté de l'image
    def __init__(self, yaml_path):
        super().__init__()
        self.setWindowTitle("Lecteur simple - WhaleSounds")
        self.resize(1200, 800)
        abs_yaml_path = resource_path(yaml_path)
        with open(abs_yaml_path, 'r', encoding='utf-8') as f:
            self.yaml_data = yaml.safe_load(f)
        # Prépare les données par étage
        self.all_images = []  # (img_path, animal_name, credits, etage)
        self.etages = list(self.yaml_data.keys())
        for etage, animals in self.yaml_data.items():
            for animal, info in animals.items():
                if isinstance(info, dict) and 'image' in info:
                    img_path = os.path.join('data', info['image'].lstrip('/'))
                    credits = info.get('credits', '')
                    self.all_images.append((img_path, animal, credits, etage))

        # Layout principal : compteur + images + boutons filtres
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Compteur d'animaux affichés
        self.count_label = QLabel()
        self.count_label.setAlignment(Qt.AlignLeft)
        self.count_label.setStyleSheet("font-size: 16px; color: #888; margin: 8px 0 0 16px;")
        main_layout.addWidget(self.count_label)

        # Grille images (dans un scroll)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll, stretch=1)

        # Barre de boutons filtres
        from PySide6.QtWidgets import QHBoxLayout, QPushButton
        btn_bar = QHBoxLayout()
        btn_bar.setContentsMargins(8, 8, 8, 8)
        btn_bar.setSpacing(8)
        self.filter_buttons = []
        self._active_filter = None
        # Bouton "Tous"
        btn_style = (
            "border-radius: 20px; font-size: 20px; min-width: 120px; min-height: 48px; padding: 8px 24px;"
            "background: #232629; color: #fff; border: 2px solid #009688;"
        )
        all_btn = QPushButton("Tous")
        all_btn.setStyleSheet(btn_style)
        all_btn.clicked.connect(lambda: self._filter_images(None, all_btn))
        btn_bar.addWidget(all_btn)
        self.filter_buttons.append(all_btn)
        for etage in self.etages:
            btn = QPushButton(etage)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda checked, e=etage, b=btn: self._filter_images(e, b))
            btn_bar.addWidget(btn)
            self.filter_buttons.append(btn)
        main_layout.addLayout(btn_bar)

        self.setCentralWidget(main_widget)
        # Affiche toutes les images au départ
        self._filter_images(None, all_btn)

        self.showMaximized()


    def _filter_images(self, etage, btn=None):
        # Met à jour le bouton actif
        active_style = (
            "border-radius: 20px; font-size: 20px; min-width: 120px; min-height: 48px; padding: 8px 24px;"
            "background: #009688; color: #fff; border: 2px solid #009688;"
        )
        normal_style = (
            "border-radius: 20px; font-size: 20px; min-width: 120px; min-height: 48px; padding: 8px 24px;"
            "background: #232629; color: #fff; border: 2px solid #009688;"
        )
        if btn:
            for b in self.filter_buttons:
                b.setStyleSheet(normal_style)
            btn.setStyleSheet(active_style)
            self._active_filter = btn
        # Efface la grille
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        # Remonte la vue en haut du scroll
        self.scroll.verticalScrollBar().setValue(0)
        # Filtre les images
        if etage is None:
            images = self.all_images
        else:
            images = [img for img in self.all_images if img[3] == etage]
        # Affiche le compteur
        #self.count_label.setText(f"{len(images)} animaux affichés")
        col_count = 5
        row_count = (len(images) + col_count - 1) // col_count
        for col in range(col_count):
            self.grid.setColumnMinimumWidth(col, self.IMAGE_BOX_SIZE)
            self.grid.setColumnStretch(col, 0)
        for row in range(row_count):
            self.grid.setRowMinimumHeight(row, self.IMAGE_BOX_SIZE)
            self.grid.setRowStretch(row, 0)
        for idx, (img_path, animal, credits, etage_val) in enumerate(images):
            row, col = divmod(idx, col_count)
            label = QLabel()
            label.setFixedSize(self.IMAGE_BOX_SIZE, self.IMAGE_BOX_SIZE)
            label.setAlignment(Qt.AlignCenter)
            abs_img_path = resource_path(img_path)
            if os.path.exists(abs_img_path):
                pixmap = QPixmap(abs_img_path)
                scaled = pixmap.scaled(self.IMAGE_MAX_SIZE, self.IMAGE_MAX_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # Crée un fond blanc et centre l'image dessus
                final_pixmap = QPixmap(self.IMAGE_BOX_SIZE, self.IMAGE_BOX_SIZE)
                final_pixmap.fill(Qt.white)
                painter = None
                try:
                    from PySide6.QtGui import QPainter
                    painter = QPainter(final_pixmap)
                    x = (self.IMAGE_BOX_SIZE - scaled.width()) // 2
                    y = (self.IMAGE_BOX_SIZE - scaled.height()) // 2
                    painter.drawPixmap(x, y, scaled)
                finally:
                    if painter is not None:
                        painter.end()
                label.setPixmap(final_pixmap)
            else:
                label.setText("Image manquante")
            # Style de base + effet hover Qt-compatible
            label.setStyleSheet("""
                border: 2px solid transparent;
                background: #f8f8f8;
                border-radius: 8px;
            """)
            def enterEvent(e, l=label):
                l.setStyleSheet("border: 2px solid #009688; background: #e0f2f1; border-radius: 8px;")
            def leaveEvent(e, l=label):
                l.setStyleSheet("border: 2px solid transparent; background: #f8f8f8; border-radius: 8px;")
            label.enterEvent = enterEvent
            label.leaveEvent = leaveEvent
            label.mousePressEvent = self._make_click_handler(img_path, animal, credits)
            self.grid.addWidget(label, row, col)

    def _make_click_handler(self, img_path, animal, credits):
        def handler(event):
            dlg = ImageDialog(img_path, animal, credits, self)
            dlg.exec()
        return handler
