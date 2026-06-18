import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QPushButton, QLabel, QLineEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS
from componets.componets import StyledInput, PrimaryButton
from supabase_client import supabase


class RegisterPanel(QWidget):
    def __init__(self, on_back, on_login=None):
        super().__init__()
        self._on_login_cb = on_login
        self.inputs = {}
        fields = [
            ("name", "Nombre completo",       "Ana García",          QLineEdit.Normal),
            ("email", "Correo electrónico",    "ana@ejemplo.com",     QLineEdit.Normal),
            ("password", "Contraseña",            "Mínimo 8 caracteres", QLineEdit.Password),
            ("confirm", "Confirmar contraseña",  "Repite tu contraseña", QLineEdit.Password),
        ] 
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

        for key, lbl_text, placeholder, echo in fields:
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            layout.addWidget(lbl)
            
            inp = StyledInput(placeholder, echo)
            inp.setFixedHeight(44)
            layout.addWidget(inp)
            self.inputs[key] = inp 
        
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
        already.setOpenExternalLinks(False)
        already.linkActivated.connect(lambda: self._on_login_cb and self._on_login_cb())
        layout.addWidget(already)
        
    def _on_register(self):
        name = self.inputs["name"].text().strip()
        email = self.inputs["email"].text().strip()
        password = self.inputs["password"].text()
        confirm = self.inputs["confirm"].text()

        if not all([name, email, password, confirm]):
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            self.msg_label.setText("⚠ Todos los campos son obligatorios.")
            return

        if password != confirm:
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            self.msg_label.setText("⚠ Las contraseñas no coinciden.")
            return

        try:
            # 1. Registrar primero en el sistema de autenticación de Supabase
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": name}}
            })
            
            # 2. Extraer el ID único (UUID) que Supabase le asignó al usuario creado
            user_id = response.user.id
            
            # 3. Insertar MANUALMENTE en tu tabla de perfiles usando la estructura original
            profile_data = {
                "id": user_id,          # Llave primaria vinculada a auth.users
                "full_name": name,      # Nombre completo ingresado
                "email": email,         # Correo del usuario
            }
            
            supabase.table("profiles").insert(profile_data).execute()
            
            # Si todo sale bien, mostrar éxito
            self.msg_label.setStyleSheet(f"color: {SUCCESS}; font-size: 12px;")
            self.msg_label.setText("✓ ¡Cuenta y perfil creados con éxito!")
            self.msg_label.setText("Verifica tu correo para activar la cuenta, luego inicia sesión.")
            
        except Exception as e:
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            # Imprime en consola el error real por si llega a faltar apagar el RLS en la tabla profiles
            print("Error en registro:", str(e))
            self.msg_label.setText("⚠ Error al registrar el perfil en la base de datos.")
            self.msg_label.setText("⚠ Favor de consultar con el sosporte.")