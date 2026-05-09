import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFrame, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QMessageBox,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient,
    QBrush, QPainter
)

from colors.colors import (
    TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS,
    DARK_BG, CARD_BG, BORDER, INPUT_BG, ACCENT_HOVER
)
from componets.componets import StyledInput, PrimaryButton


# ── Fondo con gradiente (reutilizado del proyecto) ────────────────────────────
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#0D0D0F"))
        gradient.setColorAt(0.5, QColor("#12101C"))
        gradient.setColorAt(1.0, QColor("#0D1117"))
        painter.fillRect(self.rect(), QBrush(gradient))
        painter.setBrush(QColor(108, 99, 255, 18))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-80, -80, 420, 420)
        painter.setBrush(QColor(78, 205, 196, 12))
        painter.drawEllipse(self.width() - 250, self.height() - 200, 400, 400)


# ── Estilos globales ──────────────────────────────────────────────────────────
TABLE_STYLE = f"""
    QTableWidget {{
        background: transparent;
        border: none;
        gridline-color: {BORDER};
        color: {TEXT_PRIMARY};
        font-size: 13px;
        selection-background-color: rgba(108,99,255,0.18);
    }}
    QTableWidget::item {{
        padding: 10px 14px;
        border-bottom: 1px solid {BORDER};
    }}
    QTableWidget::item:selected {{
        background: rgba(108,99,255,0.18);
        color: {TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background: rgba(108,99,255,0.10);
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 10px 14px;
        border: none;
        border-bottom: 1px solid {BORDER};
        text-transform: uppercase;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        background: {INPUT_BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        color: {TEXT_PRIMARY};
        font-size: 13px;
        padding: 10px 14px;
    }}
    QLineEdit:focus {{
        border-color: {ACCENT};
    }}
    QLineEdit::placeholder {{
        color: {TEXT_MUTED};
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background: rgba(226,75,74,0.12);
        color: #e24b4a;
        border: 1px solid rgba(226,75,74,0.30);
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: rgba(226,75,74,0.22);
    }}
"""

BTN_ACCENT = f"""
    QPushButton {{
        background: rgba(108,99,255,0.15);
        color: {ACCENT};
        border: 1px solid rgba(108,99,255,0.30);
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: rgba(108,99,255,0.25);
    }}
"""


# ── Diálogo: Agregar / Editar libro ──────────────────────────────────────────
class BookDialog(QDialog):
    """
    Se usa tanto para agregar como para editar.
    Si se pasa `book_data`, los campos se pre-llenan (modo edición).
    """

    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar libro" if book_data else "Agregar libro")
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet(f"background: {CARD_BG}; border-radius: 14px;")

        self.result_data = None  # Se llena al confirmar

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(28, 24, 28, 24)

        # Título del diálogo
        ttl = QLabel("Editar libro" if book_data else "Nuevo libro")
        ttl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        ttl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(ttl)

        # Campos
        fields = [
            ("Título",    "Ej: El Señor de los Anillos"),
            ("Autor",     "Ej: J.R.R. Tolkien"),
            ("ISBN",      "Ej: 978-0-06-112008-4"),
            ("Año",       "Ej: 1954"),
            ("Categoría", "Ej: Fantasía"),
            ("Stock",     "Ej: 5"),
        ]

        self.inputs = {}
        for label_text, placeholder in fields:
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            layout.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(40)
            inp.setStyleSheet(INPUT_STYLE)
            layout.addWidget(inp)
            self.inputs[label_text] = inp

        # Pre-llenar en modo edición
        if book_data:
            keys = ["Título", "Autor", "ISBN", "Año", "Categoría", "Stock"]
            for i, key in enumerate(keys):
                self.inputs[key].setText(str(book_data[i]))

        # Mensaje de error
        self.msg = QLabel("")
        self.msg.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        self.msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel = QPushButton("Cancelar")
        cancel.setFixedHeight(40)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: 1px solid {BORDER}; border-radius: 10px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; border-color: {TEXT_MUTED}; }}
        """)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        confirm = PrimaryButton("Guardar")
        confirm.setFixedHeight(40)
        confirm.clicked.connect(self._confirm)
        btn_row.addWidget(confirm)

        layout.addLayout(btn_row)

    def _confirm(self):
        values = [self.inputs[k].text().strip() for k in
                  ["Título", "Autor", "ISBN", "Año", "Categoría", "Stock"]]

        if not all(values):
            self.msg.setText("⚠  Todos los campos son obligatorios.")
            return

        # Validar año y stock como números
        try:
            int(values[3])
            int(values[5])
        except ValueError:
            self.msg.setText("⚠  Año y Stock deben ser números enteros.")
            return

        self.result_data = values
        self.accept()


# ── Ventana principal del CRUD ────────────────────────────────────────────────
class LibraryCRUD(QMainWindow):
    def __init__(self, user_email="usuario@ejemplo.com", on_logout=None):
        super().__init__()
        self.user_email = user_email
        self.on_logout  = on_logout        # callback para volver al login
        self._drag_pos  = None

        self.setWindowTitle("Biblioteca Técnica Nº1")
        self.setMinimumSize(900, 620)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ── Datos en memoria ──────────────────────────────────────────────────
        # Cada libro: [Título, Autor, ISBN, Año, Categoría, Stock]
        self._books = [
            ["Clean Code",              "Robert C. Martin", "978-0-13-235088-4", "2008", "Programación",  "3"],
            ["The Pragmatic Programmer","David Thomas",     "978-0-13-595705-9", "1999", "Programación",  "2"],
            ["Design Patterns",         "GoF",              "978-0-20-163361-5", "1994", "Arquitectura",  "1"],
            ["Dune",                    "Frank Herbert",    "978-0-44-101359-7", "1965", "Ciencia ficción","4"],
            ["Sapiens",                 "Yuval N. Harari",  "978-0-06-231609-7", "2011", "Historia",       "5"],
        ]

        self._build_ui()

    # ── Construcción de la UI ─────────────────────────────────────────────────
    def _build_ui(self):
        root = GradientBackground()
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Barra de título ───────────────────────────────────────────────────
        title_bar = QWidget()
        title_bar.setFixedHeight(46)
        title_bar.setStyleSheet("background: transparent;")
        tb = QHBoxLayout(title_bar)
        tb.setContentsMargins(20, 0, 14, 0)

        logo = QLabel("◈  Biblioteca Técnica Nº1")
        logo.setFont(QFont("Segoe UI", 11, QFont.Bold))
        logo.setStyleSheet(f"color: {ACCENT};")
        tb.addWidget(logo)

        tb.addStretch()

        # Usuario activo
        user_lbl = QLabel(f"● {self.user_email}")
        user_lbl.setFont(QFont("Segoe UI", 9))
        user_lbl.setStyleSheet(f"color: {TEXT_MUTED}; margin-right: 8px;")
        tb.addWidget(user_lbl)

        # Botón cerrar sesión
        logout_btn = QPushButton("Cerrar sesión")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; padding: 4px 12px;
            }}
            QPushButton:hover {{ color: #e24b4a; border-color: #e24b4a; }}
        """)
        logout_btn.clicked.connect(self._logout)
        tb.addWidget(logout_btn)

        for symbol, action in [("─", self.showMinimized), ("✕", self.close)]:
            btn = QPushButton(symbol)
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(action)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_MUTED};
                    border: none; font-size: 13px; border-radius: 6px; margin-left: 4px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.08); color: {TEXT_PRIMARY};
                }}
            """)
            tb.addWidget(btn)

        main.addWidget(title_bar)

        # ── Separador ─────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        main.addWidget(sep)

        # ── Cuerpo ────────────────────────────────────────────────────────────
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 22, 28, 22)
        body_layout.setSpacing(16)

        # Encabezado + botón agregar
        header_row = QHBoxLayout()

        h_title = QLabel("Catálogo de Libros")
        h_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        h_title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header_row.addWidget(h_title)

        header_row.addStretch()

        add_btn = PrimaryButton("＋  Agregar libro")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_book)
        header_row.addWidget(add_btn)

        body_layout.addLayout(header_row)

        # Barra de búsqueda
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por título, autor o categoría…")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self.search_input)
        body_layout.addLayout(search_row)

        # Estadísticas rápidas
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        body_layout.addLayout(self.stats_row)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Título", "Autor", "ISBN", "Año", "Categoría", "Stock", "Acciones"]
        )
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 160)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        body_layout.addWidget(self.table)

        # Mensaje de feedback (toast)
        self.toast = QLabel("")
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.setFixedHeight(0)
        self.toast.setStyleSheet(f"""
            QLabel {{
                background: rgba(108,99,255,0.15);
                border: 1px solid rgba(108,99,255,0.35);
                border-radius: 8px;
                color: {ACCENT};
                font-size: 13px;
                padding: 8px;
            }}
        """)
        body_layout.addWidget(self.toast)

        main.addWidget(body)

        self._refresh_table()
        self._refresh_stats()

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _refresh_stats(self):
        # Limpiar chips anteriores
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_libros = len(self._books)
        total_stock  = sum(int(b[5]) for b in self._books)
        categorias   = len(set(b[4] for b in self._books))

        for icon, value, label in [
            ("📚", str(total_libros), "Títulos"),
            ("📦", str(total_stock),  "Ejemplares"),
            ("🗂", str(categorias),   "Categorías"),
        ]:
            chip = QFrame()
            chip.setStyleSheet(f"""
                QFrame {{
                    background: rgba(108,99,255,0.08);
                    border: 1px solid {BORDER};
                    border-radius: 10px;
                    padding: 6px 14px;
                }}
            """)
            cl = QHBoxLayout(chip)
            cl.setContentsMargins(10, 6, 10, 6)
            cl.setSpacing(8)
            ico = QLabel(icon)
            ico.setFont(QFont("Segoe UI", 14))
            cl.addWidget(ico)
            txt = QLabel(f"<b>{value}</b> {label}")
            txt.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            cl.addWidget(txt)
            self.stats_row.addWidget(chip)

        self.stats_row.addStretch()

    # ── Tabla ─────────────────────────────────────────────────────────────────
    def _refresh_table(self, data=None):
        books = data if data is not None else self._books
        self.table.setRowCount(len(books))

        for row, book in enumerate(books):
            self.table.setRowHeight(row, 48)
            for col, val in enumerate(book):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(TEXT_PRIMARY))
                # Colorear stock bajo en rojo
                if col == 5 and int(val) == 0:
                    item.setForeground(QColor(ERROR))
                self.table.setItem(row, col, item)

            # Botones de acción
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 4, 8, 4)
            action_layout.setSpacing(6)

            edit_btn = QPushButton("✏ Editar")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setFixedHeight(30)
            edit_btn.setStyleSheet(BTN_ACCENT)
            # Capturar índice real en _books
            edit_btn.clicked.connect(lambda _, r=row, b=book: self._edit_book(r, b))
            action_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑 Borrar")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedHeight(30)
            del_btn.setStyleSheet(BTN_DANGER)
            del_btn.clicked.connect(lambda _, r=row: self._delete_book(r))
            action_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 6, action_widget)

    def _filter_table(self, text):
        q = text.lower()
        if not q:
            self._refresh_table()
            return
        filtered = [b for b in self._books
                    if q in b[0].lower() or q in b[1].lower() or q in b[4].lower()]
        self._refresh_table(filtered)

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def _add_book(self):
        dlg = BookDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            self._books.append(dlg.result_data)
            self._refresh_table()
            self._refresh_stats()
            self._show_toast("✓  Libro agregado correctamente.")

    def _edit_book(self, row, book):
        # Encontrar índice real en _books por referencia de datos
        try:
            real_idx = self._books.index(book)
        except ValueError:
            real_idx = row

        dlg = BookDialog(self, book_data=self._books[real_idx])
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            self._books[real_idx] = dlg.result_data
            self._refresh_table()
            self._refresh_stats()
            self._show_toast("✓  Libro actualizado correctamente.")

    def _delete_book(self, row):
        # Obtener título del libro visible en la fila
        title_item = self.table.item(row, 0)
        title = title_item.text() if title_item else "este libro"

        mb = QMessageBox(self)
        mb.setWindowTitle("Confirmar eliminación")
        mb.setText(f"¿Eliminar «{title}»?\nEsta acción no se puede deshacer.")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mb.setDefaultButton(QMessageBox.No)
        mb.setStyleSheet(f"""
            QMessageBox {{ background: {CARD_BG}; color: {TEXT_PRIMARY}; }}
            QPushButton {{ background: {CARD_BG}; color: {TEXT_PRIMARY};
                          border: 1px solid {BORDER}; border-radius: 8px;
                          padding: 6px 18px; }}
            QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
        """)
        if mb.exec_() == QMessageBox.Yes:
            # Buscar y eliminar de _books por título visible
            for i, b in enumerate(self._books):
                if b[0] == title:
                    self._books.pop(i)
                    break
            self._refresh_table()
            self._refresh_stats()
            self._show_toast("🗑  Libro eliminado.")

    # ── Toast de feedback ─────────────────────────────────────────────────────
    def _show_toast(self, msg):
        self.toast.setText(msg)
        self.toast.setFixedHeight(38)
        QTimer.singleShot(2800, lambda: self.toast.setFixedHeight(0))

    # ── Logout ────────────────────────────────────────────────────────────────
    def _logout(self):
        self.close()
        if self.on_logout:
            self.on_logout()

    # ── Arrastrar ventana ─────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None


# ── Entry point independiente (para probar crud.py solo) ─────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window,     QColor(DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base,       QColor(INPUT_BG))
    palette.setColor(QPalette.Text,       QColor(TEXT_PRIMARY))
    app.setPalette(palette)
    w = LibraryCRUD(user_email="admin@biblioteca.com")
    w.show()
    sys.exit(app.exec_())