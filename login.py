# login.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QStackedWidget, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from themes import build_stylesheet, DARK
import database as db

# Reutilizamos el helper svg_icon — se importa desde main en tiempo de ejecución
# para evitar importación circular; lo redefinimos mínimamente aquí.
import os
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")

def _svg_icon(name, color, size=18):
    from PyQt6.QtGui import QIcon
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
    from PyQt6.QtGui import QIcon
    return QIcon(pix)


def _pix(name, color, size=18):
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


# ── Panel de login ────────────────────────────────────────
class PanelLogin(QWidget):
    login_exitoso = pyqtSignal(dict)   # emite el dict del usuario
    ir_a_registro = pyqtSignal()

    def __init__(self, tm, parent=None):
        super().__init__(parent)
        self.tm = tm
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Contenedor centrado
        center = QHBoxLayout()
        center.addStretch(1)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(400)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 40, 40, 40)
        card_lay.setSpacing(16)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_pix = QLabel()
        self.logo_pix.setFixedSize(36, 36)
        logo_lbl = QLabel("Flujo de Caja")
        logo_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        logo_lbl.setStyleSheet(f"color: {self.tm.t['accent']};")
        logo_row.addWidget(self.logo_pix)
        logo_row.addWidget(logo_lbl)
        card_lay.addLayout(logo_row)

        subtitle = QLabel("Inicia sesión en tu cuenta")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.tm.t['text_muted']}; font-size: 13px;")
        card_lay.addWidget(subtitle)
        card_lay.addSpacing(8)

        # Campos
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("Correo electrónico")
        self.inp_email.setFixedHeight(42)

        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Contraseña")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setFixedHeight(42)
        self.inp_pass.returnPressed.connect(self._intentar_login)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet(f"color: {self.tm.t['egreso']}; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()

        btn_login = QPushButton("Iniciar sesión")
        btn_login.setFixedHeight(42)
        btn_login.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_login.clicked.connect(self._intentar_login)

        card_lay.addWidget(self.inp_email)
        card_lay.addWidget(self.inp_pass)
        card_lay.addWidget(self.lbl_error)
        card_lay.addWidget(btn_login)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self.tm.t['border']};")
        card_lay.addWidget(sep)

        # Ir a registro
        reg_row = QHBoxLayout()
        reg_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_reg = QLabel("¿No tienes cuenta?")
        lbl_reg.setStyleSheet(f"color: {self.tm.t['text_muted']}; font-size: 12px;")
        btn_reg = QPushButton("Regístrate")
        btn_reg.setObjectName("btn_secondary")
        btn_reg.setFlat(True)
        btn_reg.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.tm.t['accent']};
                border: none;
                font-size: 12px;
                font-weight: 700;
                padding: 0;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        btn_reg.clicked.connect(self.ir_a_registro)
        reg_row.addWidget(lbl_reg)
        reg_row.addWidget(btn_reg)
        card_lay.addLayout(reg_row)

        center.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)
        center.addStretch(1)
        root.addStretch(1)
        root.addLayout(center)
        root.addStretch(1)

        # Actualizar icono logo
        self._refresh_icons()

    def _refresh_icons(self):
        pix = _pix("accounts", self.tm.t["accent"], 32)
        self.logo_pix.setPixmap(pix)

    def _intentar_login(self):
        email = self.inp_email.text().strip()
        pw    = self.inp_pass.text()
        if not email or not pw:
            self._show_error("Completa todos los campos.")
            return
        ok, result = db.login_usuario(email, pw)
        if ok:
            self.lbl_error.hide()
            self.inp_pass.clear()
            self.login_exitoso.emit(result)
        else:
            self._show_error(result)

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self.lbl_error.show()


# ── Panel de registro ─────────────────────────────────────
class PanelRegistro(QWidget):
    registro_exitoso = pyqtSignal(dict)
    ir_a_login       = pyqtSignal()

    def __init__(self, tm, parent=None):
        super().__init__(parent)
        self.tm = tm
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        center = QHBoxLayout()
        center.addStretch(1)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 40, 40, 40)
        card_lay.setSpacing(14)

        # Encabezado
        title = QLabel("Crear cuenta")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title)

        subtitle = QLabel("Completa los datos para registrarte")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.tm.t['text_muted']}; font-size: 13px;")
        card_lay.addWidget(subtitle)
        card_lay.addSpacing(6)

        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre completo")
        self.inp_nombre.setFixedHeight(42)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("Correo electrónico")
        self.inp_email.setFixedHeight(42)

        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Contraseña (mínimo 6 caracteres)")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setFixedHeight(42)

        self.inp_pass2 = QLineEdit()
        self.inp_pass2.setPlaceholderText("Confirmar contraseña")
        self.inp_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass2.setFixedHeight(42)
        self.inp_pass2.returnPressed.connect(self._intentar_registro)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet(f"color: {self.tm.t['egreso']}; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()

        btn_reg = QPushButton("Crear cuenta")
        btn_reg.setFixedHeight(42)
        btn_reg.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_reg.clicked.connect(self._intentar_registro)

        card_lay.addWidget(self.inp_nombre)
        card_lay.addWidget(self.inp_email)
        card_lay.addWidget(self.inp_pass)
        card_lay.addWidget(self.inp_pass2)
        card_lay.addWidget(self.lbl_error)
        card_lay.addWidget(btn_reg)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self.tm.t['border']};")
        card_lay.addWidget(sep)

        back_row = QHBoxLayout()
        back_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_back = QLabel("¿Ya tienes cuenta?")
        lbl_back.setStyleSheet(f"color: {self.tm.t['text_muted']}; font-size: 12px;")
        btn_back = QPushButton("Inicia sesión")
        btn_back.setFlat(True)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.tm.t['accent']};
                border: none;
                font-size: 12px;
                font-weight: 700;
                padding: 0;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        btn_back.clicked.connect(self.ir_a_login)
        back_row.addWidget(lbl_back)
        back_row.addWidget(btn_back)
        card_lay.addLayout(back_row)

        center.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)
        center.addStretch(1)
        root.addStretch(1)
        root.addLayout(center)
        root.addStretch(1)

    def _intentar_registro(self):
        nombre = self.inp_nombre.text().strip()
        email  = self.inp_email.text().strip()
        pw     = self.inp_pass.text()
        pw2    = self.inp_pass2.text()

        if not all([nombre, email, pw, pw2]):
            self._show_error("Completa todos los campos.")
            return
        if "@" not in email or "." not in email:
            self._show_error("Ingresa un correo válido.")
            return
        if len(pw) < 6:
            self._show_error("La contraseña debe tener al menos 6 caracteres.")
            return
        if pw != pw2:
            self._show_error("Las contraseñas no coinciden.")
            return

        ok, result = db.registrar_usuario(nombre, email, pw)
        if ok:
            self.lbl_error.hide()
            self.inp_pass.clear()
            self.inp_pass2.clear()
            self.registro_exitoso.emit(result)
        else:
            self._show_error(result)

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self.lbl_error.show()


# ── Ventana de autenticación ──────────────────────────────
class VentanaAuth(QWidget):
    autenticado = pyqtSignal(dict)   # emite user dict al padre

    def __init__(self, tm, parent=None):
        super().__init__(parent)
        self.tm = tm
        self.setStyleSheet(build_stylesheet(tm.t))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.panel_login   = PanelLogin(tm)
        self.panel_registro = PanelRegistro(tm)

        self.stack.addWidget(self.panel_login)     # índice 0
        self.stack.addWidget(self.panel_registro)  # índice 1

        self.panel_login.login_exitoso.connect(self.autenticado)
        self.panel_login.ir_a_registro.connect(lambda: self.stack.setCurrentIndex(1))
        self.panel_registro.ir_a_login.connect(lambda: self.stack.setCurrentIndex(0))
        self.panel_registro.registro_exitoso.connect(self.autenticado)

        lay.addWidget(self.stack)

        tm.theme_changed.connect(self._on_theme)

    def _on_theme(self, t):
        self.setStyleSheet(build_stylesheet(t))