# main.py
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit,
    QFrame, QGridLayout, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import database as db
from themes import DARK, LIGHT, build_stylesheet
from login import VentanaAuth

# ── Theme Manager ─────────────────────────────────────────
class ThemeManager(QObject):
    theme_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._theme   = DARK
        self._is_dark = True

    @property
    def t(self): return self._theme

    @property
    def is_dark(self): return self._is_dark

    def toggle(self):
        self._is_dark = not self._is_dark
        self._theme   = DARK if self._is_dark else LIGHT
        self.theme_changed.emit(self._theme)

TM = ThemeManager()

# ── Icon helpers ──────────────────────────────────────────
ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")

def svg_icon(name, color, size=18):
    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.exists(path):
        return QIcon()
    with open(path) as f:
        data = f.read()
    data = data.replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(data.encode())
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    renderer.render(p)
    p.end()
    return QIcon(pix)

def svg_pix(name, color, size=18):
    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.exists(path):
        return QPixmap()
    with open(path) as f:
        data = f.read()
    data = data.replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(data.encode())
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    renderer.render(p)
    p.end()
    return pix

# ── Helpers ───────────────────────────────────────────────
def fmt_money(v):
    try:
        return f"$ {v:,.0f}".replace(",", ".")
    except Exception:
        return "$ 0"

def card(parent=None):
    f = QFrame(parent)
    f.setObjectName("card")
    return f

def h_line():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line

# ── Dialog: Nueva Cuenta ──────────────────────────────────
class DialogCuenta(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva cuenta")
        self.setMinimumWidth(400)
        self.setStyleSheet(build_stylesheet(TM.t))
        self._user_id = user_id
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(18)
        lay.setContentsMargins(28, 28, 28, 28)

        title = QLabel("Nueva cuenta")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        lay.addWidget(title)
        lay.addWidget(h_line())

        form = QFormLayout()
        form.setSpacing(13)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Ej: Cuenta principal, Caja menor…")
        form.addRow("Nombre *", self.inp_nombre)

        self.inp_tipo = QComboBox()
        self.inp_tipo.addItems(["Negocio", "Personal", "Proyecto", "Inversión", "Ahorro"])
        form.addRow("Tipo", self.inp_tipo)

        self.inp_saldo = QDoubleSpinBox()
        self.inp_saldo.setRange(0, 999_999_999)
        self.inp_saldo.setDecimals(0)
        self.inp_saldo.setSingleStep(10_000)
        self.inp_saldo.setPrefix("$ ")
        form.addRow("Saldo inicial", self.inp_saldo)

        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Descripción opcional…")
        self.inp_desc.setFixedHeight(68)
        form.addRow("Descripción", self.inp_desc)

        lay.addLayout(form)
        lay.addSpacerItem(QSpacerItem(0, 8))

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("  Crear cuenta")
        btn_ok.setIcon(svg_icon("add", TM.t["text_inverse"]))
        btn_ok.setIconSize(QSize(14, 14))
        btn_ok.clicked.connect(self._aceptar)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

    def _aceptar(self):
        if not self.inp_nombre.text().strip():
            QMessageBox.warning(self, "Campo requerido", "El nombre es obligatorio.")
            return
        db.crear_cuenta(
            self._user_id,
            self.inp_nombre.text().strip(),
            self.inp_desc.toPlainText().strip(),
            self.inp_tipo.currentText(),
            self.inp_saldo.value()
        )
        self.accept()

# ── Dialog: Nuevo Movimiento ──────────────────────────────
class DialogMovimiento(QDialog):
    def __init__(self, user_id, cuenta_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar movimiento")
        self.setMinimumWidth(430)
        self.setStyleSheet(build_stylesheet(TM.t))
        self._user_id   = user_id
        self._cuenta_id = cuenta_id
        self._tipo      = "ingreso"
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(18)
        lay.setContentsMargins(28, 28, 28, 28)

        title = QLabel("Nuevo movimiento")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        lay.addWidget(title)
        lay.addWidget(h_line())

        form = QFormLayout()
        form.setSpacing(13)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_cuenta = QComboBox()
        self._cuentas = db.obtener_cuentas(self._user_id)
        for c in self._cuentas:
            self.inp_cuenta.addItem(c[2], c[0])
        if self._cuenta_id:
            for i, c in enumerate(self._cuentas):
                if c[0] == self._cuenta_id:
                    self.inp_cuenta.setCurrentIndex(i)
        form.addRow("Cuenta *", self.inp_cuenta)

        tipo_row = QHBoxLayout()
        tipo_row.setSpacing(8)
        self.btn_ingreso = QPushButton("Ingreso")
        self.btn_egreso  = QPushButton("Egreso")
        for b in [self.btn_ingreso, self.btn_egreso]:
            b.setCheckable(True)
            b.setObjectName("btn_secondary")
            b.setFixedHeight(34)
        self.btn_ingreso.setChecked(True)
        self.btn_ingreso.clicked.connect(lambda: self._set_tipo("ingreso"))
        self.btn_egreso.clicked.connect(lambda: self._set_tipo("egreso"))
        tipo_row.addWidget(self.btn_ingreso)
        tipo_row.addWidget(self.btn_egreso)
        tipo_row.addStretch()
        w = QWidget(); w.setLayout(tipo_row)
        form.addRow("Tipo *", w)

        self.inp_cat = QComboBox()
        self._cargar_categorias("ingreso")
        form.addRow("Categoría", self.inp_cat)

        self.inp_desc = QLineEdit()
        self.inp_desc.setPlaceholderText("Ej: Pago cliente, Factura eléctrica…")
        form.addRow("Descripción *", self.inp_desc)

        self.inp_monto = QDoubleSpinBox()
        self.inp_monto.setRange(0.01, 999_999_999)
        self.inp_monto.setDecimals(0)
        self.inp_monto.setSingleStep(10_000)
        self.inp_monto.setPrefix("$ ")
        form.addRow("Monto *", self.inp_monto)

        self.inp_fecha = QDateEdit(QDate.currentDate())
        self.inp_fecha.setCalendarPopup(True)
        self.inp_fecha.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha *", self.inp_fecha)

        self.inp_notas = QTextEdit()
        self.inp_notas.setPlaceholderText("Notas adicionales…")
        self.inp_notas.setFixedHeight(58)
        form.addRow("Notas", self.inp_notas)

        lay.addLayout(form)
        lay.addSpacerItem(QSpacerItem(0, 8))

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("  Registrar")
        btn_ok.setIcon(svg_icon("add", TM.t["text_inverse"]))
        btn_ok.setIconSize(QSize(14, 14))
        btn_ok.clicked.connect(self._aceptar)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

    def _set_tipo(self, tipo):
        self._tipo = tipo
        self.btn_ingreso.setChecked(tipo == "ingreso")
        self.btn_egreso.setChecked(tipo == "egreso")
        self._cargar_categorias(tipo)

    def _cargar_categorias(self, tipo):
        self.inp_cat.clear()
        for cat in db.obtener_categorias(tipo):
            self.inp_cat.addItem(cat[1])

    def _aceptar(self):
        if not self.inp_desc.text().strip():
            QMessageBox.warning(self, "Campo requerido", "La descripción es obligatoria.")
            return
        if self.inp_monto.value() <= 0:
            QMessageBox.warning(self, "Monto inválido", "El monto debe ser mayor a cero.")
            return
        db.agregar_movimiento(
            self.inp_cuenta.currentData(),
            self._tipo,
            self.inp_cat.currentText(),
            self.inp_desc.text().strip(),
            self.inp_monto.value(),
            self.inp_fecha.date().toString("yyyy-MM-dd"),
            self.inp_notas.toPlainText().strip()
        )
        self.accept()

# ── KPI Card ──────────────────────────────────────────────
class KPICard(QFrame):
    def __init__(self, label, icon_name, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(108)
        self._icon_name = icon_name
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(6)

        top = QHBoxLayout()
        self.lbl_label = QLabel(label.upper())
        self.lbl_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        top.addWidget(self.lbl_label)
        top.addStretch()
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(20, 20)
        top.addWidget(self.icon_lbl)
        lay.addLayout(top)

        self.lbl_value = QLabel("$ 0")
        self.lbl_value.setFont(QFont("Segoe UI", 22, QFont.Weight.ExtraBold))
        lay.addWidget(self.lbl_value)

        self.apply_theme(TM.t)
        TM.theme_changed.connect(self.apply_theme)

    def apply_theme(self, t):
        self.lbl_label.setStyleSheet(f"color: {t['text_muted']};")
        self.icon_lbl.setPixmap(svg_pix(self._icon_name, t["text_muted"], 18))

    def set_value(self, text, color):
        self.lbl_value.setText(text)
        self.lbl_value.setStyleSheet(f"color: {color};")

# ── Gráfica ───────────────────────────────────────────────
class GraficaFlujo(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 3.2), facecolor="none")
        super().__init__(self.fig)
        self._last_data = []
        TM.theme_changed.connect(lambda t: self.actualizar(self._last_data, t))

    def actualizar(self, datos, t=None):
        if t is None: t = TM.t
        self._last_data = datos
        self.fig.clear()
        self.fig.patch.set_facecolor("none")
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("none")

        if not datos:
            ax.text(0.5, 0.5, "Sin movimientos registrados",
                    ha="center", va="center",
                    color=t["text_muted"], fontsize=12)
            ax.axis("off")
            self.draw()
            return

        meses    = [d[0] for d in datos]
        ingresos = [d[1] for d in datos]
        egresos  = [d[2] for d in datos]
        x = list(range(len(meses)))
        w = 0.36
        ax.bar([i - w/2 for i in x], ingresos, width=w,
               color=t["ingreso"], alpha=0.88, label="Ingresos", zorder=3, linewidth=0)
        ax.bar([i + w/2 for i in x], egresos, width=w,
               color=t["egreso"],  alpha=0.88, label="Egresos",  zorder=3, linewidth=0)
        ax.set_xticks(x)
        ax.set_xticklabels(meses, rotation=28, ha="right",
                           color=t["text_muted"], fontsize=9)
        ax.tick_params(axis="y", colors=t["text_muted"], labelsize=9)
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        for sp in ["left", "bottom"]:
            ax.spines[sp].set_color(t["border"])
        ax.yaxis.grid(True, color=t["border"], linestyle="--", alpha=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.legend(facecolor=t["bg_input"], edgecolor=t["border"],
                  labelcolor=t["text_primary"], fontsize=9, framealpha=0.9)
        self.fig.tight_layout(pad=1.2)
        self.draw()

# ── Tab Dashboard ─────────────────────────────────────────
class TabDashboard(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self._user = user
        self._build_ui()
        TM.theme_changed.connect(lambda t: None)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(18)

        top = QHBoxLayout()
        lbl = QLabel("Cuenta:")
        lbl.setStyleSheet(f"color: {TM.t['text_muted']};")
        self.cmb_cuenta = QComboBox()
        self.cmb_cuenta.setMinimumWidth(210)
        self.cmb_cuenta.currentIndexChanged.connect(self.actualizar)
        top.addWidget(lbl)
        top.addWidget(self.cmb_cuenta)
        top.addStretch()
        lay.addLayout(top)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        self.kpi_saldo    = KPICard("Saldo actual",   "accounts")
        self.kpi_ingresos = KPICard("Total ingresos", "movements")
        self.kpi_egresos  = KPICard("Total egresos",  "movements")
        for k in [self.kpi_saldo, self.kpi_ingresos, self.kpi_egresos]:
            kpi_row.addWidget(k)
        lay.addLayout(kpi_row)

        g_card = card()
        g_lay  = QVBoxLayout(g_card)
        g_lay.setContentsMargins(18, 16, 18, 16)
        g_lay.setSpacing(10)
        g_title = QLabel("Flujo Mensual — Ingresos vs Egresos")
        g_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        g_lay.addWidget(g_title)
        self.grafica = GraficaFlujo()
        g_lay.addWidget(self.grafica)
        lay.addWidget(g_card)

    def recargar_cuentas(self):
        self.cmb_cuenta.blockSignals(True)
        self.cmb_cuenta.clear()
        self.cmb_cuenta.addItem("Todas las cuentas", None)
        for c in db.obtener_cuentas(self._user["id"]):
            self.cmb_cuenta.addItem(c[2], c[0])
        self.cmb_cuenta.blockSignals(False)
        self.actualizar()

    def actualizar(self):
        cid = self.cmb_cuenta.currentData()
        r   = db.obtener_resumen(self._user["id"], cid)
        t   = TM.t
        self.kpi_saldo.set_value(
            fmt_money(r["saldo"]),
            t["accent"] if r["saldo"] >= 0 else t["egreso"]
        )
        self.kpi_ingresos.set_value(fmt_money(r["ingresos"]), t["ingreso"])
        self.kpi_egresos.set_value(fmt_money(r["egresos"]),   t["egreso"])
        self.grafica.actualizar(db.obtener_flujo_mensual(self._user["id"], cid))

# ── Tab Movimientos ───────────────────────────────────────
class TabMovimientos(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self._user  = user
        self._datos = []
        self._build_ui()
        TM.theme_changed.connect(self._on_theme)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        tb = QHBoxLayout()
        tb.setSpacing(10)
        self.cmb_cuenta = QComboBox()
        self.cmb_cuenta.setMinimumWidth(160)
        self.cmb_cuenta.currentIndexChanged.connect(self.cargar)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Todos los tipos", "ingreso", "egreso"])
        self.cmb_tipo.currentIndexChanged.connect(self.cargar)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar por descripción…")
        self.inp_buscar.setMinimumWidth(200)
        self.inp_buscar.textChanged.connect(self.cargar)

        self.btn_nuevo = QPushButton("  Nuevo movimiento")
        self.btn_nuevo.setObjectName("btn_icon")
        self.btn_nuevo.setIcon(svg_icon("add", TM.t["accent"]))
        self.btn_nuevo.setIconSize(QSize(14, 14))
        self.btn_nuevo.clicked.connect(self.nuevo_movimiento)

        tb.addWidget(QLabel("Cuenta:"))
        tb.addWidget(self.cmb_cuenta)
        tb.addWidget(QLabel("Tipo:"))
        tb.addWidget(self.cmb_tipo)
        tb.addWidget(self.inp_buscar)
        tb.addStretch()
        tb.addWidget(self.btn_nuevo)
        lay.addLayout(tb)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["Cuenta", "Tipo", "Categoría", "Descripción", "Monto", "Fecha", "Notas"]
        )
        h = self.tabla.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for col in [0, 1, 4, 5]:
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        lay.addWidget(self.tabla)

        footer = QHBoxLayout()
        self.lbl_total = QLabel("0 movimientos")
        self.lbl_total.setStyleSheet(f"color: {TM.t['text_muted']};")
        self.btn_del = QPushButton("  Eliminar seleccionado")
        self.btn_del.setObjectName("btn_danger")
        self.btn_del.setIcon(svg_icon("delete", "#FFFFFF"))
        self.btn_del.setIconSize(QSize(14, 14))
        self.btn_del.clicked.connect(self.eliminar)
        footer.addWidget(self.lbl_total)
        footer.addStretch()
        footer.addWidget(self.btn_del)
        lay.addLayout(footer)

    def _on_theme(self, t):
        self.btn_nuevo.setIcon(svg_icon("add",    t["accent"]))
        self.btn_del.setIcon(svg_icon("delete", "#FFFFFF"))
        self.lbl_total.setStyleSheet(f"color: {t['text_muted']};")
        self.cargar()

    def recargar_cuentas(self):
        self.cmb_cuenta.blockSignals(True)
        self.cmb_cuenta.clear()
        self.cmb_cuenta.addItem("Todas las cuentas", None)
        for c in db.obtener_cuentas(self._user["id"]):
            self.cmb_cuenta.addItem(c[2], c[0])
        self.cmb_cuenta.blockSignals(False)
        self.cargar()

    def cargar(self):
        cid  = self.cmb_cuenta.currentData()
        tipo = self.cmb_tipo.currentText()
        txt  = self.inp_buscar.text().lower()
        t    = TM.t
        self._datos = db.obtener_movimientos(self._user["id"], cid)
        filas = [
            r for r in self._datos
            if (tipo == "Todos los tipos" or r[2] == tipo)
            and (not txt or txt in (r[4] or "").lower())
        ]
        self.tabla.setRowCount(len(filas))
        for i, r in enumerate(filas):
            vals = [r[1], r[2], r[3] or "", r[4] or "",
                    fmt_money(r[5]), r[6], r[7] or ""]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, r[0])
                if j == 1:
                    color = t["ingreso"] if val == "ingreso" else t["egreso"]
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                    item.setText(val.capitalize())
                if j == 4:
                    color = t["ingreso"] if r[2] == "ingreso" else t["egreso"]
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.tabla.setItem(i, j, item)
            self.tabla.setRowHeight(i, 42)
        self.lbl_total.setText(f"{len(filas)} movimiento{'s' if len(filas) != 1 else ''}")

    def nuevo_movimiento(self):
        cid = self.cmb_cuenta.currentData()
        dlg = DialogMovimiento(self._user["id"], cid, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar()
            mw = self.window()
            if hasattr(mw, "tab_dash"):
                mw.tab_dash.actualizar()
            if hasattr(mw, "tab_cuentas"):
                mw.tab_cuentas.cargar()
            if hasattr(mw, "tab_presupuesto"):
                mw.tab_presupuesto.cargar()   

    def eliminar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un movimiento primero.")
            return
        mov_id = self.tabla.item(row, 0).data(Qt.ItemDataRole.UserRole)
        resp = QMessageBox.question(
            self, "Confirmar",
            "¿Eliminar este movimiento? Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            db.eliminar_movimiento(mov_id)
            self.cargar()
            mw = self.window()
            if hasattr(mw, "tab_dash"):
                mw.tab_dash.actualizar()

# ── Tab Cuentas ───────────────────────────────────────────
class TabCuentas(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self._user = user
        self._build_ui()
        TM.theme_changed.connect(lambda t: self.cargar())

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel("Mis cuentas")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.btn_nueva = QPushButton("  Nueva cuenta")
        self.btn_nueva.setObjectName("btn_icon")
        self.btn_nueva.setIcon(svg_icon("add", TM.t["accent"]))
        self.btn_nueva.setIconSize(QSize(14, 14))
        self.btn_nueva.clicked.connect(self.nueva_cuenta)
        TM.theme_changed.connect(
            lambda t: self.btn_nueva.setIcon(svg_icon("add", t["accent"]))
        )
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.btn_nueva)
        lay.addLayout(top)

        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(14)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.scroll_content)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        lay.addWidget(scroll)

    def cargar(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.deleteLater()

        cuentas = db.obtener_cuentas(self._user["id"])
        t = TM.t

        if not cuentas:
            lbl = QLabel("No hay cuentas creadas.\nHaz clic en 'Nueva cuenta' para comenzar.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {t['text_muted']}; font-size: 14px; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0, 1, 3)
            return

        for idx, c in enumerate(cuentas):
            resumen = db.obtener_resumen(self._user["id"], c[0])
            f = card()
            f.setMinimumHeight(152)
            cl = QVBoxLayout(f)
            cl.setContentsMargins(22, 18, 22, 18)
            cl.setSpacing(8)

            head = QHBoxLayout()
            nombre = QLabel(c[2])
            nombre.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            badge = QLabel(c[4])
            badge.setStyleSheet(f"""
                background: {t['bg_input']}; color: {t['text_muted']};
                border-radius: 4px; padding: 2px 10px;
                font-size: 11px; font-weight: 700;
            """)
            head.addWidget(nombre)
            head.addStretch()
            head.addWidget(badge)
            cl.addLayout(head)

            if c[3]:
                desc = QLabel(c[3])
                desc.setStyleSheet(f"color: {t['text_muted']}; font-size: 12px;")
                cl.addWidget(desc)

            cl.addWidget(h_line())

            saldo_color = t["accent"] if resumen["saldo"] >= 0 else t["egreso"]
            saldo_lbl = QLabel(fmt_money(resumen["saldo"]))
            saldo_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.ExtraBold))
            saldo_lbl.setStyleSheet(f"color: {saldo_color};")
            cl.addWidget(saldo_lbl)

            stats = QHBoxLayout()
            ing = QLabel(f"Ingresos  {fmt_money(resumen['ingresos'])}")
            ing.setStyleSheet(f"color: {t['ingreso']}; font-size: 12px; font-weight: 600;")
            egr = QLabel(f"Egresos  {fmt_money(resumen['egresos'])}")
            egr.setStyleSheet(f"color: {t['egreso']}; font-size: 12px; font-weight: 600;")
            btn_del = QPushButton("  Eliminar")
            btn_del.setObjectName("btn_danger")
            btn_del.setIcon(svg_icon("delete", "#FFFFFF"))
            btn_del.setIconSize(QSize(13, 13))
            btn_del.setFixedHeight(30)
            btn_del.setFixedWidth(105)
            btn_del.clicked.connect(lambda checked, cid=c[0]: self.eliminar(cid))
            stats.addWidget(ing)
            stats.addSpacing(16)
            stats.addWidget(egr)
            stats.addStretch()
            stats.addWidget(btn_del)
            cl.addLayout(stats)

            self.grid.addWidget(f, idx // 3, idx % 3)

        for col in range(3):
            self.grid.setColumnStretch(col, 1)

    def nueva_cuenta(self):
        dlg = DialogCuenta(self._user["id"], self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar()
            mw = self.window()
            if hasattr(mw, "tab_dash"): mw.tab_dash.recargar_cuentas()
            if hasattr(mw, "tab_mov"):  mw.tab_mov.recargar_cuentas()

    def eliminar(self, cid):
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Eliminar esta cuenta y todos sus movimientos?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            db.eliminar_cuenta(cid)
            self.cargar()
            mw = self.window()
            if hasattr(mw, "tab_dash"): mw.tab_dash.recargar_cuentas()
            if hasattr(mw, "tab_mov"):  mw.tab_mov.recargar_cuentas()

# ── Dialog: Nuevo Presupuesto ─────────────────────────────
class DialogPresupuesto(QDialog):
    def __init__(self, user_id, mes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo presupuesto")
        self.setMinimumWidth(380)
        self.setStyleSheet(build_stylesheet(TM.t))
        self._user_id = user_id
        self._mes     = mes or datetime.now().strftime("%Y-%m")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(18)
        lay.setContentsMargins(28, 28, 28, 28)

        title = QLabel("Nuevo presupuesto")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        lay.addWidget(title)
        lay.addWidget(h_line())

        form = QFormLayout()
        form.setSpacing(13)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Solo categorías de egreso
        self.inp_cat = QComboBox()
        for cat in db.obtener_categorias("egreso"):
            self.inp_cat.addItem(cat[1])
        form.addRow("Categoría *", self.inp_cat)

        self.inp_limite = QDoubleSpinBox()
        self.inp_limite.setRange(1, 999_999_999)
        self.inp_limite.setDecimals(0)
        self.inp_limite.setSingleStep(10_000)
        self.inp_limite.setPrefix("$ ")
        form.addRow("Límite mensual *", self.inp_limite)

        # Mes
        try:
            dt = datetime.strptime(self._mes, "%Y-%m")
            mes_label = dt.strftime("%B %Y").capitalize()
        except Exception:
            mes_label = self._mes
        lbl_mes = QLabel(mes_label)
        lbl_mes.setStyleSheet(f"color: {TM.t['accent']}; font-weight: 700;")
        form.addRow("Mes", lbl_mes)

        lay.addLayout(form)
        lay.addSpacerItem(QSpacerItem(0, 8))

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("  Guardar presupuesto")
        btn_ok.setIcon(svg_icon("add", TM.t["text_inverse"]))
        btn_ok.setIconSize(QSize(14, 14))
        btn_ok.clicked.connect(self._guardar)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

    def _guardar(self):
        db.crear_presupuesto(
            self._user_id,
            self.inp_cat.currentText(),
            self.inp_limite.value(),
            self._mes
        )
        self.accept()

# ── Tab Presupuestos ──────────────────────────────────────
class TabPresupuestos(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self._user = user
        self._mes_actual = datetime.now().strftime("%Y-%m")
        self._build_ui()
        TM.theme_changed.connect(lambda t: self.cargar())

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        # ── Toolbar ──
        top = QHBoxLayout()
        top.setSpacing(12)

        title = QLabel("Presupuestos mensuales")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))

        lbl_mes = QLabel("Mes:")
        lbl_mes.setStyleSheet(f"color: {TM.t['text_muted']};")

        self.cmb_mes = QComboBox()
        self.cmb_mes.setMinimumWidth(140)
        self._poblar_meses()
        self.cmb_mes.currentIndexChanged.connect(self.cargar)

        self.btn_nuevo = QPushButton("  Nuevo presupuesto")
        self.btn_nuevo.setObjectName("btn_icon")
        self.btn_nuevo.setIcon(svg_icon("add", TM.t["accent"]))
        self.btn_nuevo.setIconSize(QSize(14, 14))
        self.btn_nuevo.clicked.connect(self.nuevo_presupuesto)
        TM.theme_changed.connect(
            lambda t: self.btn_nuevo.setIcon(svg_icon("add", t["accent"]))
        )

        top.addWidget(title)
        top.addStretch()
        top.addWidget(lbl_mes)
        top.addWidget(self.cmb_mes)
        top.addWidget(self.btn_nuevo)
        lay.addLayout(top)

        # ── Leyenda de estados ──
        leyenda = QHBoxLayout()
        leyenda.setSpacing(20)
        for color, texto in [
            ("#3DD68C", "Dentro del presupuesto"),
            ("#F0A500", "Advertencia  (>80%)"),
            ("#F85149", "Presupuesto excedido"),
        ]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            lbl = QLabel(texto)
            lbl.setStyleSheet(f"color: {TM.t['text_muted']}; font-size: 12px;")
            leyenda.addWidget(dot)
            leyenda.addWidget(lbl)
        leyenda.addStretch()
        lay.addLayout(leyenda)

        # ── Área de tarjetas ──
        self.scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_content)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.scroll_content)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        lay.addWidget(scroll)

        # ── Resumen total ──
        self.card_resumen = card()
        res_lay = QHBoxLayout(self.card_resumen)
        res_lay.setContentsMargins(20, 14, 20, 14)
        res_lay.setSpacing(32)
        self.lbl_total_presup  = QLabel("Total presupuestado: $ 0")
        self.lbl_total_gastado = QLabel("Total gastado: $ 0")
        self.lbl_disponible    = QLabel("Disponible: $ 0")
        for lbl in [self.lbl_total_presup, self.lbl_total_gastado, self.lbl_disponible]:
            lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            res_lay.addWidget(lbl)
        res_lay.addStretch()
        lay.addWidget(self.card_resumen)

    def _poblar_meses(self):
        self.cmb_mes.blockSignals(True)
        self.cmb_mes.clear()
        # Mes actual siempre primero
        ahora = datetime.now()
        meses_set = set()
        # Últimos 12 meses
        for i in range(12):
            m = ahora.month - i
            y = ahora.year
            while m <= 0:
                m += 12
                y -= 1
            meses_set.add(f"{y:04d}-{m:02d}")
        # Meses con movimientos
        for m in db.obtener_meses_con_movimientos(self._user["id"]):
            meses_set.add(m)
        meses_sorted = sorted(meses_set, reverse=True)
        for m in meses_sorted:
            try:
                dt = datetime.strptime(m, "%Y-%m")
                label = dt.strftime("%B %Y").capitalize()
            except Exception:
                label = m
            self.cmb_mes.addItem(label, m)
        self.cmb_mes.blockSignals(False)

    def cargar(self):
        # Limpiar tarjetas
        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        mes = self.cmb_mes.currentData() or self._mes_actual
        presupuestos = db.obtener_presupuestos(self._user["id"], mes)
        t = TM.t

        if not presupuestos:
            lbl = QLabel("No hay presupuestos para este mes.\nHaz clic en 'Nuevo presupuesto' para comenzar.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {t['text_muted']}; font-size: 14px; padding: 40px;")
            self.cards_layout.addWidget(lbl)
            self._actualizar_resumen(0, 0, t)
            return

        total_limite = 0
        total_gastado = 0

        for p in presupuestos:
            # p: id, categoria, monto_limite, mes, gastado
            pid, categoria, limite, mes_p, gastado = p
            pct = min(gastado / limite, 1.0) if limite > 0 else 0
            pct_real = gastado / limite if limite > 0 else 0

            if pct_real >= 1.0:
                color_barra = t["egreso"]
                estado = "EXCEDIDO"
                color_estado = t["egreso"]
            elif pct_real >= 0.8:
                color_barra = "#F0A500"
                estado = "ADVERTENCIA"
                color_estado = "#F0A500"
            else:
                color_barra = t["ingreso"]
                estado = "OK"
                color_estado = t["ingreso"]

            # Tarjeta
            f = card()
            f.setMinimumHeight(90)
            cl = QVBoxLayout(f)
            cl.setContentsMargins(20, 14, 20, 14)
            cl.setSpacing(8)

            # Fila superior
            row1 = QHBoxLayout()
            lbl_cat = QLabel(categoria)
            lbl_cat.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

            lbl_estado = QLabel(estado)
            lbl_estado.setStyleSheet(f"""
                color: {color_estado};
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                padding: 2px 8px;
                border: 1px solid {color_estado};
                border-radius: 4px;
            """)

            btn_del = QPushButton()
            btn_del.setObjectName("btn_icon")
            btn_del.setIcon(svg_icon("delete", t["text_muted"]))
            btn_del.setIconSize(QSize(13, 13))
            btn_del.setFixedSize(28, 28)
            btn_del.setToolTip("Eliminar presupuesto")
            btn_del.clicked.connect(lambda checked, i=pid: self._eliminar(i))

            row1.addWidget(lbl_cat)
            row1.addStretch()
            row1.addWidget(lbl_estado)
            row1.addSpacing(8)
            row1.addWidget(btn_del)
            cl.addLayout(row1)

            # Barra de progreso personalizada
            barra_bg = QFrame()
            barra_bg.setFixedHeight(8)
            barra_bg.setStyleSheet(f"""
                background: {t['bg_input']};
                border-radius: 4px;
            """)
            barra_bg_lay = QHBoxLayout(barra_bg)
            barra_bg_lay.setContentsMargins(0, 0, 0, 0)
            barra_bg_lay.setSpacing(0)

            barra_fill = QFrame()
            barra_fill.setFixedHeight(8)
            ancho_pct = max(int(pct * 100), 2) if gastado > 0 else 0
            barra_fill.setStyleSheet(f"""
                background: {color_barra};
                border-radius: 4px;
            """)
            barra_fill.setFixedWidth(0)  # se ajusta abajo
            barra_fill.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            # Usamos QLabel con width% via stylesheet trick
            contenedor_barra = QWidget()
            contenedor_barra.setFixedHeight(8)
            contenedor_barra.setStyleSheet(f"background: {t['bg_input']}; border-radius: 4px;")
            barra_interior = QFrame(contenedor_barra)
            barra_interior.setStyleSheet(f"background: {color_barra}; border-radius: 4px;")
            barra_interior.setFixedHeight(8)
            # El ancho se establece en resizeEvent, usamos proporción guardada
            contenedor_barra.setProperty("pct", pct)
            contenedor_barra.setProperty("color", color_barra)
            contenedor_barra.setProperty("bg", t["bg_input"])
            cl.addWidget(contenedor_barra)

            # Fila inferior: montos
            row2 = QHBoxLayout()
            lbl_gastado = QLabel(f"Gastado: {fmt_money(gastado)}")
            lbl_gastado.setStyleSheet(f"color: {color_barra}; font-size: 12px; font-weight: 700;")
            lbl_limite = QLabel(f"Límite: {fmt_money(limite)}")
            lbl_limite.setStyleSheet(f"color: {t['text_muted']}; font-size: 12px;")
            lbl_restante_val = limite - gastado
            lbl_restante = QLabel(
                f"Disponible: {fmt_money(lbl_restante_val)}" if lbl_restante_val >= 0
                else f"Exceso: {fmt_money(abs(lbl_restante_val))}"
            )
            lbl_restante.setStyleSheet(f"color: {t['text_muted']}; font-size: 12px;")
            row2.addWidget(lbl_gastado)
            row2.addStretch()
            row2.addWidget(lbl_limite)
            row2.addSpacing(16)
            row2.addWidget(lbl_restante)
            cl.addLayout(row2)

            self.cards_layout.addWidget(f)

            # Ajustar barra después de agregar al layout
            self._ajustar_barra(contenedor_barra, barra_interior)

            total_limite  += limite
            total_gastado += gastado

        self._actualizar_resumen(total_limite, total_gastado, t)

    def _ajustar_barra(self, contenedor, barra):
        """Ajusta el ancho de la barra de progreso."""
        pct = contenedor.property("pct") or 0
        def resize_barra():
            w = contenedor.width()
            barra.setFixedWidth(max(int(w * pct), 0))
            barra.setFixedHeight(8)
        # Diferir para que el widget ya tenga tamaño
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, resize_barra)

    def _actualizar_resumen(self, total_limite, total_gastado, t):
        disponible = total_limite - total_gastado
        color_disp = t["ingreso"] if disponible >= 0 else t["egreso"]
        self.lbl_total_presup.setText(f"Total presupuestado: {fmt_money(total_limite)}")
        self.lbl_total_presup.setStyleSheet(f"color: {t['text_primary']}; font-size: 12px; font-weight: 700;")
        self.lbl_total_gastado.setText(f"Total gastado: {fmt_money(total_gastado)}")
        self.lbl_total_gastado.setStyleSheet(f"color: {t['egreso']}; font-size: 12px; font-weight: 700;")
        self.lbl_disponible.setText(
            f"Disponible: {fmt_money(disponible)}" if disponible >= 0
            else f"Exceso total: {fmt_money(abs(disponible))}"
        )
        self.lbl_disponible.setStyleSheet(f"color: {color_disp}; font-size: 12px; font-weight: 700;")

    def nuevo_presupuesto(self):
        dlg = DialogPresupuesto(self._user["id"], self.cmb_mes.currentData(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cargar()

    def _eliminar(self, pid):
        resp = QMessageBox.question(
            self, "Eliminar presupuesto",
            "¿Eliminar este presupuesto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            db.eliminar_presupuesto(pid)
            self.cargar()

# ── Ventana Principal ─────────────────────────────────────
class MainWindow(QMainWindow):
    cerrar_sesion = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self._user = user
        self.setWindowTitle("Flujo de Caja")
        self.setMinimumSize(1060, 700)
        self._build_ui()
        self._apply_theme()
        TM.theme_changed.connect(self._apply_theme)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        self.header = QFrame()
        self.header.setObjectName("header_frame")
        self.header.setFixedHeight(62)
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(26, 0, 26, 0)
        hl.setSpacing(14)

        self.logo_icon = QLabel()
        self.logo_icon.setFixedSize(22, 22)
        self.logo_lbl = QLabel("Flujo de Caja")
        self.logo_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))

        self.lbl_fecha = QLabel(datetime.now().strftime("%d de %B de %Y"))
        self.lbl_fecha.setFont(QFont("Segoe UI", 11))

        # Usuario activo
        self.lbl_user = QLabel()
        self.lbl_user.setFont(QFont("Segoe UI", 11))
        self.user_icon = QLabel()
        self.user_icon.setFixedSize(16, 16)

        # Toggle tema
        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("btn_toggle_theme")
        self.btn_theme.setFixedHeight(34)
        self.btn_theme.clicked.connect(TM.toggle)

        # Cerrar sesión
        self.btn_logout = QPushButton("  Cerrar sesión")
        self.btn_logout.setObjectName("btn_secondary")
        self.btn_logout.setFixedHeight(34)
        self.btn_logout.setIcon(svg_icon("logout", TM.t["text_muted"]))
        self.btn_logout.setIconSize(QSize(14, 14))
        self.btn_logout.clicked.connect(self._logout)

        hl.addWidget(self.logo_icon)
        hl.addWidget(self.logo_lbl)
        hl.addStretch()
        hl.addWidget(self.lbl_fecha)
        hl.addSpacing(10)
        hl.addWidget(self.user_icon)
        hl.addWidget(self.lbl_user)
        hl.addSpacing(4)
        hl.addWidget(self.btn_theme)
        hl.addWidget(self.btn_logout)
        root.addWidget(self.header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tab_dash       = TabDashboard(self._user)
        self.tab_mov        = TabMovimientos(self._user)
        self.tab_cuentas    = TabCuentas(self._user)
        self.tab_presupuesto = TabPresupuestos(self._user)

        self.tabs.addTab(self.tab_dash,        "  Dashboard  ")
        self.tabs.addTab(self.tab_mov,         "  Movimientos  ")
        self.tabs.addTab(self.tab_cuentas,     "  Cuentas  ")
        self.tabs.addTab(self.tab_presupuesto, "  Presupuestos  ")
        self.tabs.setIconSize(QSize(16, 16))
        root.addWidget(self.tabs)

        # Cargar datos
        self.tab_dash.recargar_cuentas()
        self.tab_mov.recargar_cuentas()
        self.tab_cuentas.cargar()

    def _apply_theme(self, t=None):
        if t is None: t = TM.t
        self.setStyleSheet(build_stylesheet(t))
        self.logo_lbl.setStyleSheet(f"color: {t['accent']};")
        self.lbl_fecha.setStyleSheet(f"color: {t['text_muted']};")
        self.lbl_user.setText(self._user["nombre"])
        self.lbl_user.setStyleSheet(f"color: {t['text_muted']}; font-size: 12px;")
        self.logo_icon.setPixmap(svg_pix("accounts", t["accent"], 22))
        self.user_icon.setPixmap(svg_pix("user", t["text_muted"], 15))
        self.btn_logout.setIcon(svg_icon("logout", t["text_muted"]))

        if TM.is_dark:
            self.btn_theme.setText("  Modo claro")
            self.btn_theme.setIcon(svg_icon("sun",  t["text_muted"], 15))
        else:
            self.btn_theme.setText("  Modo oscuro")
            self.btn_theme.setIcon(svg_icon("moon", t["text_muted"], 15))
        self.btn_theme.setIconSize(QSize(14, 14))

        self.tabs.setTabIcon(0, svg_icon("dashboard", t["text_muted"]))
        self.tabs.setTabIcon(1, svg_icon("movements", t["text_muted"]))
        self.tabs.setTabIcon(2, svg_icon("accounts",  t["text_muted"]))
        self.tabs.setTabIcon(3, svg_icon("budget",    t["text_muted"]))

    def _logout(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Estás seguro que deseas cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.cerrar_sesion.emit()


# ── App Controller ────────────────────────────────────────
class AppController:
    """Controla el flujo entre login y la app principal."""

    def __init__(self):
        self.auth_window = None
        self.main_window = None

    def start(self):
        self._mostrar_auth()

    def _mostrar_auth(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.auth_window = VentanaAuth(TM)
        self.auth_window.setWindowTitle("Flujo de Caja — Acceso")
        self.auth_window.resize(800, 560)
        self.auth_window.setStyleSheet(build_stylesheet(TM.t))
        self.auth_window.autenticado.connect(self._mostrar_app)
        TM.theme_changed.connect(
            lambda t: self.auth_window.setStyleSheet(build_stylesheet(t))
            if self.auth_window else None
        )
        self.auth_window.show()

    def _mostrar_app(self, user):
        if self.auth_window:
            self.auth_window.close()
            self.auth_window = None

        self.main_window = MainWindow(user)
        self.main_window.cerrar_sesion.connect(self._mostrar_auth)
        self.main_window.show()


# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    db.init_db()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    controller = AppController()
    controller.start()
    sys.exit(app.exec())