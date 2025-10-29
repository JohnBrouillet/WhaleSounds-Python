import sys
import os
import logging
import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox

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
    # configure a file logger next to the executable so crashes can be diagnosed
    base = getattr(sys, 'frozen', False) and os.path.dirname(sys.executable) or os.path.abspath('.')
    app = QApplication(sys.argv)
    try:
        try:
            from qt_material import apply_stylesheet
            #apply_stylesheet(app, theme='light_blue.xml')
        except ImportError:
            pass
        win = MainApp()
        win.show()
        code = app.exec()
    except Exception as e:
        # Log full traceback to file
        tb = traceback.format_exc()
        logging.error("Unhandled exception during startup:\n%s", tb)
        # Show a friendly message box to the user
        try:
            QMessageBox.critical(None, "Erreur au démarrage", "Une erreur est survenue au démarrage. Voir whalesounds_error.log à côté de l'exécutable pour les détails.")
        except Exception:
            pass
        code = 1
    sys.exit(code)
