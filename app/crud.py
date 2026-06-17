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
from supabase_client import supabase


# ── Fondo con gradiente (reutilizado del proyecto) ────────────────────────────
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


# ── Estilos globales ──────────────────────────────────────────────────────────
TABLE_STYLE = f"""
    QTableWidget {{
        background: transparent;
        border: none;
        gridline-color: {BORDER};
        color: {TEXT_PRIMARY};
        font-size: 13px;
        selection-background-color: rgba(255,115,7,0.18);
    }}
    QTableWidget::item {{
        padding: 10px 14px;
        border-bottom: 1px solid {BORDER};
    }}
    QTableWidget::item:selected {{
        background: rgba(255,115,7,0.18);
        color: {TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background-color: {CARD_BG};
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
        background: rgba(217,83,79,0.12);
        color: {ERROR};
        border: 1px solid rgba(217,83,79,0.30);
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: rgba(217,83,79,0.22);
        border: 1px solid {ERROR};
    }}
"""

BTN_ACCENT = f"""
    QPushButton {{
        background: rgba(255,115,7,0.15);
        color: {ACCENT};
        border: 1px solid rgba(255,115,7,0.35);
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: rgba(255,115,7,0.25);
        border: 1px solid {ACCENT};
    }}
"""


# ── Diálogo: Agregar / Editar libro ──────────────────────────────────────────
class BookDialog(QDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar libro" if book_data else "Agregar libro")
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet(f"background: {CARD_BG}; border-radius: 14px;")

        self.result_data = None  

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(28, 24, 28, 24)

        ttl = QLabel("Editar libro" if book_data else "Nuevo libro")
        ttl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        ttl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(ttl)

        # Campos alineados al 100% con las columnas de tu BD de Supabase
        fields = [
            ("Título",    "Ej: El Señor de los Anillos"),
            ("Autor",     "Ej: J.R.R. Tolkien"),
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

        if book_data:
            keys = ["Título", "Autor", "Año", "Categoría", "Stock"]
            for i, key in enumerate(keys):
                self.inputs[key].setText(str(book_data[i]))

        self.msg = QLabel("")
        self.msg.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        self.msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg)

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
                  ["Título", "Autor", "Año", "Categoría", "Stock"]]

        if not all(values):
            self.msg.setText("⚠  Todos los campos son obligatorios.")
            return

        # Corrección de índices de validación (Año está en índice 2, Stock en índice 4)
        try:
            int(values[2])
            int(values[4])
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
        self.on_logout  = on_logout        
        self._drag_pos  = None

        self.setWindowTitle("Biblioteca Secundaria Técnica Nº1")
        self.setMinimumSize(900, 620)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._books = [] 
        self._build_ui()

    def _load_data_from_supabase(self):
        try:
            response = supabase.table("books").select("*").execute()
        
            self._books = []
            for b in response.data:
                # b.get("name") corrige el mapeo con tu columna de la nube
                self._books.append([
                    b.get("name", ""),      
                    b.get("author", ""),    
                    str(b.get("year", 0)),  
                    b.get("category", ""),  
                    str(b.get("stock", 0)), 
                ])
        except Exception as e:
            self._show_toast(f"❌ Error de red: {str(e)}")

    def _build_ui(self):
        root = GradientBackground()
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 22, 28, 22)
        body_layout.setSpacing(16)

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

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por título, autor o categoría…")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self.search_input)
        body_layout.addLayout(search_row)

        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        body_layout.addLayout(self.stats_row)

        # Ajustado a 6 columnas en total (Removido ISBN de la vista)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Título", "Autor", "Año", "Categoría", "Stock", "Acciones"]
        )
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 160)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        body_layout.addWidget(self.table)

        self.toast = QLabel("")
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.setFixedHeight(0)
        self.toast.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,115,7,0.15);
                border: 1px solid rgba(255,115,7,0.35);
                border-radius: 8px;
                color: {ACCENT};
                font-size: 13px;
                padding: 8px;
            }}
        """)
        body_layout.addWidget(self.toast)

        main.addWidget(body)

        self._load_data_from_supabase() 
        self._refresh_table()
        self._refresh_stats()

    def _refresh_stats(self):
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_libros = len(self._books)
        # Corrección de índices para las operaciones de conteo matemático
        total_stock  = sum(int(b[4]) for b in self._books) 
        categorias   = len(set(b[3] for b in self._books)) 

        for icon, value, label in [
            ("📚", str(total_libros), "Títulos"),
            ("📦", str(total_stock),  "Libros"),
            ("🗂", str(categorias),   "Categorías"),
        ]:
            chip = QFrame()
            chip.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255,115,7,0.08);
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

    def _refresh_table(self, data=None):
        books = data if data is not None else self._books
        self.table.setRowCount(len(books))

        for row, book in enumerate(books):
            self.table.setRowHeight(row, 48)
            for col, val in enumerate(book):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(TEXT_PRIMARY))
                if col == 4 and int(val) == 0:
                    item.setForeground(QColor(ERROR))
                self.table.setItem(row, col, item)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 4, 8, 4)
            action_layout.setSpacing(6)

            edit_btn = QPushButton("✏ Editar")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setFixedHeight(30)
            edit_btn.setStyleSheet(BTN_ACCENT)
            edit_btn.clicked.connect(lambda _, r=row, b=book: self._edit_book(r, b))
            action_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑 Borrar")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedHeight(30)
            del_btn.setStyleSheet(BTN_DANGER)
            del_btn.clicked.connect(lambda _, r=row: self._delete_book(r))
            action_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def _filter_table(self, text):
        q = text.lower()
        if not q:
            self._refresh_table()
            return
        filtered = [b for b in self._books
                    if q in b[0].lower() or q in b[1].lower() or q in b[3].lower()]
        self._refresh_table(filtered)

    def _add_book(self):
        dlg = BookDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            # Removido ISBN de la estructura enviada a la API
            new_book = {
                "name": dlg.result_data[0],
                "author": dlg.result_data[1],
                "year": int(dlg.result_data[2]),
                "category": dlg.result_data[3],
                "stock": int(dlg.result_data[4])
            }
            try:
                supabase.table("books").insert(new_book).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("✓ Libro guardado en la nube.")
            except Exception as e:
                self._show_toast("❌ Error al guardar.")

    def _edit_book(self, row, book):
        try:
            real_idx = self._books.index(book)
        except ValueError:
            real_idx = row

        dlg = BookDialog(self, book_data=self._books[real_idx][:5])
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            # Tu llave primaria en Supabase es el título ('name')
            book_name = self._books[real_idx][0] 
            
            updated_data = {
                "name": dlg.result_data[0],
                "author": dlg.result_data[1],
                "year": int(dlg.result_data[2]),
                "category": dlg.result_data[3],
                "stock": int(dlg.result_data[4])
            }
            try:
                supabase.table("books").update(updated_data).eq("name", book_name).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("✓ Libro actualizado con éxito.")
            except Exception as e:
                self._show_toast("❌ Error al actualizar.")

    def _delete_book(self, row):
        title_item = self.table.item(row, 0)
        title = title_item.text() if title_item else ""
        
        if not title: return

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
            try:
                supabase.table("books").delete().eq("name", title).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("🗑 Libro eliminado de la base de datos.")
            except Exception as e:
                self._show_toast("❌ Error al eliminar.")

    def _show_toast(self, msg):
        self.toast.setText(msg)
        self.toast.setFixedHeight(38)
        QTimer.singleShot(2800, lambda: self.toast.setFixedHeight(0))

    def _logout(self):
        try:
            supabase.auth.sign_out()
        except:
            pass
        self.close()
        if self.on_logout:
            self.on_logout()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None


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