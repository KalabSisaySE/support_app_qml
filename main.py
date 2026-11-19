"""Entry point of the Macrosoft Support desktop application."""

import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from support_app import app_config
from support_app.backend import MacrosoftBackend
from support_app.logging_setup import configure_logging, get_logger
from support_app.version import __version__

logger = get_logger(__name__)


def main():
    """Create the Qt application, expose the backend and load the QML UI."""
    configure_logging()
    logger.info(
        "Macrosoft Support %s starting (name=%s, exe=%s)",
        __version__, app_config.NAME, app_config.EXE_NAME,
    )

    # 1. Set the desired Qt Quick Controls style before creating the application
    QQuickStyle.setStyle("Fusion")  # Options: "Basic", "Fusion", "Material", "Imagine", etc.

    # 2. Initialize the application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # 3. Get Context
    backend = MacrosoftBackend()

    engine.rootContext().setContextProperty("backend", backend)

    # 4. Set App Extra Info
    app.setOrganizationName("Macrosoft s.r.o")
    app.setOrganizationDomain("https://online.macrosoft.sk/")

    # 5. Load QML File
    qml_file = os.path.join(os.path.dirname(__file__), "qml/main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    logger.info("QML directory: %s", os.path.dirname(__file__))
    logger.info("QML entry point: %s", __file__)

    app.aboutToQuit.connect(backend.cleanup)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
