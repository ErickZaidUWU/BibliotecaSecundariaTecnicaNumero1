import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QDialog, QMessageBox, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient, QBrush, QPainter
)

from colors.colors import (
    TEXT_PRIMARY, TEXT_MUTED, ACCENT, ERROR, SUCCESS,
    DARK_BG, CARD_BG, BORDER, INPUT_BG, ACCENT_HOVER
)
from componets.componets import StyledInput, PrimaryButton
from supabase_client import supabase


# ── Fondo con gradiente (Mismo estilo visual) ─────────────────────────────────
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


# ── Estilos globales heredados ────────────────────────────────────────────────
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
        background-color: #1a1926;
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 10px 14px;
        border: none;
        border-bottom: 1px solid {BORDER};
        text-transform: uppercase;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background: {INPUT_BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        color: {TEXT_PRIMARY};
        font-size: 13px;
        padding: 10px 14px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {ACCENT};
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
INPUT_STYLE = f"""
    QLineEdit, QComboBox, QDateEdit {{
        background: {INPUT_BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        color: {TEXT_PRIMARY};
        font-size: 13px;
        padding: 10px 14px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border-color: {ACCENT};
    }}
"""

CALENDAR_STYLE = f"""
    QCalendarWidget QWidget {{
        alternate-background-color: #1a1926;
        background-color: {CARD_BG};
        color: {TEXT_PRIMARY};
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {TEXT_PRIMARY};
        background-color: {DARK_BG};
        selection-background-color: {ACCENT};
        selection-color: {TEXT_PRIMARY};
    }}
    QCalendarWidget QMenu {{
        background-color: {CARD_BG};
        color: {TEXT_PRIMARY};
    }}
"""

# ── Diálogo: Registrar / Editar Préstamo ──────────────────────────────────────
class LoanDialog(QDialog):
    def __init__(self, parent=None, loan_data=None, books_list=None):
        super().__init__(parent)
        self.setWindowTitle("Editar préstamo" if loan_data else "Registrar préstamo")
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet(f"background: {CARD_BG}; border-radius: 14px;")

        self.result_data = None  
        self.books_list = books_list if books_list else []

        # Lista predefinida de grados y grupos
        self.grade_groups_list = [
            "1º A", "1º B", "1º C", "1º D", "1º E", "1º F", "1º G", "1º H", "1º I", "1º J", "1º K", "1º L",
            "2º A", "2º B", "2º C", "2º D", "2º E", "2º F", "2º G", "2º H", "2º I", "2º J", "2º K", "2º L",
            "3º A", "3º B", "3º C", "3º D", "3º E", "3º F", "3º G", "3º H", "3º I", "3º J", "3º K", "3º L",
        ]

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(28, 22, 28, 22)

        ttl = QLabel("Editar préstamo" if loan_data else "Nuevo préstamo")
        ttl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        ttl.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(ttl)

        # 1. Selector de Libro
        lbl_book = QLabel("Libro Solicitado")
        lbl_book.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_book)
        
        self.book_combo = QComboBox()
        self.book_combo.setFixedHeight(40)
        self.book_combo.setStyleSheet(INPUT_STYLE)
        if self.books_list:
            self.book_combo.addItems(self.books_list)
        else:
            self.book_combo.addItem("No hay libros disponibles")
        layout.addWidget(self.book_combo)

        # 2. Nombre del Alumno
        lbl_student = QLabel("Alumno")
        lbl_student.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_student)
        
        self.student_input = QLineEdit()
        self.student_input.setPlaceholderText("Nombre completo del alumno")
        self.student_input.setFixedHeight(40)
        self.student_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.student_input)

        # 3. Combo Box para Grado y Grupo
        lbl_grade = QLabel("Grado y Grupo")
        lbl_grade.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_grade)
        
        self.grade_combo = QComboBox()
        self.grade_combo.setFixedHeight(40)
        self.grade_combo.setStyleSheet(INPUT_STYLE)
        self.grade_combo.addItems(self.grade_groups_list)
        layout.addWidget(self.grade_combo)

        # 4. Fecha de Salida
        lbl_loan_date = QLabel("Fecha de Salida")
        lbl_loan_date.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_loan_date)
        
        self.loan_date_input = QLineEdit()
        self.loan_date_input.setFixedHeight(40)
        self.loan_date_input.setStyleSheet(INPUT_STYLE)
        self.loan_date_input.setText(QDate.currentDate().toString("yyyy-MM-dd"))
        layout.addWidget(self.loan_date_input)

        # 5. Calendario para la Fecha de Devolución
        lbl_return_date = QLabel("Fecha de Devolución")
        lbl_return_date.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_return_date)
        
        self.return_date_edit = QDateEdit()
        self.return_date_edit.setFixedHeight(40)
        self.return_date_edit.setStyleSheet(INPUT_STYLE)
        self.return_date_edit.setCalendarPopup(True)  # Muestra el calendario al hacer clic
        self.return_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.return_date_edit.setDate(QDate.currentDate().addDays(7)) # Por defecto añade una semana
        self.return_date_edit.calendarWidget().setStyleSheet(CALENDAR_STYLE)
        layout.addWidget(self.return_date_edit)

        # Mensaje de error interno
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

        # Cargar datos existentes si se pasa a modo Edición
        if loan_data:
            idx_book = self.book_combo.findText(str(loan_data[0]))
            if idx_book >= 0: self.book_combo.setCurrentIndex(idx_book)
            
            self.student_input.setText(str(loan_data[1]))
            
            idx_grade = self.grade_combo.findText(str(loan_data[2]))
            if idx_grade >= 0: 
                self.grade_combo.setCurrentIndex(idx_grade)
            else: 
                self.grade_combo.addItem(str(loan_data[2]))
                self.grade_combo.setCurrentText(str(loan_data[2]))
            
            self.loan_date_input.setText(str(loan_data[3]))
            
            parsed_date = QDate.fromString(str(loan_data[4]), "yyyy-MM-dd")
            if parsed_date.isValid():
                self.return_date_edit.setDate(parsed_date)

    def _confirm(self):
        book = self.book_combo.currentText()
        student = self.student_input.text().strip()
        grade_group = self.grade_combo.currentText()
        loan_date = self.loan_date_input.text().strip()
        # Obtener la fecha seleccionada del calendario formateada como texto
        return_date = self.return_date_edit.date().toString("yyyy-MM-dd")

        if not student or book == "No hay libros disponibles":
            self.msg.setText("⚠ El nombre del alumno es obligatorio.")
            return

        if len(loan_date) != 10 or loan_date[4] != '-':
            self.msg.setText("⚠ La fecha de salida debe tener el formato AAAA-MM-DD.")
            return

        self.result_data = [book, student, grade_group, loan_date, return_date]
        self.accept()


# ── Ventana principal de Préstamos ────────────────────────────────────────────
class LibraryLoans(QMainWindow):
    def __init__(self, user_email="admin@biblioteca.com", on_logout=None):
        super().__init__()
        self.user_email = user_email
        self.on_logout  = on_logout        
        self._drag_pos  = None

        self.setWindowTitle("Control de Préstamos - Biblioteca")
        self.setMinimumSize(950, 640)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._loans = [] 
        self._available_books = []
        self._build_ui()

    def _load_data_from_supabase(self):
        try:
            # 1. Cargar Préstamos
            response = supabase.table("loans").select("*").execute()
            self._loans = []
            for l in response.data:
                self._loans.append([
                    l.get("book_title", ""),
                    l.get("student_name", ""),
                    l.get("grade_group", ""),
                    l.get("loan_date", ""),
                    l.get("return_date", ""),
                ])
                
            # 2. Cargar libros para el selector del diálogo
            book_resp = supabase.table("books").select("name").execute()
            self._available_books = [b.get("name") for b in book_resp.data if b.get("name")]
            
        except Exception as e:
            self._show_toast(f"❌ Error de red: {str(e)}")

    def _build_ui(self):
        root = GradientBackground()
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Cuerpo Principal
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 22, 28, 22)
        body_layout.setSpacing(16)

        header_row = QHBoxLayout()
        h_title = QLabel("Historial y Registro de Préstamos")
        h_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        h_title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header_row.addWidget(h_title)
        header_row.addStretch()

        add_btn = PrimaryButton("＋  Registrar Préstamo")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_loan)
        header_row.addWidget(add_btn)
        body_layout.addLayout(header_row)

        # Barra de Búsqueda inteligente
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por alumno, libro o grado...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self.search_input)
        body_layout.addLayout(search_row)

        # Fila de Estadísticas Rápidas
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        body_layout.addLayout(self.stats_row)

        # Tabla de Préstamos configurada a 6 columnas
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Libro Prestado", "Alumno", "Grado y Grupo", "F. Salida", "F. Devolución", "Acciones"]
        )
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 160)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        body_layout.addWidget(self.table)

        # Sistema de Notificaciones Toast
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

        # Cargar y Renderizar Datos
        self._load_data_from_supabase() 
        self._refresh_table()
        self._refresh_stats()

    def _refresh_stats(self):
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_prestamos = len(self._loans)
        
        # Lógica para detectar si un libro ya expiró comparado con el día de hoy
        hoy = QDate.currentDate().toString("yyyy-MM-dd")
        vencidos = sum(1 for l in self._loans if l[4] < hoy)

        for icon, value, label in [
            ("📝", str(total_prestamos), "Préstamos Activos"),
            ("⚠", str(vencidos), "Vencidos / Atrasados"),
        ]:
            chip = QFrame()
            chip.setStyleSheet(f"QFrame {{ background: rgba(108,99,255,0.08); border: 1px solid {BORDER}; border-radius: 10px; padding: 6px 14px; }}")
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
        loans = data if data is not None else self._loans
        self.table.setRowCount(len(loans))
        hoy = QDate.currentDate().toString("yyyy-MM-dd")

        for row, loan in enumerate(loans):
            self.table.setRowHeight(row, 48)
            for col, val in enumerate(loan):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(TEXT_PRIMARY))
                
                # Resaltar en rojo si la fecha de devolución ya venció
                if col == 4 and str(val) < hoy:
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
            edit_btn.clicked.connect(lambda _, r=row, l=loan: self._edit_loan(r, l))
            action_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑 Terminar")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedHeight(30)
            del_btn.setStyleSheet(BTN_DANGER)
            del_btn.clicked.connect(lambda _, r=row: self._delete_loan(r))
            action_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def _filter_table(self, text):
        q = text.lower()
        if not q:
            self._refresh_table()
            return
        filtered = [l for l in self._loans
                    if q in l[0].lower() or q in l[1].lower() or q in l[2].lower()]
        self._refresh_table(filtered)

    def _add_loan(self):
        dlg = LoanDialog(self, books_list=self._available_books)
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            new_loan = {
                "book_title": dlg.result_data[0],
                "student_name": dlg.result_data[1],
                "grade_group": dlg.result_data[2],
                "loan_date": dlg.result_data[3],
                "return_date": dlg.result_data[4]
            }
            try:
                supabase.table("loans").insert(new_loan).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("✓ Préstamo registrado con éxito en la nube.")
            except Exception as e:
                self._show_toast("❌ Error al registrar préstamo.")

    def _edit_loan(self, row, loan):
        try:
            real_idx = self._loans.index(loan)
        except ValueError:
            real_idx = row

        dlg = LoanDialog(self, loan_data=self._loans[real_idx], books_list=self._available_books)
        if dlg.exec_() == QDialog.Accepted and dlg.result_data:
            # Usamos el nombre del alumno y libro como identificador de actualización 
            student_name = self._loans[real_idx][1]
            book_title = self._loans[real_idx][0]
            
            updated_data = {
                "book_title": dlg.result_data[0],
                "student_name": dlg.result_data[1],
                "grade_group": dlg.result_data[2],
                "loan_date": dlg.result_data[3],
                "return_date": dlg.result_data[4]
            }
            try:
                supabase.table("loans").update(updated_data).eq("student_name", student_name).eq("book_title", book_title).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("✓ Préstamo actualizado correctamente.")
            except Exception as e:
                self._show_toast("❌ Error al actualizar.")

    def _delete_loan(self, row):
        student_item = self.table.item(row, 1)
        book_item = self.table.item(row, 0)
        
        student = student_item.text() if student_item else ""
        book = book_item.text() if book_item else ""
        
        if not student or not book: return

        mb = QMessageBox(self)
        mb.setWindowTitle("Finalizar Préstamo")
        mb.setText(f"¿Dar por devuelto el libro «{book}» de {student}?\nSe eliminará del registro activo.")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mb.setDefaultButton(QMessageBox.No)
        mb.setStyleSheet(f"""
            QMessageBox {{ background: {CARD_BG}; color: {TEXT_PRIMARY}; }}
            QPushButton {{ background: {CARD_BG}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 8px; padding: 6px 18px; }}
            QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
        """)
        if mb.exec_() == QMessageBox.Yes:
            try:
                supabase.table("loans").delete().eq("student_name", student).eq("book_title", book).execute()
                self._load_data_from_supabase()
                self._refresh_table()
                self._refresh_stats()
                self._show_toast("🗑 Libro marcado como devuelto con éxito.")
            except Exception as e:
                self._show_toast("❌ Error al procesar la devolución.")

    def _show_toast(self, msg):
        self.toast.setText(msg)
        self.toast.setFixedHeight(38)
        QTimer.singleShot(2800, lambda: self.toast.setFixedHeight(0))

    def _logout(self):
        try: supabase.auth.sign_out()
        except: pass
        self.close()
        if self.on_logout: self.on_logout()

    # ── Manejo de arrastre de ventana sin bordes (Frameless) ──────────────────
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
    w = LibraryLoans(user_email="admin@biblioteca.com")
    w.show()
    sys.exit(app.exec_())