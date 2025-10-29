from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


# Nouvelle Card verticale, très épurée
class HomeCard(QPushButton):
    CARD_WIDTH = 500
    CARD_HEIGHT = 320
    IMG_HEIGHT = 240
    def __init__(self, image_path, title, description, on_click, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        # Image en haut, centrée
        img = QLabel()
        img.setPixmap(QPixmap(image_path).scaled(self.CARD_WIDTH, self.IMG_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img.setAlignment(Qt.AlignCenter)
        img.setFixedHeight(self.IMG_HEIGHT)
        img.setStyleSheet('margin: 15px 15px 0px 15px;')
        layout.addWidget(img)
        # Titre centré
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet('font-size: 22px; font-weight: 700; color: #232629; margin: 3px 0 8px 0;')
        layout.addWidget(title_lbl)
        # Description centrée
        desc_lbl = QLabel(description)
        desc_lbl.setAlignment(Qt.AlignCenter)
        #desc_lbl.setStyleSheet('font-size: 15px; color: #555; margin: 0 18px 0 18px;')
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        layout.addStretch(1)
        self.clicked.connect(on_click)

class HomePage(QWidget):
    def __init__(self, on_simple, on_complet, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: #f4f6fb;')
    # Taille d'accueil = 2 cards + espacement + marges
        card_w = HomeCard.CARD_WIDTH
        card_h = HomeCard.CARD_HEIGHT
        spacing = 48
        margin = 40
        total_w = 2 * card_w + spacing + 2 * margin
        total_h = card_h + 2 * margin


        main = QVBoxLayout()
        main.setAlignment(Qt.AlignCenter)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        title = QLabel('Bienvenue sur WhaleSounds')
        title.setStyleSheet('font-size: 36px; font-weight: bold; color: #222; margin-bottom: 48px; margin-top: 20px;')
        title.setAlignment(Qt.AlignCenter)
        main.addWidget(title)
        cards = QHBoxLayout()
        cards.setSpacing(48)
        # Deux cards côte à côte, taille fixe et alignement parfait
        from whalemainwindow import resource_path
        simple = HomeCard(resource_path('data/baleine_bleue/images/baleine_bleue.jpg'), 'Mode simple', "Parcourez toutes les images d'espèces et écoutez leurs sons en mode galerie.", on_simple)
        complet = HomeCard(resource_path('data/baleine_a_bosse/images/humpback.jpg'), 'Mode complet', "Explorez toutes les fonctionnalités avancées d'analyse et de visualisation sonore.", on_complet)
        cards.addStretch(1)
        cards.addWidget(simple)
        cards.addWidget(complet)
        cards.addStretch(1)
        main.addLayout(cards)
        main.addStretch(1)
        self.setLayout(main)

        self.setMinimumSize(total_w, total_h)
        self.resize(total_w, total_h)