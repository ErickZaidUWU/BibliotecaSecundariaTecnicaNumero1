import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient,
    QBrush, QPainter, QPainterPath, QFontDatabase
)

from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS, DARK_BG, CARD_BG, BORDER, INPUT_BG, ACCENT_HOVER
from componets.componets import StyledInput, PrimaryButton, LinkButton

# ── Panel de Inicio de Sesión ─────────────────────────────────────────────────
class LoginPanel(QWidget):
    def __init__(self, on_back, on_success=None):   # ← NUEVO: on_success
        super().__init__()
        self._on_success = on_success               # ← guarda el callback
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        # Botón atrás
        back_btn = QPushButton("← Volver")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFont(QFont("Segoe UI", 10))
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: none; text-align: left; font-size: 12px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        back_btn.clicked.connect(on_back)
        layout.addWidget(back_btn)

        title = QLabel("Iniciar Sesión")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        sub = QLabel("Ingresa tus credenciales para continuar")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 8px;")
        layout.addWidget(sub)

        lbl_email = QLabel("Correo electrónico")
        lbl_email.setFont(QFont("Segoe UI", 10))
        lbl_email.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_email)
        self.email_input = StyledInput("usuario@ejemplo.com")
        layout.addWidget(self.email_input)

        lbl_pass = QLabel("Contraseña")
        lbl_pass.setFont(QFont("Segoe UI", 10))
        lbl_pass.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_pass)
        self.pass_input = StyledInput("••••••••", QLineEdit.Password)
        layout.addWidget(self.pass_input)

        forgot = LinkButton("¿Olvidaste tu contraseña?")
        forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: none; font-size: 12px; text-align: right;
            }}
            QPushButton:hover {{ color: {ACCENT}; }}
        """)
        layout.addWidget(forgot, alignment=Qt.AlignRight)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setFont(QFont("Segoe UI", 10))
        self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        layout.addWidget(self.msg_label)

        btn = PrimaryButton("Iniciar Sesión →")
        btn.clicked.connect(self._on_login)
        layout.addWidget(btn)

    def _on_login(self):
        email = self.email_input.text().strip()
        pwd   = self.pass_input.text()

        if not email or not pwd:
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            self.msg_label.setText("⚠  Por favor completa todos los campos.")
            return

        self.msg_label.setStyleSheet(f"color: {SUCCESS}; font-size: 12px;")
        self.msg_label.setText("✓  Iniciando sesión…")

        # ← Espera 800 ms y luego abre el CRUD
        QTimer.singleShot(800, lambda: self._launch(email))

    def _launch(self, email):
        if self._on_success:
            self._on_success(email)