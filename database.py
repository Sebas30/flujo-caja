# database.py
import sqlite3
import bcrypt

DB_PATH = "flujo_caja.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Cuentas
    c.execute('''CREATE TABLE IF NOT EXISTS cuentas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        tipo TEXT NOT NULL,
        saldo_inicial REAL DEFAULT 0,
        fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    )''')

    # Movimientos
    c.execute('''CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cuenta_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        categoria TEXT,
        descripcion TEXT,
        monto REAL NOT NULL,
        fecha TEXT NOT NULL,
        notas TEXT,
        FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
    )''')

    # Categorías
    c.execute('''CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        color TEXT DEFAULT '#4CAF50'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS presupuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        categoria TEXT NOT NULL,
        monto_limite REAL NOT NULL,
        mes TEXT NOT NULL,
        UNIQUE(user_id, categoria, mes),
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    )''')

    categorias_default = [
        ("Ventas",            "ingreso", "#3DD68C"),
        ("Servicios",         "ingreso", "#3498DB"),
        ("Inversiones",       "ingreso", "#9B59B6"),
        ("Cobros",            "ingreso", "#1ABC9C"),
        ("Otros ingresos",    "ingreso", "#F0A500"),
        ("Nómina",            "egreso",  "#F85149"),
        ("Arriendo",          "egreso",  "#E67E22"),
        ("Servicios públicos","egreso",  "#F39C12"),
        ("Proveedores",       "egreso",  "#C0392B"),
        ("Marketing",         "egreso",  "#8E44AD"),
        ("Impuestos",         "egreso",  "#E74C3C"),
        ("Otros gastos",      "egreso",  "#7F8C8D"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO categorias (nombre, tipo, color) VALUES (?, ?, ?)",
        categorias_default
    )
    conn.commit()
    conn.close()

# ── Usuarios ──────────────────────────────────────────────

def registrar_usuario(nombre, email, password):
    """Registra un nuevo usuario. Retorna (True, user) o (False, mensaje)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE email = ?", (email.lower().strip(),))
    if c.fetchone():
        conn.close()
        return False, "Ya existe una cuenta con ese correo."
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    c.execute(
        "INSERT INTO usuarios (nombre, email, password_hash) VALUES (?, ?, ?)",
        (nombre.strip(), email.lower().strip(), pw_hash)
    )
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return True, {"id": user_id, "nombre": nombre.strip(), "email": email.lower().strip()}

def login_usuario(email, password):
    """Verifica credenciales. Retorna (True, user) o (False, mensaje)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, nombre, email, password_hash FROM usuarios WHERE email = ?",
        (email.lower().strip(),)
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "No existe una cuenta con ese correo."
    if not bcrypt.checkpw(password.encode(), row[3].encode()):
        return False, "Contraseña incorrecta."
    return True, {"id": row[0], "nombre": row[1], "email": row[2]}

# ── Cuentas ───────────────────────────────────────────────

def crear_cuenta(user_id, nombre, descripcion, tipo, saldo_inicial=0):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO cuentas (user_id, nombre, descripcion, tipo, saldo_inicial) VALUES (?, ?, ?, ?, ?)",
        (user_id, nombre, descripcion, tipo, saldo_inicial)
    )
    conn.commit()
    conn.close()

def obtener_cuentas(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cuentas WHERE user_id = ? ORDER BY nombre", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def eliminar_cuenta(cuenta_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM movimientos WHERE cuenta_id = ?", (cuenta_id,))
    c.execute("DELETE FROM cuentas WHERE id = ?", (cuenta_id,))
    conn.commit()
    conn.close()

# ── Movimientos ───────────────────────────────────────────

def agregar_movimiento(cuenta_id, tipo, categoria, descripcion, monto, fecha, notas=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO movimientos (cuenta_id, tipo, categoria, descripcion, monto, fecha, notas) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (cuenta_id, tipo, categoria, descripcion, monto, fecha, notas)
    )
    conn.commit()
    conn.close()

def obtener_movimientos(user_id, cuenta_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT m.id, cu.nombre, m.tipo, m.categoria, m.descripcion, m.monto, m.fecha, m.notas
        FROM movimientos m
        JOIN cuentas cu ON m.cuenta_id = cu.id
        WHERE cu.user_id = ?
    """
    params = [user_id]
    if cuenta_id:
        query += " AND m.cuenta_id = ?"
        params.append(cuenta_id)
    query += " ORDER BY m.fecha DESC, m.id DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def eliminar_movimiento(mov_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM movimientos WHERE id = ?", (mov_id,))
    conn.commit()
    conn.close()

# ── Resumen y gráficas ────────────────────────────────────

def obtener_resumen(user_id, cuenta_id=None):
    conn = get_connection()
    c = conn.cursor()
    if cuenta_id:
        filtro  = "WHERE m.cuenta_id = ?"
        params  = [cuenta_id]
        c.execute("SELECT saldo_inicial FROM cuentas WHERE id = ?", [cuenta_id])
        row = c.fetchone()
        saldo_inicial = row[0] if row else 0
    else:
        filtro  = "WHERE cu.user_id = ?"
        params  = [user_id]
        c.execute("SELECT COALESCE(SUM(saldo_inicial),0) FROM cuentas WHERE user_id = ?", [user_id])
        saldo_inicial = c.fetchone()[0]

    base = f"""
        FROM movimientos m
        JOIN cuentas cu ON m.cuenta_id = cu.id
        {filtro}
    """
    c.execute(f"SELECT COALESCE(SUM(m.monto),0) {base} AND m.tipo='ingreso'", params)
    ingresos = c.fetchone()[0]
    c.execute(f"SELECT COALESCE(SUM(m.monto),0) {base} AND m.tipo='egreso'", params)
    egresos = c.fetchone()[0]
    conn.close()
    return {"ingresos": ingresos, "egresos": egresos,
            "saldo": saldo_inicial + ingresos - egresos}

def obtener_flujo_mensual(user_id, cuenta_id=None):
    conn = get_connection()
    c = conn.cursor()
    if cuenta_id:
        filtro = "AND m.cuenta_id = ?"
        params = [cuenta_id]
    else:
        filtro = "AND cu.user_id = ?"
        params = [user_id]
    c.execute(f"""
        SELECT strftime('%Y-%m', m.fecha) as mes,
               SUM(CASE WHEN m.tipo='ingreso' THEN m.monto ELSE 0 END),
               SUM(CASE WHEN m.tipo='egreso'  THEN m.monto ELSE 0 END)
        FROM movimientos m
        JOIN cuentas cu ON m.cuenta_id = cu.id
        WHERE 1=1 {filtro}
        GROUP BY mes ORDER BY mes
    """, params)
    rows = c.fetchall()
    conn.close()
    return rows

def obtener_categorias(tipo=None):
    conn = get_connection()
    c = conn.cursor()
    if tipo:
        c.execute("SELECT * FROM categorias WHERE tipo=? ORDER BY nombre", (tipo,))
    else:
        c.execute("SELECT * FROM categorias ORDER BY nombre")
    rows = c.fetchall()
    conn.close()
    return rows

# ── Presupuestos ──────────────────────────────────────────

def crear_presupuesto(user_id, categoria, monto_limite, mes):
    """mes formato: '2024-01'"""
    conn = get_connection()
    c = conn.cursor()
    # Si ya existe uno para esa categoría y mes, lo actualiza
    c.execute("""
        INSERT INTO presupuestos (user_id, categoria, monto_limite, mes)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, categoria, mes) DO UPDATE SET monto_limite=excluded.monto_limite
    """, (user_id, categoria, monto_limite, mes))
    conn.commit()
    conn.close()

def obtener_presupuestos(user_id, mes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.categoria, p.monto_limite, p.mes,
               COALESCE(SUM(CASE WHEN m.tipo='egreso' AND m.categoria=p.categoria
                                  AND strftime('%Y-%m', m.fecha)=p.mes
                             THEN m.monto ELSE 0 END), 0) as gastado
        FROM presupuestos p
        LEFT JOIN movimientos m ON m.cuenta_id IN (
            SELECT id FROM cuentas WHERE user_id = ?
        )
        WHERE p.user_id = ? AND p.mes = ?
        GROUP BY p.id
        ORDER BY p.categoria
    """, (user_id, user_id, mes))
    rows = c.fetchall()
    conn.close()
    return rows

def eliminar_presupuesto(presupuesto_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM presupuestos WHERE id = ?", (presupuesto_id,))
    conn.commit()
    conn.close()

def obtener_meses_con_movimientos(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT strftime('%Y-%m', m.fecha) as mes
        FROM movimientos m
        JOIN cuentas cu ON m.cuenta_id = cu.id
        WHERE cu.user_id = ?
        ORDER BY mes DESC
    """, (user_id,))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows