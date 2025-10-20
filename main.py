import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from home_page import HomePage


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhaleSounds")
        #self.resize(1400, 900)
        from whalemainwindow import resource_path
        self.data_file = resource_path("data/whale_data.yml")
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        # Page d'accueil
        self.home = HomePage(self.open_simple, self.open_complet)
        self.tabs.addTab(self.home, "Accueil")
        self.simple_viewer = None
        self.complet_viewer = None

    def open_simple(self):
        if not self.simple_viewer:
            from simple_viewer import SimpleViewer
            self.simple_viewer = SimpleViewer(self.data_file)
            self.tabs.addTab(self.simple_viewer, "Mode simple")
        self.tabs.setCurrentWidget(self.simple_viewer)
        self.showMaximized()

    def open_complet(self):
        if not self.complet_viewer:
            from whalemainwindow import WhaleMainWindow
            self.complet_viewer = WhaleMainWindow(self.data_file)
            self.tabs.addTab(self.complet_viewer, "Mode complet")
        self.tabs.setCurrentWidget(self.complet_viewer)
        self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from qt_material import apply_stylesheet
        #apply_stylesheet(app, theme='light_blue.xml')
    except ImportError:
        pass
    win = MainApp()
    win.show()
    sys.exit(app.exec())
