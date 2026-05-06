import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QPushButton, QLabel, QLineEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFont
)

from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS
from componets.componets import StyledInput, PrimaryButton



# ── Panel de Registro ─────────────────────────────────────────────────────────
class RegisterPanel(QWidget):
    def __init__(self, on_back, on_login=None):
        super().__init__()
        self._on_login_cb = on_login 
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

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

        title = QLabel("Crear Cuenta")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        sub = QLabel("Completa el formulario para registrarte")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 4px;")
        layout.addWidget(sub)

        for lbl_text, placeholder, echo in [
            ("Nombre completo",       "Ana García",          QLineEdit.Normal),
            ("Correo electrónico",    "ana@ejemplo.com",     QLineEdit.Normal),
            ("Contraseña",            "Mínimo 8 caracteres", QLineEdit.Password),
            ("Confirmar contraseña",  "Repite tu contraseña",QLineEdit.Password),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            layout.addWidget(lbl)
            inp = StyledInput(placeholder, echo)
            inp.setFixedHeight(44)
            layout.addWidget(inp)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setFont(QFont("Segoe UI", 10))
        self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        layout.addWidget(self.msg_label)

        btn = PrimaryButton("Registrarme →")
        btn.clicked.connect(self._on_register)
        layout.addWidget(btn)

        already = QLabel(f'¿Ya tienes cuenta? <a href="#" style="color:{ACCENT};">Inicia sesión</a>')
        already.setAlignment(Qt.AlignCenter)
        already.setFont(QFont("Segoe UI", 10))
        already.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: 4px;")
        already.setOpenExternalLinks(False)                          # ← no abrir browser
        already.linkActivated.connect(lambda: self._on_login_cb and self._on_login_cb())  # ← navegar
        layout.addWidget(already)
        
    def _on_register(self):
        self.msg_label.setStyleSheet(f"color: {SUCCESS}; font-size: 12px;")
        self.msg_label.setText("✓  Cuenta creada con éxito. ¡Bienvenido/a!")
