# themes.py

DARK = {
    "bg_main":      "#0D1117",
    "bg_card":      "#161B22",
    "bg_input":     "#1C2128",
    "bg_header":    "#161B22",
    "border":       "#30363D",
    "accent":       "#00C896",
    "accent_hover": "#00A87E",
    "accent_press": "#008F6B",
    "ingreso":      "#3DD68C",
    "egreso":       "#F85149",
    "text_primary": "#E6EDF3",
    "text_muted":   "#7D8590",
    "text_inverse": "#0D1117",
    "row_alt":      "#1A2030",
    "shadow":       "rgba(0,0,0,0.4)",
    "tab_selected_bg": "#1C2128",
}

LIGHT = {
    "bg_main":      "#F4F6F9",
    "bg_card":      "#FFFFFF",
    "bg_input":     "#F0F2F5",
    "bg_header":    "#FFFFFF",
    "border":       "#D8DEE9",
    "accent":       "#0A7C5C",
    "accent_hover": "#086B4E",
    "accent_press": "#065A42",
    "ingreso":      "#1A8A55",
    "egreso":       "#C0392B",
    "text_primary": "#1A202C",
    "text_muted":   "#6B7A90",
    "text_inverse": "#FFFFFF",
    "row_alt":      "#F8FAFC",
    "shadow":       "rgba(0,0,0,0.08)",
    "tab_selected_bg": "#F0F2F5",
}


def build_stylesheet(t: dict) -> str:
    return f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background-color: {t['bg_main']};
    color: {t['text_primary']};
    font-family: 'Segoe UI';
    font-size: 13px;
}}

/* ── Tabs ── */
QTabWidget::pane {{
    border: 1px solid {t['border']};
    background: {t['bg_card']};
    border-radius: 10px;
    margin-top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {t['text_muted']};
    padding: 11px 28px;
    border: none;
    font-size: 13px;
    font-weight: 500;
    min-width: 120px;
}}
QTabBar::tab:selected {{
    color: {t['accent']};
    background: {t['tab_selected_bg']};
    border-bottom: 2px solid {t['accent']};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    color: {t['text_primary']};
    background: {t['bg_input']};
}}

/* ── Table ── */
QTableWidget {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    gridline-color: {t['border']};
    selection-background-color: {t['accent']}22;
    outline: none;
    alternate-background-color: {t['row_alt']};
}}
QTableWidget::item {{
    padding: 6px 14px;
    border: none;
}}
QTableWidget::item:selected {{
    background: {t['accent']}22;
    color: {t['text_primary']};
}}
QHeaderView::section {{
    background: {t['bg_input']};
    color: {t['text_muted']};
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid {t['border']};
    border-right: 1px solid {t['border']};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── Inputs ── */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {{
    background: {t['bg_input']};
    border: 1px solid {t['border']};
    border-radius: 7px;
    color: {t['text_primary']};
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {t['accent']}44;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QDateEdit:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {t['accent']};
    background: {t['bg_card']};
}}
QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QDoubleSpinBox:hover {{
    border-color: {t['text_muted']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    selection-background-color: {t['accent']}33;
    color: {t['text_primary']};
    padding: 4px;
    outline: none;
}}
QDateEdit::drop-down {{
    border: none;
    width: 24px;
}}
QCalendarWidget {{
    background: {t['bg_card']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
}}
QCalendarWidget QToolButton {{
    background: {t['bg_input']};
    color: {t['text_primary']};
    border-radius: 4px;
    padding: 4px 8px;
}}
QCalendarWidget QMenu {{
    background: {t['bg_card']};
    color: {t['text_primary']};
}}
QCalendarWidget QAbstractItemView {{
    background: {t['bg_card']};
    color: {t['text_primary']};
    selection-background-color: {t['accent']};
    selection-color: {t['text_inverse']};
}}

/* ── Buttons ── */
QPushButton {{
    background: {t['accent']};
    color: {t['text_inverse']};
    border: none;
    border-radius: 7px;
    padding: 9px 20px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.2px;
}}
QPushButton:hover {{
    background: {t['accent_hover']};
}}
QPushButton:pressed {{
    background: {t['accent_press']};
}}
QPushButton#btn_danger {{
    background: {t['egreso']};
    color: white;
}}
QPushButton#btn_danger:hover {{
    background: #C0392B;
}}
QPushButton#btn_secondary {{
    background: {t['bg_input']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    font-weight: 600;
}}
QPushButton#btn_secondary:hover {{
    border-color: {t['accent']};
    color: {t['accent']};
    background: {t['accent']}11;
}}
QPushButton#btn_icon {{
    background: transparent;
    color: {t['text_muted']};
    border: 1px solid {t['border']};
    border-radius: 7px;
    padding: 7px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#btn_icon:hover {{
    border-color: {t['accent']};
    color: {t['accent']};
    background: {t['accent']}11;
}}
QPushButton#btn_toggle_theme {{
    background: {t['bg_input']};
    color: {t['text_muted']};
    border: 1px solid {t['border']};
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
    min-width: 110px;
}}
QPushButton#btn_toggle_theme:hover {{
    border-color: {t['accent']};
    color: {t['accent']};
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t['border']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {t['border']};
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Frame/Card ── */
QFrame#card {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 10px;
}}
QFrame#header_frame {{
    background: {t['bg_header']};
    border-bottom: 1px solid {t['border']};
}}

/* ── Dialogs ── */
QDialog {{
    background: {t['bg_card']};
}}
QMessageBox {{
    background: {t['bg_card']};
}}
QMessageBox QPushButton {{
    min-width: 80px;
}}

/* ── Labels ── */
QLabel#lbl_section_title {{
    font-size: 15px;
    font-weight: 700;
    color: {t['text_primary']};
}}
QLabel#lbl_muted {{
    color: {t['text_muted']};
    font-size: 12px;
}}
QLabel#lbl_kpi_value {{
    font-size: 22px;
    font-weight: 800;
}}
QLabel#lbl_kpi_label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
    color: {t['text_muted']};
}}
QLabel#lbl_badge {{
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 700;
}}

/* ── Separators ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {t['border']};
}}

/* ── ToolTip ── */
QToolTip {{
    background: {t['bg_card']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 12px;
}}
"""