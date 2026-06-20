import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from colors.colors import TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS
from componets.componets import StyledInput, PrimaryButton, LinkButton
from supabase_client import supabase


class LoginPanel(QWidget):
    def __init__(self, on_back, on_success=None):   
        super().__init__()
        self._on_success = on_success               
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
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

        title = QLabel("Iniciar Sesión")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        sub = QLabel("Ingresa tus credenciales para continuar")
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 6px;")
        layout.addWidget(sub)

        # 1. CAMBIO: Etiqueta mixta para Correo o Usuario
        lbl_identity = QLabel("Correo electrónico o Usuario")
        lbl_identity.setFont(QFont("Segoe UI", 10))
        lbl_identity.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_identity)
        
        # Campo de texto que aceptará ambos valores
        self.identity_input = StyledInput("usuario@ejemplo.com o usuario")
        layout.addWidget(self.identity_input)

        lbl_pass = QLabel("Contraseña")
        lbl_pass.setFont(QFont("Segoe UI", 10))
        lbl_pass.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_pass)

        # 2. CAMBIO: Contenedor para integrar el botón de ver contraseña dentro del input
        self.pass_container = QWidget()
        pass_layout = QHBoxLayout(self.pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(0)

        self.pass_input = StyledInput("••••••••", QLineEdit.Password)
        self.pass_input.setStyleSheet(self.pass_input.styleSheet() + "; padding-right: 32px;")
        pass_layout.addWidget(self.pass_input)

        # Botón de visibilidad (Icono de ojo 👁)
        self.toggle_pass_btn = QPushButton("👁")
        self.toggle_pass_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_pass_btn.setFixedWidth(30)
        self.toggle_pass_btn.setFixedHeight(40)  # Misma altura que el StyledInput
        
        # Estilo flotante sutil alineado a la derecha del input
        self.toggle_pass_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 14px;
                margin-left: -8px;  /* Lo posiciona visualmente "dentro" del campo */
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
            }}
        """)
        self.toggle_pass_btn.clicked.connect(self._toggle_password_visibility)
        pass_layout.addWidget(self.toggle_pass_btn)
        
        layout.addWidget(self.pass_container)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setFont(QFont("Segoe UI", 10))
        self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        layout.addWidget(self.msg_label)

        btn = PrimaryButton("Iniciar Sesión →")
        btn.clicked.connect(self._on_login)
        layout.addWidget(btn)

    # Lógica para alternar entre ver caracteres o asteriscos
    def _toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.Password:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pass_btn.setText("🙈")  # Icono opcional al mostrarse
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.toggle_pass_btn.setText("👁")

    def _on_login(self):
        identity = self.identity_input.text().strip()
        pwd = self.pass_input.text()

        if not identity or not pwd:
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            self.msg_label.setText("⚠ Por favor completa todos los campos.")
            return

        email = identity

        # 3. CAMBIO: Si la entrada no contiene un '@', asumimos que es un Username
        if "@" not in identity:
            try:
                # Consultamos la tabla 'profiles' buscando la coincidencia en la columna 'username'
                # NOTA: Cambia "profiles" o "username" si en tu BD tienen nombres diferentes.
                user_query = supabase.table("profiles").select("email").eq("username", identity).execute()
                
                if user_query.data and len(user_query.data) > 0:
                    email = user_query.data[0].get("email")
                else:
                    self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
                    self.msg_label.setText("⚠ El nombre de usuario no existe.")
                    return
            except Exception as e:
                self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
                self.msg_label.setText("⚠ Error al verificar el nombre de usuario.")
                return

        # 4. Intento de inicio de sesión final usando el correo recuperado/ingresado
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
            
            self.msg_label.setStyleSheet(f"color: {SUCCESS}; font-size: 12px;")
            self.msg_label.setText("✓ Iniciando sesión…")
            
            QTimer.singleShot(800, lambda: self._launch(response.user.email))
            
        except Exception as e:
            self.msg_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
            self.msg_label.setText("⚠ Credenciales incorrectas.")

    def _launch(self, email):
        if self._on_success:
            self._on_success(email)