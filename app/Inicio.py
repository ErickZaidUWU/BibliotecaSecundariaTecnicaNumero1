import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFrame,
    QGraphicsDropShadowEffect, QStackedWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QLinearGradient,
    QBrush, QPainter, QPixmap
)

from colors.colors import (
    TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS,
    DARK_BG, CARD_BG, BORDER, INPUT_BG, ACCENT_HOVER
)
from login import LoginPanel
from crud import LibraryCRUD
from loans import LibraryLoans


# ─────────────────────────────────────────────────────────────────────────────
# Índices del QStackedWidget
# ─────────────────────────────────────────────────────────────────────────────
PAGE_LOGIN = 0
PAGE_MENU  = 1
PAGE_CRUD  = 2
PAGE_LOANS = 3


def resource_path(filename):
    """
    Devuelve la ruta absoluta de un recurso (ej. imgs/logo.jpg) ubicado junto
    a este script. Si usas PyInstaller, esto también funciona empaquetado
    con --add-data, ya que respeta sys._MEIPASS cuando existe.

    Ejemplo para incluir la carpeta imgs al compilar con PyInstaller:
        --add-data "imgs:imgs"        (Linux/Mac)
        --add-data "imgs;imgs"        (Windows)
    """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)


# ── Fondo con gradiente ───────────────────────────────────────────────────────
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
        painter.drawEllipse(-80, -80, 420, 420)
        glow2 = QColor(ACCENT)
        glow2.setAlpha(14)
        painter.setBrush(glow2)
        painter.drawEllipse(self.width() - 250, self.height() - 200, 400, 400)


# ── Tarjeta de módulo clickeable ──────────────────────────────────────────────
class ModuleCard(QFrame):
    def __init__(self, icon, title, description, on_click, parent=None):
        super().__init__(parent)
        self.on_click = on_click
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(130)
        self._apply_style(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 26))
        icon_lbl.setFixedWidth(40)

        top_row.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        arrow = QLabel("→")
        arrow.setFont(QFont("Segoe UI", 14))
        arrow.setStyleSheet(f"color: {ACCENT};")
        top_row.addWidget(arrow)

        layout.addLayout(top_row)

        desc_lbl = QLabel(description)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

    def _apply_style(self, hovered):
        border_color = ACCENT if hovered else BORDER
        bg = "rgba(255,115,7,0.10)" if hovered else f"{CARD_BG}"
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border_color};
                border-radius: 14px;
            }}
        """)

    def enterEvent(self, event):  self._apply_style(True)
    def leaveEvent(self, event):  self._apply_style(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click()


# ── Panel del Menú (pantalla completa, sin tarjeta) ───────────────────────────
class MenuPanel(GradientBackground):
    def __init__(self, user_email, on_go_loans, on_go_crud, on_logout):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(0)

        # Header (logo + nombre a la izquierda, correo + cerrar sesión a la derecha)
        header = QHBoxLayout()
        header.setSpacing(14)

        # Logo (antes del nombre de la escuela)
        logo_lbl = QLabel()
        logo_pix = QPixmap(resource_path(os.path.join("imgs", "logo.png")))
        if not logo_pix.isNull():
            logo_lbl.setPixmap(
                logo_pix.scaledToHeight(200, Qt.SmoothTransformation)
            )
            header.addWidget(logo_lbl, 0, Qt.AlignVCenter)
        # Si no se encuentra el logo simplemente no se muestra nada.

        brand = QLabel(f"Escuela Secundaria Técnica No: 1 \nÁndres Álvaro García")
        brand.setFont(QFont("Segoe UI", 42, QFont.Bold))
        brand.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header.addWidget(brand, 0, Qt.AlignVCenter)
        header.addStretch()

        user_pill = QFrame()
        user_pill.setStyleSheet(f"""
            QFrame {{
                background: {ACCENT};
                border: 1px solid {ACCENT_HOVER};
                border-radius: 20px;
            }}
        """)
        pill_layout = QHBoxLayout(user_pill)
        pill_layout.setContentsMargins(12, 6, 12, 6)
        pill_layout.setSpacing(8)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
        pill_layout.addWidget(dot)
        email_lbl = QLabel(user_email)
        email_lbl.setFont(QFont("Segoe UI", 10))
        email_lbl.setStyleSheet("color: #FFFFFF;")
        pill_layout.addWidget(email_lbl)
        header.addWidget(user_pill, 0, Qt.AlignVCenter)

        logout_btn = QPushButton("Cerrar sesión")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFont(QFont("Segoe UI", 10))
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: #FFFFFF;
                border: 1px solid {ACCENT_HOVER}; border-radius: 8px;
                padding: 6px 14px; font-size: 12px; margin-left: 10px;
            }}
            QPushButton:hover {{ background: {ERROR}; border-color: {ERROR}; }}
        """)
        logout_btn.clicked.connect(on_logout)
        header.addWidget(logout_btn, 0, Qt.AlignVCenter)

        layout.addLayout(header)
        layout.addSpacing(60)

        greeting = QLabel("¡Bienvenido de nuevo!")
        greeting.setFont(QFont("Segoe UI", 30, QFont.Bold))
        greeting.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(greeting)

        subtitle = QLabel("¿Qué módulo deseas gestionar hoy?")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; margin-bottom: 32px;")
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"border: none; border-top: 1px solid {BORDER};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        layout.addSpacing(30)

        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(18)

        crud_card = ModuleCard(
            icon="📚",
            title="Catálogo de Libros",
            description="Agrega, edita y elimina libros del inventario. Consulta Cantidad, categorías y autores disponibles.",
            on_click=on_go_crud
        )
        cards_layout.addWidget(crud_card)

        loans_card = ModuleCard(
            icon="📝",
            title="Préstamos",
            description="Registra y administra los préstamos activos. Controla fechas de devolución y alumnos con libros vencidos.",
            on_click=on_go_loans
        )
        cards_layout.addWidget(loans_card)

        layout.addLayout(cards_layout)
        layout.addStretch()

        footer = QLabel("Sistema de Gestión de Biblioteca Tecnica No: 1")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)


# ── Página de Login centrada ───────────────────────────────────────────────────
class LoginPage(GradientBackground):
    """Envuelve LoginPanel en una tarjeta centrada sobre el fondo."""
    def __init__(self, on_success):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 100))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(0)

        self._panel = LoginPanel(on_back=lambda: None, on_success=on_success)
        # Ocultar botón "← Volver" (no hay pantalla previa en este flujo)
        back_item = self._panel.layout().itemAt(0)
        if back_item and back_item.widget():
            back_item.widget().hide()

        card_layout.addWidget(self._panel)
        outer.addWidget(card)

    def clear(self):
        self._panel.email_input.clear()
        self._panel.pass_input.clear()
        self._panel.msg_label.setText("")


# ── Wrapper: extrae el contenido de un QMainWindow como QWidget embebible ─────
class EmbeddedView(QWidget):
    """
    Instancia un QMainWindow (LibraryCRUD / LibraryLoans), roba su centralWidget
    y lo presenta dentro de este QWidget junto con una barra de navegación propia.
    El QMainWindow nunca llega a mostrarse como ventana separada.
    """
    def __init__(self, main_window_cls, user_email, on_back, on_logout, parent=None):
        super().__init__(parent)
        self._on_back   = on_back
        self._on_logout = on_logout

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Barra superior con navegación ─────────────────────────────────────
        nav_bar = QWidget()
        nav_bar.setFixedHeight(54)
        nav_bar.setStyleSheet(f"background: {ACCENT}; border-bottom: 1px solid {ACCENT_HOVER};")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(16, 0, 16, 0)
        nav_layout.setSpacing(10)

        back_btn = QPushButton("←  Menú")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        back_btn.setFixedHeight(34)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.14); color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.45); border-radius: 9px;
                padding: 4px 20px; font-size: 14px;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.26); border-color: #FFFFFF; }}
        """)
        back_btn.clicked.connect(on_back)
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()

        user_lbl = QLabel(f"● {user_email}")
        user_lbl.setFont(QFont("Segoe UI", 9))
        user_lbl.setStyleSheet("color: rgba(255,255,255,0.9); margin-right: 8px;")
        nav_layout.addWidget(user_lbl)

        logout_btn = QPushButton("Cerrar sesión")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.14); color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.45); border-radius: 8px;
                font-size: 11px; padding: 4px 12px;
            }}
            QPushButton:hover {{ background: {ERROR}; border-color: {ERROR}; }}
        """)
        logout_btn.clicked.connect(on_logout)
        nav_layout.addWidget(logout_btn)

        root_layout.addWidget(nav_bar)

        # ── Instanciar el QMainWindow y robar su centralWidget ────────────────
        # on_logout aquí cierra la ventana hija (no aplica), lo redirigimos
        self._win = main_window_cls(user_email=user_email, on_logout=on_logout)
        self._win._build_ui()                    # asegura que el widget esté construido
        content = self._win.centralWidget()
        content.setParent(self)                  # re-parentar al EmbeddedView
        root_layout.addWidget(content)

    def reload(self):
        """Recarga los datos al entrar a la vista."""
        try:
            self._win._load_data_from_supabase()
            self._win._refresh_table()
            self._win._refresh_stats()
        except Exception:
            pass


# ── Ventana única de la aplicación ────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, initial_email=None, on_external_logout=None):
        super().__init__()
        self.setWindowTitle("Secundaria Tecnica No: 1")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos    = None
        self._user_email  = None
        self._on_external_logout = on_external_logout

        # Vistas embebidas (se crean al hacer login para tener el email)
        self._crud_view  = None
        self._loans_view = None

        # ── Root widget ───────────────────────────────────────────────────────
        self._root = GradientBackground()
        root_layout = QVBoxLayout(self._root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Barra de título custom (drag + minimizar/maximizar/cerrar)
        root_layout.addWidget(self._build_title_bar())

        # ── Stack de páginas ──────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        root_layout.addWidget(self._stack)

        # PAGE_LOGIN
        self._login_page = LoginPage(on_success=self._on_login_success)
        self._stack.addWidget(self._login_page)          # 0

        # PAGE_MENU (placeholder; se reconstruye con el email)
        self._menu_page = QWidget()
        self._stack.addWidget(self._menu_page)           # 1

        # PAGE_CRUD y PAGE_LOANS se añaden en _build_inner_views()
        # Reservamos dos slots vacíos para que los índices sean fijos
        self._crud_placeholder  = QWidget()
        self._loans_placeholder = QWidget()
        self._stack.addWidget(self._crud_placeholder)    # 2
        self._stack.addWidget(self._loans_placeholder)   # 3

        self.setCentralWidget(self._root)

        if initial_email:
            # Ya viene autenticado desde menu.py: saltar el login y abrir el menú
            self._on_login_success(initial_email)
        else:
            # Tamaño inicial: compacto para la pantalla de login
            self._set_login_size()

    # ─────────────────────────────────────────────────────────────────────────
    # Barra de título
    # ─────────────────────────────────────────────────────────────────────────
    def _build_title_bar(self):
        bar = QWidget()
        bar.setFixedHeight(34)
        bar.setStyleSheet("background: transparent;")
        bar.mousePressEvent   = self._bar_press
        bar.mouseMoveEvent    = self._bar_move
        bar.mouseReleaseEvent = self._bar_release

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(4)

        lbl = QLabel("Tecnica No: 1")
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(lbl)
        layout.addStretch()

        for label, slot, hover in [
            ("─", self.showMinimized, TEXT_MUTED),
            ("□", self._toggle_max,   TEXT_MUTED),
            ("✕", self.close,         ERROR),
        ]:
            btn = QPushButton(label)
            btn.setFixedSize(28, 22)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_MUTED};
                    border: none; border-radius: 4px;
                }}
                QPushButton:hover {{ background: rgba(58,36,16,0.10); color: {hover}; }}
            """)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        return bar

    def _toggle_max(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def _bar_press(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def _bar_move(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def _bar_release(self, e):
        self._drag_pos = None

    # ─────────────────────────────────────────────────────────────────────────
    # Tamaño de ventana
    # ─────────────────────────────────────────────────────────────────────────
    def _set_login_size(self):
        """Tamaño compacto para Login/Menú/Register."""
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)   # sin límite
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 860, 600
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)

    def _set_fullscreen_size(self):
        """Pantalla completa para CRUD / Loans."""
        self.showMaximized()

    # ─────────────────────────────────────────────────────────────────────────
    # Construir vistas embebidas (solo una vez, tras conocer el email)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_inner_views(self, email):
        # CRUD
        crud_view = EmbeddedView(
            main_window_cls=LibraryCRUD,
            user_email=email,
            on_back=self._go_menu,
            on_logout=self._on_logout,
        )
        self._stack.removeWidget(self._crud_placeholder)
        self._stack.insertWidget(PAGE_CRUD, crud_view)
        self._crud_view = crud_view

        # Loans
        loans_view = EmbeddedView(
            main_window_cls=LibraryLoans,
            user_email=email,
            on_back=self._go_menu,
            on_logout=self._on_logout,
        )
        self._stack.removeWidget(self._loans_placeholder)
        self._stack.insertWidget(PAGE_LOANS, loans_view)
        self._loans_view = loans_view

    # ─────────────────────────────────────────────────────────────────────────
    # Navegación
    # ─────────────────────────────────────────────────────────────────────────
    def _on_login_success(self, email):
        self._user_email = email

        # Reconstruir menú con el email real
        old_menu = self._menu_page
        self._menu_page = MenuPanel(
            user_email=email,
            on_go_loans=self._go_loans,
            on_go_crud=self._go_crud,
            on_logout=self._on_logout,
        )
        self._stack.removeWidget(old_menu)
        self._stack.insertWidget(PAGE_MENU, self._menu_page)
        old_menu.deleteLater()

        # Construir vistas internas si es la primera vez
        if self._crud_view is None:
            self._build_inner_views(email)

        self._go_menu()

    def _go_menu(self):
        self._stack.setCurrentIndex(PAGE_MENU)
        self._set_fullscreen_size()

    def _go_crud(self):
        self._stack.setCurrentIndex(PAGE_CRUD)
        if self._crud_view:
            self._crud_view.reload()
        self._set_fullscreen_size()

    def _go_loans(self):
        self._stack.setCurrentIndex(PAGE_LOANS)
        if self._loans_view:
            self._loans_view.reload()
        self._set_fullscreen_size()

    def _on_logout(self):
        self._crud_view  = None
        self._loans_view = None

        if self._on_external_logout:
            # Esta ventana fue abierta desde menu.py tras un login externo:
            # cerrar Inicio.py y devolver el control a la pantalla de menu.py
            self.close()
            self._on_external_logout()
            return

        # Restaurar placeholders para el próximo login
        self._crud_placeholder  = QWidget()
        self._loans_placeholder = QWidget()
        self._stack.insertWidget(PAGE_CRUD,  self._crud_placeholder)
        self._stack.insertWidget(PAGE_LOANS, self._loans_placeholder)
        self._login_page.identity_input.clear()
        self._login_page.pass_input.clear()
        self._stack.setCurrentIndex(PAGE_LOGIN)
        self._set_login_size()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window,     QColor(DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base,       QColor(INPUT_BG))
    palette.setColor(QPalette.Text,       QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())