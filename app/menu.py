import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel,
    QFrame, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient,
    QBrush, QPainter
)
from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, DARK_BG, CARD_BG, BORDER, INPUT_BG
from componets.componets import PrimaryButton
from login import LoginPanel
from register import RegisterPanel

# ── Widget de fondo con gradiente ─────────────────────────────────────────────
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#0D0D0F"))
        gradient.setColorAt(0.5, QColor("#12101C"))
        gradient.setColorAt(1.0, QColor("#0D1117"))
        painter.fillRect(self.rect(), QBrush(gradient))

        # Círculo decorativo superior
        painter.setBrush(QColor(108, 99, 255, 18))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-80, -80, 380, 380)

        # Círculo decorativo inferior
        painter.setBrush(QColor(78, 205, 196, 12))
        painter.drawEllipse(self.width() - 200, self.height() - 150, 350, 350)


# ── Panel selector inicial ────────────────────────────────────────────────────
class WelcomePanel(QWidget):
    def __init__(self, on_login, on_register):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ícono / Logo
        logo = QLabel("◈")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 46))
        logo.setStyleSheet(f"color: {ACCENT}; margin-bottom: 4px;")
        layout.addWidget(logo)

        # Título
        title = QLabel("Bienvenid@")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: -0.5px;")
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("¿Qué deseas hacer hoy?")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Botón Iniciar Sesión
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

        # Botón Registrarse
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
                background: rgba(108,99,255,0.08);
            }}
            QPushButton:pressed {{
                background: rgba(108,99,255,0.16);
            }}
        """)
        btn_register.clicked.connect(on_register)
        layout.addWidget(btn_register)

        # Footer
        footer = QLabel("Sistema de Gestión de Biblioteca Técnica Nº1")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(f"color: {TEXT_MUTED}; margin-top: 12px;")
        layout.addWidget(footer)




# ── Ventana Principal ─────────────────────────────────────────────────────────
class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autenticación")
        self.setFixedSize(420, 580)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self):
        root = GradientBackground()
        root.setFixedSize(420, 580)
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
                    background: rgba(255,255,255,0.08); color: {TEXT_PRIMARY};
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
        card_layout.setContentsMargins(36, 32, 36, 32)

        # Stack de paneles
        self.stack = QStackedWidget()
        self.welcome  = WelcomePanel(self._go_login, self._go_register)
        self.login    = LoginPanel(self._go_welcome)
        self.register = RegisterPanel(self._go_welcome, self._go_login) 

        self.stack.addWidget(self.welcome)   # index 0
        self.stack.addWidget(self.login)     # index 1
        self.stack.addWidget(self.register)  # index 2

        card_layout.addWidget(self.stack)
        outer.addWidget(card, alignment=Qt.AlignCenter)
        outer.addStretch()

        # Ajustar tamaño de tarjeta
        card.setFixedWidth(348)
        card.setMinimumHeight(460)

    # ── Navegación ─────────────────────────────────────────────────────────────
    def _go_welcome(self):  self.stack.setCurrentIndex(0)
    def _go_login(self):    self.stack.setCurrentIndex(1)
    def _go_register(self): self.stack.setCurrentIndex(2)

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