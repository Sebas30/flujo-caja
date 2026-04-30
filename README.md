# Flujo de Caja

Aplicación de escritorio para gestión de flujo de caja personal y empresarial, construida con Python y PyQt6.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/Licencia-MIT-orange?style=flat-square)

---

## Características

- **Autenticación** — registro e inicio de sesión con contraseñas hasheadas (bcrypt)
- **Multi-cuenta** — crea y gestiona múltiples cuentas por usuario (negocio, personal, proyecto, etc.)
- **Movimientos** — registra ingresos y egresos con categorías, fecha y notas
- **Dashboard** — KPIs en tiempo real y gráfica de flujo mensual
- **Presupuestos** — define límites por categoría con alertas visuales de progreso
- **Tema Dark / Light** — cambio de tema desde el header
- **Base de datos local** — SQLite, sin necesidad de servidor externo

---

## Requisitos del sistema

- Python **3.10 o superior**
- Windows 10/11 (también compatible con macOS y Linux)
- Conexión a internet solo para la instalación de dependencias

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/flujo-caja.git
cd flujo-caja
```

### 2. Verificar versión de Python

```bash
python --version
```

Debe mostrar `Python 3.10.x` o superior. Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/).

>  Durante la instalación de Python en Windows, marca la casilla **"Add Python to PATH"**.

### 3. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Sabrás que el entorno está activo cuando veas `(venv)` al inicio de tu terminal.

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python main.py
```

---

## Estructura del proyecto

```
flujo-caja/
├── icons/                  # Iconos SVG de la interfaz
│   ├── dashboard.svg
│   ├── movements.svg
│   ├── accounts.svg
│   ├── add.svg
│   ├── delete.svg
│   ├── budget.svg
│   ├── user.svg
│   ├── logout.svg
│   ├── sun.svg
│   └── moon.svg
├── venv/                   # Entorno virtual (no se sube al repo)
├── main.py                 # Ventana principal y todas las vistas
├── login.py                # Pantallas de login y registro
├── database.py             # Capa de datos — SQLite
├── themes.py               # Temas dark y light
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Este archivo
```

> La base de datos `flujo_caja.db` se genera automáticamente al ejecutar la app por primera vez.

---

## Dependencias principales

| Paquete | Versión mínima | Uso |
|---|---|---|
| PyQt6 | 6.4+ | Interfaz gráfica |
| matplotlib | 3.6+ | Gráficas de flujo mensual |
| pandas | 1.5+ | Manejo de datos |
| bcrypt | 4.0+ | Hash seguro de contraseñas |
| openpyxl | 3.0+ | Exportación a Excel |

---

## Primer uso

1. Ejecuta `python main.py`
2. Haz clic en **"Regístrate"** para crear tu cuenta
3. Inicia sesión con tu correo y contraseña
4. Crea tu primera cuenta desde la pestaña **Cuentas**
5. Registra movimientos desde la pestaña **Movimientos**
6. Define presupuestos por categoría en la pestaña **Presupuestos**
7. Visualiza tu flujo financiero en el **Dashboard**

---

## Seguridad

- Las contraseñas se almacenan hasheadas con **bcrypt** y salt aleatorio, nunca en texto plano
- Cada usuario accede únicamente a sus propios datos
- La base de datos es local — tus datos no salen de tu equipo

---

## Configuración del repositorio Git

Si vas a subir el proyecto a GitHub, crea un archivo `.gitignore` con el siguiente contenido para no subir archivos innecesarios:

```
# Entorno virtual
venv/

# Base de datos local
flujo_caja.db

# Caché de Python
__pycache__/
*.pyc
*.pyo

# Archivos del sistema
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
```

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor abre un *issue* primero para discutir los cambios que deseas realizar.

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.