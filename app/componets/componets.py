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

# ── Campo de texto estilizado ─────────────────────────────────────────────────
class StyledInput(QLineEdit):
    def __init__(self, placeholder, echo_mode=QLineEdit.Normal):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setEchoMode(echo_mode)
        self.setFixedHeight(48)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_BG};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 0 16px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {ACCENT};
                background: #1A1A24;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """)


# ── Botón primario ────────────────────────────────────────────────────────────
class PrimaryButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._apply_style(ACCENT)

    def _apply_style(self, color):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 #9B5DE5
                );
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT_HOVER}, stop:1 #B07BFF
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A52D5, stop:1 #8A50C8
                );
            }}
        """)


# ── Botón de texto (link) ─────────────────────────────────────────────────────
class LinkButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {ACCENT};
                border: none;
                font-size: 13px;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {ACCENT_HOVER};
            }}
        """)
