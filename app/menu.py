import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel,
    QFrame, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient,
    QBrush, QPainter, QPixmap
)
from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, DARK_BG, CARD_BG, BORDER, INPUT_BG
from componets.componets import PrimaryButton
from login import LoginPanel
from register import RegisterPanel
from Inicio import MainWindow, resource_path, sc         # ← importa la ventana principal (menú + crud/loans)


# ── Widget de fondo con gradiente ─────────────────────────────────────────────
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(DARK_BG))
        gradient.setColorAt(0.5, QColor(CARD_BG))
        gradient.setColorAt(1.0, QColor(DARK_BG))
        painter.fillRect(self.rect(), QBrush(gradient))

        glow = QColor(ACCENT)
        glow.setAlpha(22)
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-80, -80, 380, 380)

        glow2 = QColor(ACCENT)
        glow2.setAlpha(14)
        painter.setBrush(glow2)
        painter.drawEllipse(self.width() - 200, self.height() - 150, 350, 350)


# ── Panel selector inicial ────────────────────────────────────────────────────
class WelcomePanel(QWidget):
    def __init__(self, on_login, on_register):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        logo_pix = QPixmap(resource_path(os.path.join("imgs", "logo.png")))
        if not logo_pix.isNull():
            logo.setPixmap(logo_pix.scaledToHeight(130, Qt.SmoothTransformation))
        else:
            # Si no se encuentra el logo, se usa el texto como respaldo
            logo.setText("...")
            logo.setFont(QFont("Segoe UI", 46))
            logo.setStyleSheet(f"color: {ACCENT}; margin-bottom: 4px;")
        layout.addWidget(logo)

        title = QLabel("Bienvenid@")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.9px;")
        layout.addWidget(title)

        subtitle = QLabel("¿Qué deseas hacer hoy?")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        btn_login = PrimaryButton("  Iniciar Sesión")
        btn_login.clicked.connect(on_login)
        layout.addWidget(btn_login)

        # Separador
        sep_layout = QHBoxLayout()
        for _ in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet(f"color: {BORDER};")
            sep_layout.addWidget(line)
        sep_label = QLabel("  o  ")
        sep_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        sep_layout.addWidget(sep_label)
        for _ in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet(f"color: {BORDER};")
            sep_layout.addWidget(line)
        layout.addLayout(sep_layout)

        btn_register = QPushButton("  Crear Cuenta")
        btn_register.setFixedHeight(50)
        btn_register.setCursor(Qt.PointingHandCursor)
        btn_register.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_register.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER};
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {ACCENT};
                color: {ACCENT};
                background: rgba(255,115,7,0.08);
            }}
            QPushButton:pressed {{
                background: rgba(255,115,7,0.16);
            }}
        """)
        btn_register.clicked.connect(on_register)
        layout.addWidget(btn_register)

        footer = QLabel("Sistema de Gestión de Biblioteca Técnica Nº1")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Segoe UI", 8))
        footer.setStyleSheet(f"color: {TEXT_MUTED}; margin-top: 20px;")
        layout.addWidget(footer)


# ── Ventana Principal ─────────────────────────────────────────────────────────
class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autenticación")
        self.setFixedSize(sc(500), sc(850))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._crud_window = None    # ← referencia a la ventana CRUD
        self._build_ui()

    def _build_ui(self):
        root = GradientBackground()
        root.setFixedSize(sc(500), sc(850))
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)

        # Barra de título custom
        title_bar = QWidget()
        title_bar.setFixedHeight(36)
        title_bar.setStyleSheet("background: transparent;")
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(14, 0, 14, 0)

        app_name = QLabel("◈  Biblioteca Técnica Nº1")
        app_name.setFont(QFont("Segoe UI", 10, QFont.Bold))
        app_name.setStyleSheet(f"color: {ACCENT};")
        tb_layout.addWidget(app_name)
        tb_layout.addStretch()

        for symbol, action in [("─", self.showMinimized), ("✕", self.close)]:
            btn = QPushButton(symbol)
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.PointingHandCursor)

            btn.clicked.connect(action)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_MUTED};
                    border: none; font-size: 13px; border-radius: 6px;
                }}
                QPushButton:hover {{
                    background: rgba(58,36,16,0.10); color: {TEXT_PRIMARY};
                }}
            """)
            tb_layout.addWidget(btn)

        outer.addWidget(title_bar)

        # Tarjeta central
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 36, 20, 36)

        # Stack de paneles
        self.stack = QStackedWidget()
        self.welcome  = WelcomePanel(self._go_login, self._go_register)
        self.login    = LoginPanel(self._go_welcome, on_success=self._open_crud)  # ← conectado
        self.register = RegisterPanel(self._go_welcome, on_login=self._go_login)  # ← link ya corregido

        self.stack.addWidget(self.welcome)   # index 0
        self.stack.addWidget(self.login)     # index 1
        self.stack.addWidget(self.register)  # index 2

        card_layout.addWidget(self.stack)
        outer.addWidget(card, alignment=Qt.AlignCenter)
        outer.addStretch()

        card.setFixedWidth(sc(410))
        card.setMinimumHeight(sc(680))

    # ── Navegación ─────────────────────────────────────────────────────────────
    def _go_welcome(self):  self.stack.setCurrentIndex(0)
    def _go_login(self):    self.stack.setCurrentIndex(1)
    def _go_register(self): self.stack.setCurrentIndex(2)

    # ── Abrir Inicio.py (menú principal) tras login exitoso ─────────────────────
    def _open_crud(self, email: str):
        self.hide()                         # oculta la ventana de auth
        self._crud_window = MainWindow(
            initial_email=email,
            on_external_logout=self._on_logout   # al cerrar sesión vuelve al login de menu.py
        )
        self._crud_window.show()

    def _on_logout(self):
        # Vuelve al login limpiando los campos
        self.login.identity_input.clear()
        self.login.pass_input.clear()
        self.login.msg_label.setText("")
        self._go_login()
        self.show()

    # ── Arrastrar ventana ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Habilita escalado automático según el DPI del sistema operativo,
    # para que la interfaz se vea consistente en pantallas con distinto
    # factor de escala (125%, 150%, etc. en Windows).
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(DARK_BG))
    palette.setColor(QPalette.WindowText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base,            QColor(INPUT_BG))
    palette.setColor(QPalette.Text,            QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button,          QColor(CARD_BG))
    palette.setColor(QPalette.ButtonText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight,       QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())