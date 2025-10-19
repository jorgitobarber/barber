# app.py
# Barbería — Registro/Resumen con métricas y gráficos
# Tecnologías: Streamlit + SQLite + SQLAlchemy + Pandas + Plotly
# Moneda: CLP

import os
import uuid
import base64
import enum
import datetime as dt
from datetime import datetime, date, timedelta
import calendar
from statistics import mean, median
from collections import Counter

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

# =========================
# Streamlit — Config & CSS
# =========================
st.set_page_config(
    page_title="Barbería — Registro & Resumen",
    layout="wide",
    page_icon="✂️",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#1f77b4">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Barbería">
<meta name="mobile-web-app-capable" content="yes">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""",
    unsafe_allow_html=True,
)

# ======== Dark Theme CSS + Header reducido ========
st.markdown(
    """
<style>
:root { color-scheme: dark; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background-color: #0e1117 !important;
  color: #fafafa !important;
}
.main { background-color: #0e1117 !important; padding-top: .5rem; }

/* Texto claro global */
h1, h2, h3, h4, h5, h6,
p, span, label, legend,
[data-testid="stMarkdownContainer"], .stMarkdown, .stCaption, .stText {
  color: #e5e7eb !important;
}
::placeholder { color: #94a3b8 !important; opacity: .85; }
a { color: #8ab4ff !important; }

/* Sidebar oscuro */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #121826 0%, #0b1220 100%) !important;
  border-right: 1px solid rgba(255,255,255,.08) !important;
}
[data-testid="stSidebar"] * { color: #e5e7eb !important; }

/* Header */
.header-container {
  max-width: 980px;
  margin: 0 auto 1rem auto;
  padding: .8rem 1.2rem;
  border-radius: 14px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255,255,255,.08);
}
.hero-content { display: grid; grid-template-columns: 1.2fr .8fr; gap: 1rem; align-items: center; }
.header-title { color: #fff; font-size: 1.6rem; font-weight: 800; margin: 0; letter-spacing: .3px; }
.header-subtitle { color: #b8c5d1; margin-top: .25rem; font-size: .95rem; }
.hero-image { display:flex; align-items:center; justify-content:flex-end; }
.hero-image img {
  height: 110px; width: auto; border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,.45);
  border: 1px solid rgba(255,255,255,.08);
}
@media (max-width: 900px) {
  .hero-content { grid-template-columns: 1fr; }
  .hero-image { justify-content:center; }
  .hero-image img { height: 90px; }
  .header-title { font-size: 1.4rem; text-align:center; }
  .header-subtitle { text-align:center; }
}

/* Controles */
.stTextInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"], .stDateInput input,
.stTimeInput input, .stNumberInput input {
  background-color: #1e2329 !important;
  color: #fafafa !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  border-radius: 10px !important;
}

/* Select: menú y trigger oscuros */
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] > div,
div[data-baseweb="popover"] [data-baseweb="menu"] {
  background-color: #1e2329 !important;
  color: #e5e7eb !important;
  border-color: rgba(255,255,255,.18) !important;
}

/* Radios / Checkboxes */
div[role="radiogroup"] > label, .stCheckbox > label { color: #e5e7eb !important; }

/* Botones */
.stButton>button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  padding: .55rem 1rem !important;
  font-weight: 700 !important;
  box-shadow: 0 6px 18px rgba(102,126,234,.35) !important;
}
.stButton>button:hover { transform: translateY(-1px); }

/* Tabs */
.stTabs [data-baseweb="tab"] {
  height: 46px;
  background: #1e2329 !important;
  border-radius: 10px !important;
  color: #b8c5d1 !important;
  font-weight: 700 !important;
  padding: 10px 16px !important;
}

/* Métricas */
[data-testid="metric-container"] {
  background: linear-gradient(135deg, #1e2329 0%, #2a2f36 100%) !important;
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; padding: .8rem;
  color: #e5e7eb !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
  color: #fafafa !important;
}

/* Tablas */
[data-testid="stDataFrame"] { background: #1e2329 !important; border-radius: 10px; }
[data-testid="stDataFrame"] table { background-color: #1e2329 !important; }
[data-testid="stDataFrame"] thead tr { background: #20262d !important; }
[data-testid="stDataFrame"] tbody tr { background: #1e2329 !important; }
[data-testid="stDataFrame"] * , [data-testid="stTable"] * { color: #e5e7eb !important; }

/* Alerts */
div[data-testid="stAlert"] {
  background: #141820 !important;
  color: #e5e7eb !important;
  border: 1px solid rgba(255,255,255,.12) !important;
}

/* Plotly */
.js-plotly-plot { background: transparent !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #1e2329; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #667eea; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #764ba2; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# DB — SQLite (local) por ahora
# =========================
DB_PATH = "barberia.db"
engine = create_engine(
    f"sqlite:///{DB_PATH}", echo=False, future=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# =========================
# Modelos
# =========================
class ItemType(enum.Enum):
    service = "service"
    product = "product"

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sales = relationship("Sale", back_populates="client")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    type = Column(Enum(ItemType), nullable=False)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    ticket_id = Column(String(36), nullable=True, index=True)  # agrupa una visita
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)  # precio histórico
    discount = Column(Float, default=0.0)       # CLP descuento
    tip = Column(Float, default=0.0)            # propina total de la visita en 1ra línea
    client = relationship("Client", back_populates="sales")
    item = relationship("Item")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(120), nullable=False)
    note = Column(Text, nullable=True)

class AppConfig(Base):
    __tablename__ = "app_config"
    id = Column(Integer, primary_key=True)
    key = Column(String(120), nullable=False, unique=True)
    value = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_items()
    migrate_tip_column()
    migrate_ticket_id_column()

def migrate_tip_column():
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(sales)")
        columns = [c[1] for c in cur.fetchall()]
        if "tip" not in columns:
            cur.execute("ALTER TABLE sales ADD COLUMN tip REAL DEFAULT 0.0")
            conn.commit()
        conn.close()
    except Exception as e:
        print("migrate_tip_column error:", e)

def migrate_ticket_id_column():
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(sales)")
        columns = [c[1] for c in cur.fetchall()]
        if "ticket_id" not in columns:
            cur.execute("ALTER TABLE sales ADD COLUMN ticket_id TEXT")
            conn.commit()
            # agrupar legacy por cliente y ventana de 90 min
            cur.execute("SELECT id, ts, client_id FROM sales WHERE ticket_id IS NULL ORDER BY client_id, ts")
            rows = cur.fetchall()
            current_ticket = None
            current_client = None
            current_time = None
            for sale_id, ts_str, client_id in rows:
                ts = datetime.fromisoformat(ts_str) if ts_str else datetime.utcnow()
                if (current_client != client_id) or (current_time is None) or ((ts - current_time).total_seconds() > 5400):
                    current_ticket = str(uuid.uuid4())
                    current_client = client_id
                current_time = ts
                cur.execute("UPDATE sales SET ticket_id = ? WHERE id = ?", (current_ticket, sale_id))
            conn.commit()
        conn.close()
    except Exception as e:
        print("migrate_ticket_id_column error:", e)

def seed_items():
    base_items = [
        ("Corte de pelo", 8000, ItemType.service),
        ("Perfilado de cejas", 1000, ItemType.service),
        ("Perfilado de barba", 5000, ItemType.service),
        ("Corte + barba", 12000, ItemType.service),
        ("Polvo texturizador", 5000, ItemType.product),
        ("Cera para peinar", 5000, ItemType.product),
    ]
    with SessionLocal() as s:
        existing = {i.name: i for i in s.query(Item).all()}
        changed = False
        for name, price, itype in base_items:
            if name in existing:
                it = existing[name]
                if (it.price != price) or (it.type != itype):
                    it.price = price
                    it.type = itype
                    changed = True
            else:
                s.add(Item(name=name, price=price, type=itype))
                changed = True
        if changed:
            s.commit()

init_db()

# =========
# Utilidades
# =========
def money(x: float) -> str:
    try:
        return f"$ {int(round(x)):,}".replace(",", ".")
    except:
        try:
            return f"$ {x:,.0f}".replace(",", ".")
        except:
            return str(x)

def get_30min_intervals():
    times = []
    for hour in range(24):
        times.append(dt.time(hour, 0).strftime("%H:%M"))
        times.append(dt.time(hour, 30).strftime("%H:%M"))
    return times

def apply_dark_theme(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fafafa"),
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis=dict(type="category"),
        title_font_color="#fafafa",
    )
    fig.update_xaxes(
        title_font=dict(color="#e5e7eb"),
        tickfont=dict(color="#e5e7eb"),
        gridcolor="rgba(255,255,255,.08)"
    )
    fig.update_yaxes(
        title_font=dict(color="#e5e7eb"),
        tickfont=dict(color="#e5e7eb"),
        gridcolor="rgba(255,255,255,.08)"
    )
    return fig

def nombre_mes_es(m: int) -> str:
    meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]
    return meses[m-1]

def semanas_en_mes(year: int, month: int) -> int:
    first_weekday, days_in_month = calendar.monthrange(year, month)  # Lunes=0
    return ((first_weekday + days_in_month - 1) // 7) + 1

def semana_del_mes(d: date) -> int:
    first_weekday, _ = calendar.monthrange(d.year, d.month)  # Lunes=0
    return ((d.day + first_weekday - 1) // 7) + 1

def semana_bucket_4(d: date) -> int:
    if d.day <= 7:
        return 1
    elif d.day <= 14:
        return 2
    elif d.day <= 21:
        return 3
    else:
        return 4

# ========
# Queries base
# ========
def get_df_sales(start: date = None, end: date = None) -> pd.DataFrame:
    with SessionLocal() as s:
        q = s.query(Sale).order_by(Sale.ts.desc())
        if start:
            q = q.filter(Sale.ts >= dt.datetime.combine(start, dt.time.min))
        if end:
            q = q.filter(Sale.ts <= dt.datetime.combine(end, dt.time.max))
        rows = q.all()
        data = []
        for r in rows:
            data.append(
                {
                    "id": r.id,
                    "ts": r.ts,
                    "fecha": r.ts.date(),
                    "hora": r.ts.time().strftime("%H:%M"),
                    "cliente_id": r.client_id,
                    "cliente": (r.client.name if r.client else "(sin cliente)"),
                    "item_id": r.item_id,
                    "item": r.item.name,
                    "tipo": r.item.type.value,
                    "cantidad": r.quantity,
                    "precio_unit": r.unit_price,
                    "descuento": r.discount,
                    "total_linea": r.quantity * r.unit_price - r.discount,
                    "ticket_id": r.ticket_id,
                    "tip": r.tip,
                }
            )
        return (
            pd.DataFrame(data)
            if data
            else pd.DataFrame(
                columns=[
                    "id","ts","fecha","hora","cliente_id","cliente",
                    "item_id","item","tipo","cantidad","precio_unit",
                    "descuento","total_linea","ticket_id","tip"
                ]
            )
        )

def get_df_expenses(start: date = None, end: date = None) -> pd.DataFrame:
    with SessionLocal() as s:
        q = s.query(Expense).order_by(Expense.ts.desc())
        if start:
            q = q.filter(Expense.ts >= dt.datetime.combine(start, dt.time.min))
        if end:
            q = q.filter(Expense.ts <= dt.datetime.combine(end, dt.time.max))
        rows = q.all()
        data = [
            {
                "id": r.id,
                "ts": r.ts,
                "fecha": r.ts.date(),
                "hora": r.ts.time().strftime("%H:%M"),
                "categoria": r.category,
                "nota": r.note or "",
                "monto": r.amount,
            }
            for r in rows
        ]
        return (
            pd.DataFrame(data)
            if data
            else pd.DataFrame(columns=["id","ts","fecha","hora","categoria","nota","monto"])
        )

def get_items():
    with SessionLocal() as s:
        return s.query(Item).order_by(Item.type, Item.name).all()

def get_items_by_names(names):
    with SessionLocal() as s:
        rows = s.query(Item).filter(Item.name.in_(names)).all()
        return {r.name: r for r in rows}

def get_all_clients():
    with SessionLocal() as s:
        return s.query(Client).order_by(Client.name.asc()).all()

def get_grouped_sales(start: date = None, end: date = None):
    with SessionLocal() as s:
        q = s.query(Sale).join(Item)
        if start:
            q = q.filter(Sale.ts >= dt.datetime.combine(start, dt.time.min))
        if end:
            q = q.filter(Sale.ts <= dt.datetime.combine(end, dt.time.max))
        sales = q.order_by(Sale.ts.desc()).all()

        visits = {}
        for sale in sales:
            ticket = sale.ticket_id or f"legacy_{sale.id}"
            if ticket not in visits:
                visits[ticket] = {
                    "ticket_id": ticket,
                    "fecha_hora": sale.ts,
                    "fecha": sale.ts.date(),
                    "hora": sale.ts.time().strftime("%H:%M"),
                    "cliente_id": sale.client_id,
                    "cliente": sale.client.name if sale.client else "(sin cliente)",
                    "items": [],
                    "total": 0.0,
                    "descuento_total": 0.0,
                    "propina_total": 0.0,
                }
            item_total = sale.quantity * sale.unit_price - sale.discount
            visits[ticket]["items"].append(
                {
                    "id": sale.id,
                    "servicio_id": sale.item_id,
                    "nombre": sale.item.name,
                    "tipo": sale.item.type.value,
                    "cantidad": sale.quantity,
                    "precio_unitario": sale.unit_price,
                    "descuento": sale.discount,
                    "subtotal": item_total,
                }
            )
            visits[ticket]["total"] += item_total
            visits[ticket]["descuento_total"] += sale.discount
            visits[ticket]["propina_total"] += sale.tip

        result = sorted(visits.values(), key=lambda x: x["fecha_hora"], reverse=True)
        return result

def get_grouped_sales_by_client(client_id: int, start: date = None, end: date = None):
    """Visitas agrupadas por ticket para un cliente específico."""
    with SessionLocal() as s:
        q = s.query(Sale).join(Item).filter(Sale.client_id == client_id)
        if start:
            q = q.filter(Sale.ts >= dt.datetime.combine(start, dt.time.min))
        if end:
            q = q.filter(Sale.ts <= dt.datetime.combine(end, dt.time.max))
        sales = q.order_by(Sale.ts.desc()).all()

        visits = {}
        for sale in sales:
            ticket = sale.ticket_id or f"legacy_{sale.id}"
            if ticket not in visits:
                visits[ticket] = {
                    "ticket_id": ticket,
                    "fecha_hora": sale.ts,
                    "fecha": sale.ts.date(),
                    "hora": sale.ts.time().strftime("%H:%M"),
                    "items": [],
                    "total": 0.0,
                    "descuento_total": 0.0,
                    "propina_total": 0.0,
                }
            item_total = sale.quantity * sale.unit_price - sale.discount
            visits[ticket]["items"].append(
                {
                    "id": sale.id,
                    "servicio_id": sale.item_id,
                    "nombre": sale.item.name,
                    "tipo": sale.item.type.value,
                    "cantidad": sale.quantity,
                    "precio_unitario": sale.unit_price,
                    "descuento": sale.discount,
                    "subtotal": item_total,
                }
            )
            visits[ticket]["total"] += item_total
            visits[ticket]["descuento_total"] += sale.discount
            visits[ticket]["propina_total"] += sale.tip

        result = sorted(visits.values(), key=lambda x: x["fecha_hora"], reverse=True)
        return result

# =========
# Helpers edición/eliminación de visitas
# =========
def _is_legacy_ticket(ticket_id: str) -> bool:
    return (ticket_id or "").startswith("legacy_")

def _legacy_sale_id(ticket_id: str) -> int | None:
    try:
        return int((ticket_id or "").split("_", 1)[1])
    except Exception:
        return None

def delete_visit(ticket_id: str):
    """Elimina todas las líneas de una visita (por ticket_id) o una línea legacy."""
    with SessionLocal() as s:
        if _is_legacy_ticket(ticket_id):
            sale_id = _legacy_sale_id(ticket_id)
            if sale_id is not None:
                s.query(Sale).filter(Sale.id == sale_id).delete(synchronize_session=False)
        else:
            s.query(Sale).filter(Sale.ticket_id == ticket_id).delete(synchronize_session=False)
        s.commit()

def replace_visit(ticket_id: str, ts: datetime, client_name: str, lines: list[dict], tip_total: float) -> str:
    """
    Reemplaza la visita completa:
    - Borra líneas actuales (ticket o legacy)
    - Inserta nuevas líneas con el mismo ticket (o crea uno si era legacy)
    lines: [{item_id, quantity, unit_price, discount}]
    """
    new_ticket = ticket_id if (ticket_id and not _is_legacy_ticket(ticket_id)) else str(uuid.uuid4())
    client_id = ensure_client(client_name) if (client_name or "").strip() else None

    with SessionLocal() as s:
        # Borrar actuales
        if _is_legacy_ticket(ticket_id):
            sale_id = _legacy_sale_id(ticket_id)
            if sale_id is not None:
                s.query(Sale).filter(Sale.id == sale_id).delete(synchronize_session=False)
        else:
            s.query(Sale).filter(Sale.ticket_id == ticket_id).delete(synchronize_session=False)

        # Insertar nuevas
        for i, ln in enumerate(lines):
            s.add(Sale(
                ts=ts,
                ticket_id=new_ticket,
                client_id=client_id,
                item_id=int(ln["item_id"]),
                quantity=int(ln.get("quantity", 1)),
                unit_price=float(ln.get("unit_price", 0.0)),
                discount=float(ln.get("discount", 0.0)),
                tip=(float(tip_total) if i == 0 else 0.0)
            ))
        s.commit()
    return new_ticket

def ensure_client(name: str, phone: str = "", notes: str = ""):
    name = (name or "").strip()
    if not name:
        return None
    with SessionLocal() as s:
        c = s.query(Client).filter(Client.name.ilike(name)).first()
        if c:
            updated = False
            if phone and (not c.phone):
                c.phone = phone
                updated = True
            if notes and (not c.notes):
                c.notes = notes
                updated = True
            if updated:
                s.commit()
            return c.id
        c = Client(name=name, phone=phone or None, notes=notes or None)
        s.add(c)
        s.commit()
        return c.id

def add_sale(
    ts: datetime,
    client_id: int,
    item_id: int,
    quantity: int,
    unit_price: float,
    discount: float,
    tip: float = 0.0,
    ticket_id: str = None,
):
    with SessionLocal() as s:
        if not ticket_id:
            ticket_id = str(uuid.uuid4())
        sale = Sale(
            ts=ts,
            ticket_id=ticket_id,
            client_id=client_id,
            item_id=item_id,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tip=tip,
        )
        s.add(sale)
        s.commit()
        return ticket_id

def add_expense(ts: datetime, amount: float, category: str, note: str):
    with SessionLocal() as s:
        e = Expense(
            ts=ts, amount=float(amount), category=category.strip() or "Otros", note=note or None
        )
        s.add(e)
        s.commit()

def _safe_rerun():
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# =========
# Header UI
# =========
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

hero_image_path = os.path.join(os.path.dirname(__file__), "static", "hero_image.png")
hero_image_b64 = get_image_base64(hero_image_path)
if hero_image_b64:
    st.markdown(
        f"""
<div class="header-container">
  <div class="hero-content">
    <div class="hero-text">
      <h1 class="header-title">Bienvenido Jorgito</h1>
      <div class="header-subtitle">Tu panel de barbería — métricas y registro</div>
    </div>
    <div class="hero-image">
      <img src="data:image/png;base64,{hero_image_b64}" alt="Bienvenida" />
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
<div class="header-container">
  <div class="hero-content">
    <div class="hero-text">
      <h1 class="header-title">Bienvenido Jorgito</h1>
      <div class="header-subtitle">Tu panel de barbería — métricas y registro</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ===================
# Sidebar navegación
# ===================
st.sidebar.markdown("### 🏪 Navegación")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📍 Ir a:",
    [
        "📊 Resumen",
        "🧾 Registrar venta",
        "💰 Finanzas",
        "👤 Clientes",
        "🧰 Items",
        "📜 Historial",
        "📈 Análisis",
        "⚙️ Configuración",
    ],
    index=0,
)

# Filtros globales rápidos (pueden usarse en otras páginas)
with st.sidebar.expander("Filtros de fecha (global)", expanded=False):
    hoy = date.today()
    default_start = hoy - timedelta(days=30)
    global_start = st.date_input("Desde", value=default_start, key="fdesde_global")
    global_end = st.date_input("Hasta", value=hoy, key="fhasta_global")

# ==========================
# Resumen
# ==========================
if page == "📊 Resumen":
    st.title("📊 Resumen")

    st.markdown("#### 🎛️ Vista y período")
    vista = st.radio(
        "Selecciona vista",
        ["Diario", "Semanal", "Mensual", "Anual"],
        horizontal=True,
        index=0,
        key="vista_resumen",
    )

    def pick_diario():
        d = st.date_input("Día", value=date.today(), key="pick_dia")
        start = d; end = d; label = d.strftime("%d/%m/%Y")
        return start, end, label

    def pick_semanal():
        d = st.date_input(
            "Semana (elige cualquier día de la semana deseada)",
            value=date.today(), key="pick_semana",
        )
        week_start = d - timedelta(days=d.weekday())
        week_end = week_start + timedelta(days=6)
        label = f"Semana {week_start.strftime('%d/%m')} → {week_end.strftime('%d/%m/%Y')}"
        return week_start, week_end, label

    def pick_mensual():
        coly, colm = st.columns(2)
        with coly:
            y = st.number_input("Año", min_value=2000, max_value=2100, value=date.today().year, step=1)
        with colm:
            m = st.selectbox(
                "Mes",
                list(range(1, 12 + 1)),
                index=date.today().month - 1,
                format_func=lambda x: [
                    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
                ][x - 1],
            )
        start = date(y, m, 1)
        end = date(y, m, calendar.monthrange(y, m)[1])
        label = f"{start.strftime('%B %Y')}"
        return start, end, label

    def pick_anual():
        y = st.number_input("Año", min_value=2000, max_value=2100, value=date.today().year, step=1, key="pick_anio")
        start = date(y, 1, 1); end = date(y, 12, 31); label = f"{y}"
        return start, end, label

    if vista == "Diario":
        p_start, p_end, p_label = pick_diario()
    elif vista == "Semanal":
        p_start, p_end, p_label = pick_semanal()
    elif vista == "Mensual":
        p_start, p_end, p_label = pick_mensual()
    else:
        p_start, p_end, p_label = pick_anual()

    df_period = get_df_sales(p_start, p_end)
    df_exp_period = get_df_expenses(p_start, p_end)

    ingresos = df_period["total_linea"].sum() if not df_period.empty else 0
    gastos = df_exp_period["monto"].sum() if not df_exp_period.empty else 0
    balance = ingresos - gastos

    c1, c2, c3 = st.columns(3)
    c1.metric(f"💰 Ingresos ({p_label})", money(ingresos))
    c2.metric(f"💸 Gastos ({p_label})", money(gastos))
    c3.metric(f"🧮 Balance ({p_label})", money(balance))

    st.markdown("---")

    # Evolución de Ingresos
    st.markdown("### 📈 Evolución de Ingresos")
    st.caption("La granularidad se ajusta automáticamente a la vista seleccionada.")

    def rango_dia():
        col1, col2 = st.columns(2)
        with col1: d1 = st.date_input("Desde (día)", value=p_start, key="evo_d1")
        with col2: d2 = st.date_input("Hasta (día)", value=p_end, key="evo_d2")
        return d1, d2

    def rango_mes_con_anio():
        col1, col2 = st.columns(2)
        with col1: y = st.number_input("Año", min_value=2000, max_value=2100, value=p_start.year, key="evo_y")
        with col2: m = st.selectbox("Mes", list(range(1, 13)), index=p_start.month - 1, key="evo_m", format_func=nombre_mes_es)
        start = date(y, m, 1)
        end = date(y, m, calendar.monthrange(y, m)[1])
        return start, end, y, m

    def rango_solo_anio():
        y = st.number_input("Año", min_value=2000, max_value=2100, value=p_start.year, key="evo_year_only")
        return date(y, 1, 1), date(y, 12, 31), y

    if vista == "Diario":
        gran = "Día"
    elif vista == "Semanal":
        gran = "Semana"
    elif vista == "Mensual":
        gran = "Mes"
    else:
        gran = "Año"

    if gran == "Día":
        r_start, r_end = rango_dia()
        df_evo = get_df_sales(r_start, r_end)
        if not df_evo.empty:
            rng = pd.date_range(r_start, r_end, freq="D").date
            serie = df_evo.groupby("fecha")["total_linea"].sum().reindex(rng, fill_value=0.0)
            x_labels = [d.strftime("%d/%m") for d in rng]
            fig = go.Figure()
            fig.add_scatter(x=x_labels, y=serie.values, mode="lines+markers", name="Ingresos diarios", fill="tozeroy")
            fig.update_layout(title="Evolución diaria", xaxis_title="Fecha", yaxis_title="Ingresos (CLP)")
            st.plotly_chart(apply_dark_theme(fig), use_container_width=True)
        else:
            st.info("No hay datos para el rango diario seleccionado.")

    elif gran == "Semana":
        m_start, m_end, y_sel, m_sel = rango_mes_con_anio()
        df_evo = get_df_sales(m_start, m_end)
        n_weeks = semanas_en_mes(y_sel, m_sel)
        semanas = [f"Semana {i}" for i in range(1, n_weeks + 1)]
        vals = [0.0] * n_weeks
        if not df_evo.empty:
            df_evo["fecha"] = pd.to_datetime(df_evo["ts"]).dt.date
            df_evo["semana_mes"] = df_evo["fecha"].apply(semana_del_mes)
            g = df_evo.groupby("semana_mes")["total_linea"].sum().to_dict()
            for i in range(1, n_weeks + 1):
                vals[i - 1] = float(g.get(i, 0.0))
        fig = go.Figure()
        fig.add_scatter(x=semanas, y=vals, mode="lines+markers", name="Ingresos semanales", fill="tozeroy")
        fig.update_layout(title=f"Evolución semanal — {nombre_mes_es(m_sel)} {y_sel}",
                          xaxis_title="Semanas del mes (calendario)", yaxis_title="Ingresos (CLP)")
        st.plotly_chart(apply_dark_theme(fig), use_container_width=True)

    elif gran == "Mes":
        m_start, m_end, y_sel, m_sel = rango_mes_con_anio()
        df_evo = get_df_sales(m_start, m_end)
        etiquetas = [f"Semana {i}" for i in range(1, 5)]
        vals = [0.0, 0.0, 0.0, 0.0]
        if not df_evo.empty:
            df_evo["fecha"] = pd.to_datetime(df_evo["ts"]).dt.date
            df_evo["bucket4"] = df_evo["fecha"].apply(semana_bucket_4)
            g = df_evo.groupby("bucket4")["total_linea"].sum().to_dict()
            for i in range(1, 5):
                vals[i - 1] = float(g.get(i, 0.0))
        fig = go.Figure()
        fig.add_scatter(x=etiquetas, y=vals, mode="lines+markers", name=f"Ingresos — {nombre_mes_es(m_sel)} {y_sel}", fill="tozeroy")
        fig.update_layout(title=f"Evolución mensual — {nombre_mes_es(m_sel)} {y_sel} (4 semanas)",
                          xaxis_title="Semanas del mes (1–4)", yaxis_title="Ingresos (CLP)")
        st.plotly_chart(apply_dark_theme(fig), use_container_width=True)

    else:  # Año
        y_start, y_end, y_sel = rango_solo_anio()
        df_evo = get_df_sales(y_start, y_end)
        meses_labels = [nombre_mes_es(i) for i in range(1, 13)]
        vals = [0.0] * 12
        if not df_evo.empty:
            df_evo["mes_num"] = pd.to_datetime(df_evo["ts"]).dt.month
            g = df_evo.groupby("mes_num")["total_linea"].sum().to_dict()
            for i in range(1, 13):
                vals[i - 1] = float(g.get(i, 0.0))
        fig = go.Figure()
        fig.add_scatter(x=meses_labels, y=vals, mode="lines+markers", name=f"Ingresos — {y_sel}", fill="tozeroy")
        fig.update_layout(title=f"Evolución anual — {y_sel} (por mes)",
                          xaxis_title="Meses del año", yaxis_title="Ingresos (CLP)")
        st.plotly_chart(apply_dark_theme(fig), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Resumen de Servicios y Productos")
    if not df_period.empty:
        resumen_items = (
            df_period.groupby("item")
            .agg(cantidad=("cantidad", "sum"), ingresos=("total_linea", "sum"))
            .reset_index()
            .sort_values("ingresos", ascending=False)
        )
        resumen_items["Ingresos Totales"] = resumen_items["ingresos"].apply(money)
        resumen_items = resumen_items[["item", "cantidad", "Ingresos Totales"]]
        resumen_items.columns = ["Servicio/Producto", "Cantidad", "Ingresos Totales"]
        st.dataframe(resumen_items, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos para mostrar en este período.")

# ==========================
# Registrar venta/servicio
# ==========================
elif page == "🧾 Registrar venta":
    st.title("🧾 Registrar venta/servicio")

    # Modo cliente
    modo_cliente = st.radio("¿Cliente?", ["Nuevo", "Existente"], index=0, horizontal=True)

    # Fecha / hora
    cfecha1, cfecha2 = st.columns([1, 1])
    with cfecha1:
        fecha = st.date_input("Fecha", value=date.today(), key="fecha_reg", format="DD/MM/YYYY")
    with cfecha2:
        now = dt.datetime.now()
        minute = 30 if now.minute >= 30 else 0
        default_time = now.replace(minute=minute, second=0, microsecond=0).time()
        time_str = st.selectbox(
            "Hora",
            options=get_30min_intervals(),
            index=get_30min_intervals().index(default_time.strftime("%H:%M")),
            key="hora_reg_select",
        )
        hora = dt.datetime.strptime(time_str, "%H:%M").time()

    # Cliente
    if modo_cliente == "Nuevo":
        c1, c2 = st.columns([2, 1])
        with c1:
            cliente_nombre = st.text_input("Nombre del cliente", placeholder="Ej: Juan Pérez")
            cliente_phone = st.text_input("Contacto (teléfono o Instagram)", placeholder="+569...")
        with c2:
            cliente_notes = st.text_area("Notas (opcional)", height=60)
        client_id_sel = None
    else:
        clientes = get_all_clients()
        if clientes:
            idx_cli = st.selectbox(
                "Selecciona cliente existente",
                options=list(range(len(clientes))),
                format_func=lambda i: f"{clientes[i].name}" + (f" — {clientes[i].phone}" if clientes[i].phone else ""),
            )
            client_id_sel = clientes[idx_cli].id
        else:
            st.warning("No hay clientes. Crea uno nuevo.")
            client_id_sel = None
        cliente_nombre = ""
        cliente_phone = ""
        cliente_notes = ""

    st.markdown("---")

    # Ítems
    nombres_opciones = [
        "Corte de pelo",
        "Perfilado de cejas",
        "Perfilado de barba",
        "Corte + barba",
        "Polvo texturizador",
        "Cera para peinar",
    ]
    items_map = get_items_by_names(nombres_opciones)

    servicios = []
    productos = []
    for nombre in nombres_opciones:
        it = items_map.get(nombre)
        if not it:
            continue
        (servicios if it.type == ItemType.service else productos).append((nombre, it))

    seleccion = []

    # Servicios
    if servicios:
        st.subheader("🔧 Servicios")
        cols_serv = st.columns(2)
        for i, (nombre, it) in enumerate(servicios):
            col = cols_serv[i % 2]
            with col:
                marcado = st.checkbox(f"{nombre} — {money(it.price)}", key=f"serv_chk_{i}")
                if marcado:
                    seleccion.append(
                        {
                            "item_id": it.id,
                            "item_name": it.name,
                            "quantity": 1,
                            "unit_price": float(it.price),
                            "discount": 0.0,
                            "preview_total": float(it.price),
                        }
                    )

    # Productos
    if productos:
        st.subheader("🛍️ Productos")
        cols_prod = st.columns(2)
        for i, (nombre, it) in enumerate(productos):
            col = cols_prod[i % 2]
            with col:
                marcado = st.checkbox(f"{nombre} — {money(it.price)}", key=f"prod_chk_{i}")
                if marcado:
                    cant = st.number_input(f"Cantidad: {nombre}", min_value=1, value=1, step=1, key=f"prod_qty_{i}")
                    seleccion.append(
                        {
                            "item_id": it.id,
                            "item_name": it.name,
                            "quantity": int(cant),
                            "unit_price": float(it.price),
                            "discount": 0.0,
                            "preview_total": float(it.price) * int(cant),
                        }
                    )

    st.markdown("---")
    st.subheader("💸 Propina (opcional)")
    tip = st.number_input("Monto (CLP)", min_value=0, value=0, step=500)

    st.markdown("---")
    if seleccion:
        subtotal = sum(s["preview_total"] for s in seleccion)
        total = subtotal + tip
        df_prev = pd.DataFrame(
            [
                {
                    "Ítem": s["item_name"],
                    "Cantidad": s["quantity"],
                    "Precio Unit.": money(s["unit_price"]),
                    "Total": money(s["preview_total"]),
                }
                for s in seleccion
            ]
        )
        if tip > 0:
            df_prev = pd.concat(
                [
                    df_prev,
                    pd.DataFrame([{"Ítem": "💸 Propina", "Cantidad": "", "Precio Unit.": "", "Total": money(tip)}]),
                ],
                ignore_index=True,
            )

        st.subheader("📋 Resumen")
        st.dataframe(df_prev, use_container_width=True, hide_index=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Subtotal", money(subtotal))
        c2.metric("Propina", money(tip))
        c3.metric("Total a pagar", money(total))
    else:
        st.info("Selecciona uno o más servicios/productos.")

    if st.button("Guardar todo"):
        if not seleccion:
            st.error("No hay ítems seleccionados.")
        else:
            ts = datetime.combine(fecha, hora)
            if modo_cliente == "Nuevo":
                client_id = None
                if cliente_nombre.strip():
                    client_id = ensure_client(cliente_nombre, cliente_phone, cliente_notes)
            else:
                client_id = client_id_sel
            visit_ticket_id = str(uuid.uuid4())
            for i, row in enumerate(seleccion):
                add_sale(
                    ts=ts,
                    client_id=client_id,
                    item_id=row["item_id"],
                    quantity=row["quantity"],
                    unit_price=row["unit_price"],
                    discount=row["discount"],
                    tip=(tip if i == 0 else 0.0),
                    ticket_id=visit_ticket_id,
                )
            st.success("✅ Venta registrada")
            st.info(f"Ticket ID: {visit_ticket_id[:8]}... ({len(seleccion)} líneas)")

# =========
# Finanzas (flujo de caja mejorado)
# =========
elif page == "💰 Finanzas":
    st.title("💰 Finanzas")

    # Selector de vista y fechas propias de finanzas
    vista_f = st.radio("Vista", ["Diaria", "Semanal", "Mensual", "Anual"], horizontal=True, index=0, key="fin_vista")

    if vista_f == "Diaria":
        f_start = st.date_input("Desde", value=global_start, key="fin_d_start")
        f_end = st.date_input("Hasta", value=global_end, key="fin_d_end")
        freq = "D"
        period_fmt = "%d/%m/%Y"
    elif vista_f == "Semanal":
        f_start = st.date_input("Desde (semana)", value=global_start, key="fin_w_start")
        f_end = st.date_input("Hasta (semana)", value=global_end, key="fin_w_end")
        freq = "W-MON"  # semanas que terminan el lunes siguiente (inicio lunes)
        period_fmt = "Sem %W/%Y"
    elif vista_f == "Mensual":
        y = st.number_input("Año", min_value=2000, max_value=2100, value=global_start.year, step=1, key="fin_y_m")
        f_start = date(y, 1, 1)
        f_end = date(y, 12, 31)
        freq = "M"
        period_fmt = "%b %Y"
    else:  # Anual
        y1, y2 = st.columns(2)
        with y1:
            y_from = st.number_input("Desde año", min_value=2000, max_value=2100, value=global_start.year, step=1, key="fin_y_from")
        with y2:
            y_to = st.number_input("Hasta año", min_value=2000, max_value=2100, value=global_end.year, step=1, key="fin_y_to")
        f_start = date(int(y_from), 1, 1)
        f_end = date(int(y_to), 12, 31)
        freq = "Y"
        period_fmt = "%Y"

    df_s = get_df_sales(f_start, f_end)
    df_e = get_df_expenses(f_start, f_end)

    total_ing = df_s["total_linea"].sum() if not df_s.empty else 0.0
    total_gas = df_e["monto"].sum() if not df_e.empty else 0.0
    total_bal = total_ing - total_gas

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos (rango)", money(total_ing))
    c2.metric("Gastos (rango)", money(total_gas))
    c3.metric("Balance (rango)", money(total_bal))

    # Construir flujo por periodo
    def group_cashflow(df_sales, df_exp, freq: str):
        if df_sales.empty and df_exp.empty:
            return pd.DataFrame(columns=["periodo", "ingresos", "gastos", "balance", "acumulado"])

        s = pd.DataFrame()
        if not df_sales.empty:
            s = df_sales[["ts", "total_linea"]].copy()
            s["monto"] = s["total_linea"].astype(float)
            s["tipo"] = "ingreso"
            s = s[["ts", "monto", "tipo"]]

        e = pd.DataFrame()
        if not df_exp.empty:
            e = df_exp[["ts", "monto"]].copy()
            e["monto"] = e["monto"].astype(float) * -1.0
            e["tipo"] = "gasto"
            e = e[["ts", "monto", "tipo"]]

        comb = pd.concat([s, e], ignore_index=True) if not s.empty or not e.empty else pd.DataFrame(columns=["ts","monto","tipo"])
        if comb.empty:
            return pd.DataFrame(columns=["periodo", "ingresos", "gastos", "balance", "acumulado"])

        comb["ts"] = pd.to_datetime(comb["ts"])
        comb = comb.set_index("ts").sort_index()

        grp = comb.groupby(pd.Grouper(freq=freq)).agg(
            ingresos=("monto", lambda x: float(x[x > 0].sum())),
            gastos=("monto", lambda x: float(-x[x < 0].sum())),
            balance=("monto", "sum"),
        ).reset_index()

        grp["periodo"] = grp["ts"].dt.strftime(period_fmt)
        grp["acumulado"] = grp["balance"].cumsum()
        out = grp[["periodo", "ingresos", "gastos", "balance", "acumulado"]]
        return out

    flujo = group_cashflow(df_s, df_e, freq)

    st.markdown("---")
    st.markdown("### 🔁 Flujo de caja")
    if flujo.empty:
        st.info("No hay datos en el rango seleccionado.")
    else:
        st.dataframe(
            pd.DataFrame({
                "Periodo": flujo["periodo"],
                "Ingresos": flujo["ingresos"].apply(money),
                "Gastos": flujo["gastos"].apply(money),
                "Balance": flujo["balance"].apply(money),
                "Acumulado": flujo["acumulado"].apply(money),
            }),
            use_container_width=True, hide_index=True
        )

        fig_cf = go.Figure()
        fig_cf.add_scatter(x=flujo["periodo"], y=flujo["ingresos"], mode="lines+markers", name="Ingresos")
        fig_cf.add_scatter(x=flujo["periodo"], y=flujo["gastos"], mode="lines+markers", name="Gastos")
        fig_cf.add_scatter(x=flujo["periodo"], y=flujo["balance"], mode="lines+markers", name="Balance")
        fig_cf.update_layout(title=f"Flujo ({vista_f})", xaxis_title="Periodo", yaxis_title="CLP")
        st.plotly_chart(apply_dark_theme(fig_cf), use_container_width=True)

# =========
# Clientes (perfiles + periodicidad)
# =========
elif page == "👤 Clientes":
    st.title("👤 Gestión de Clientes")
    with st.expander("➕ Agregar Nuevo Cliente", expanded=False):
        with st.form("form_client"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre completo*", placeholder="Ej: Juan Pérez")
                phone = st.text_input("Contacto", placeholder="Teléfono o Instagram")
            with col2:
                notes = st.text_area("Notas adicionales", height=80)
            ok = st.form_submit_button("💾 Guardar Cliente")
            if ok:
                if not name.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    _id = ensure_client(name, phone, notes)
                    st.success(f"✅ Cliente '{name}' guardado.")

    clientes = get_all_clients()
    if not clientes:
        st.info("No hay clientes registrados.")
    else:
        st.subheader(f"📋 Lista de Clientes ({len(clientes)})")
        search = st.text_input("🔍 Buscar", placeholder="Nombre, teléfono o notas...")
        if search:
            clientes = [
                c for c in clientes
                if search.lower() in c.name.lower()
                or (c.phone and search.lower() in c.phone.lower())
                or (c.notes and search.lower() in c.notes.lower())
            ]

        def compute_periodicity(dates_list: list[date]):
            dates_sorted = sorted(set(dates_list))
            if len(dates_sorted) < 2:
                return None
            diffs = [(dates_sorted[i] - dates_sorted[i-1]).days for i in range(1, len(dates_sorted))]
            if not diffs:
                return None
            avg = mean(diffs)
            med = median(diffs)
            try:
                mode = Counter(diffs).most_common(1)[0][0]
            except Exception:
                mode = None
            last_visit = dates_sorted[-1]
            # recordatorio al 75% del intervalo típico (promedio)
            remind_days = max(1, int(round(avg * 0.75)))
            suggested_reminder = last_visit + timedelta(days=remind_days)
            return {
                "avg": avg, "med": med, "mode": mode,
                "last": last_visit, "remind_days": remind_days,
                "suggested_reminder": suggested_reminder
            }

        for c in clientes:
            with st.expander(f"👤 {c.name}", expanded=False):
                st.write(f"**Contacto:** {c.phone or '—'}")
                st.write(f"**Notas:** {c.notes or '—'}")
                st.write(f"**Desde:** {c.created_at.strftime('%d/%m/%Y') if c.created_at else '—'}")

                visits = get_grouped_sales_by_client(c.id, None, None)
                if not visits:
                    st.info("Este cliente no tiene visitas registradas.")
                    continue

                # Fechas de visita + detalle
                fechas = [v["fecha"] for v in visits]
                st.markdown("#### 🗓️ Visitas")
                # Tabla simple de visitas
                rows = []
                for v in visits:
                    items_txt = ", ".join([f"{it['nombre']} (x{it['cantidad']})" for it in v["items"]])
                    rows.append({
                        "Fecha": v["fecha"].strftime("%d/%m/%Y"),
                        "Hora": v["hora"],
                        "Servicios/Productos": items_txt,
                        "Total": money(v["total"])
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                # Periodicidad
                stats = compute_periodicity(fechas)
                st.markdown("#### ⏱️ Periodicidad")
                if not stats:
                    st.info("Aún no hay suficientes visitas para calcular periodicidad (se requieren 2 o más).")
                else:
                    colp1, colp2, colp3 = st.columns(3)
                    colp1.metric("Promedio entre visitas", f"{stats['avg']:.1f} días")
                    colp2.metric("Mediana entre visitas", f"{stats['med']:.1f} días")
                    colp3.metric("Más común (moda)", f"{stats['mode']} días" if stats['mode'] else "—")
                    colp1, colp2 = st.columns(2)
                    colp1.metric("Última visita", stats["last"].strftime("%d/%m/%Y"))
                    colp2.metric("Sugerir recordar en", f"{stats['remind_days']} días (→ {stats['suggested_reminder'].strftime('%d/%m/%Y')})")

                # Gráfico de visitas
                ts_counts = pd.Series(1, index=pd.to_datetime([datetime.combine(f, dt.time()) for f in fechas]))
                ts_counts = ts_counts.sort_index().resample("D").sum().fillna(0)
                figv = go.Figure()
                figv.add_bar(x=[d.strftime("%d/%m/%Y") for d in ts_counts.index.date], y=ts_counts.values, name="Visitas")
                figv.update_layout(title="Visitas en el tiempo", xaxis_title="Fecha", yaxis_title="N° visitas")
                st.plotly_chart(apply_dark_theme(figv), use_container_width=True)

# =====
# Items
# =====
elif page == "🧰 Items":
    st.title("🧰 Items (servicios y productos)")
    with st.form("form_item"):
        name = st.text_input("Nombre*", placeholder="Ej: Corte de pelo")
        tipo_txt = st.selectbox("Tipo", options=["Servicio", "Producto"])
        tipo = ItemType.service if tipo_txt == "Servicio" else ItemType.product
        price = st.number_input("Precio*", min_value=0, value=0, step=500)
        ok = st.form_submit_button("Guardar / Actualizar")
        if ok:
            if not name.strip() or price <= 0:
                st.error("Nombre y precio son obligatorios.")
            else:
                with SessionLocal() as s:
                    item = s.query(Item).filter(Item.name.ilike(name.strip())).first()
                    if item:
                        item.price = float(price)
                        item.type = tipo
                        s.commit()
                    else:
                        s.add(Item(name=name.strip(), price=float(price), type=tipo))
                        s.commit()
                st.success("Item guardado/actualizado ✅")
    catalogo = [
        {
            "Ítem": i.name,
            "Tipo": "Servicio" if i.type == ItemType.service else "Producto",
            "Precio": money(i.price),
        }
        for i in get_items()
    ]
    st.dataframe(pd.DataFrame(catalogo), use_container_width=True, hide_index=True)

# =========
# Historial (con Editar / Eliminar)
# =========
elif page == "📜 Historial":
    st.title("📜 Historial de Visitas")
    visits = get_grouped_sales(global_start, global_end)
    if not visits:
        st.info("No hay visitas registradas en el período.")
    else:
        st.markdown(f"**Total de visitas:** {len(visits)}")
        items_catalog = get_items()  # para editor
        for idx, v in enumerate(visits):
            ticket = v["ticket_id"]
            with st.expander(
                f"🗓️ {v['fecha']} {v['hora']} — {v['cliente']} — {money(v['total'])}",
                expanded=(idx < 3),
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**Detalle de servicios/productos:**")
                    df_items = pd.DataFrame(v["items"])
                    if not df_items.empty:
                        df_disp = df_items.rename(
                            columns={
                                "nombre": "Servicio/Producto",
                                "cantidad": "Cant.",
                                "precio_unitario": "Precio Unit.",
                                "descuento": "Descuento",
                                "subtotal": "Subtotal",
                            }
                        )[["Servicio/Producto", "Cant.", "Precio Unit.", "Descuento", "Subtotal"]]
                        df_disp["Precio Unit."] = df_disp["Precio Unit."].apply(money)
                        df_disp["Descuento"] = df_disp["Descuento"].apply(money)
                        df_disp["Subtotal"] = df_disp["Subtotal"].apply(money)
                        st.dataframe(df_disp, use_container_width=True, hide_index=True)
                with col2:
                    st.metric("Total", money(v["total"]))
                    if v["descuento_total"] > 0:
                        st.metric("Descuento", money(v["descuento_total"]))
                    if v["propina_total"] > 0:
                        st.metric("Propina", money(v["propina_total"]))

                st.markdown("---")
                # Editor de visita
                with st.expander("✏️ Editar visita", expanded=False):
                    d_default = v["fecha"]
                    h_default = datetime.strptime(v["hora"], "%H:%M").time()
                    cliente_default = "" if v["cliente"] == "(sin cliente)" else v["cliente"]
                    tip_default = float(v.get("propina_total", 0.0))

                    cfe1, cfe2 = st.columns(2)
                    with cfe1:
                        new_date = st.date_input("Fecha", value=d_default, key=f"edit_date_{ticket}_{idx}")
                    with cfe2:
                        time_index = get_30min_intervals().index(h_default.strftime("%H:%M")) if h_default.strftime("%H:%M") in get_30min_intervals() else 0
                        new_time_str = st.selectbox("Hora", options=get_30min_intervals(), index=time_index, key=f"edit_time_{ticket}_{idx}")
                        new_time = datetime.strptime(new_time_str, "%H:%M").time()

                    new_cliente = st.text_input("Nombre del cliente (deja vacío para 'sin cliente')", value=cliente_default, key=f"edit_cliente_{ticket}_{idx}")
                    new_tip = st.number_input("Propina total (CLP)", min_value=0, value=int(round(tip_default)), step=500, key=f"edit_tip_{ticket}_{idx}")

                    st.markdown("#### Ítems de la visita")
                    current_lines = {ln["servicio_id"]: ln for ln in v["items"]}
                    selected_lines = []
                    cols = st.columns(2)
                    for j, it in enumerate(items_catalog):
                        col = cols[j % 2]
                        with col:
                            ln = current_lines.get(it.id)
                            default_checked = ln is not None and int(ln["cantidad"]) > 0
                            chk = st.checkbox(f"{it.name} — {money(it.price)}", value=default_checked, key=f"edit_chk_{ticket}_{it.id}")
                            if chk:
                                qty_default = int(ln["cantidad"]) if ln else 1
                                price_default = float(ln["precio_unitario"]) if ln else float(it.price)
                                disc_default = float(ln["descuento"]) if ln else 0.0

                                q = st.number_input(f"Cantidad: {it.name}", min_value=1, value=qty_default, step=1, key=f"edit_qty_{ticket}_{it.id}")
                                p = st.number_input(f"Precio unitario: {it.name}", min_value=0.0, value=float(price_default), step=500.0, key=f"edit_price_{ticket}_{it.id}")
                                dsc = st.number_input(f"Descuento: {it.name}", min_value=0.0, value=float(disc_default), step=500.0, key=f"edit_disc_{ticket}_{it.id}")

                                selected_lines.append({
                                    "item_id": it.id,
                                    "quantity": int(q),
                                    "unit_price": float(p),
                                    "discount": float(dsc),
                                })

                    if selected_lines:
                        preview_rows = []
                        subtotal = 0.0
                        for ln in selected_lines:
                            sub = ln["quantity"] * ln["unit_price"] - ln["discount"]
                            subtotal += sub
                            name = next((x.name for x in items_catalog if x.id == ln["item_id"]), f"ID {ln['item_id']}")
                            preview_rows.append({"Ítem": name, "Cant.": ln["quantity"], "Precio Unit.": money(ln["unit_price"]), "Desc.": money(ln["discount"]), "Subtotal": money(sub)})
                        df_prev = pd.DataFrame(preview_rows)
                        st.dataframe(df_prev, use_container_width=True, hide_index=True)
                        cpr1, cpr2, cpr3 = st.columns(3)
                        cpr1.metric("Subtotal", money(subtotal))
                        cpr2.metric("Propina", money(new_tip))
                        cpr3.metric("Total", money(subtotal + new_tip))
                    else:
                        st.info("Selecciona uno o más ítems para la visita.")

                    if st.button("💾 Guardar cambios", key=f"save_edit_{ticket}_{idx}"):
                        if not selected_lines:
                            st.error("Debe haber al menos un ítem.")
                        else:
                            new_ts = datetime.combine(new_date, new_time)
                            new_ticket = replace_visit(ticket, new_ts, new_cliente, selected_lines, new_tip)
                            st.success("✅ Visita actualizada")
                            st.info(f"Ticket ID: {new_ticket[:8]}…")
                            _safe_rerun()

                # Eliminar visita
                with st.expander("🗑️ Eliminar visita", expanded=False):
                    st.warning("Esta acción elimina la visita completa. Escribe **BORRAR** para confirmar.")
                    conf = st.text_input("Confirmación", key=f"del_conf_{ticket}_{idx}")
                    if st.button("Eliminar definitivamente", key=f"del_btn_{ticket}_{idx}"):
                        if conf.strip().upper() == "BORRAR":
                            delete_visit(ticket)
                            st.success("🗑️ Visita eliminada")
                            _safe_rerun()
                        else:
                            st.error("Escribe BORRAR para confirmar.")

# =========
# Análisis avanzado
# =========
elif page == "📈 Análisis":
    st.title("📈 Análisis de demanda")

    a_start = st.date_input("Desde", value=global_start, key="ana_from")
    a_end = st.date_input("Hasta", value=global_end, key="ana_to")
    df = get_df_sales(a_start, a_end)

    if df.empty:
        st.info("No hay datos en el rango seleccionado.")
    else:
        df["ts"] = pd.to_datetime(df["ts"])
        df["weekday"] = df["ts"].dt.weekday  # Lunes=0
        df["weekday_name"] = df["weekday"].map({
            0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
        })

        # Solo servicios para "cortes"
        servicios = df[df["tipo"] == "service"].copy()
        cortes_por_dia = servicios.groupby("weekday_name")["cantidad"].sum().reindex(
            ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"], fill_value=0
        )

        st.markdown("### 💇‍♂️ Cortes por día de la semana (servicios)")
        fig1 = go.Figure()
        fig1.add_bar(x=cortes_por_dia.index, y=cortes_por_dia.values, name="Cortes (servicios)")
        fig1.update_layout(xaxis_title="Día de la semana", yaxis_title="Cantidad")
        st.plotly_chart(apply_dark_theme(fig1), use_container_width=True)

        st.markdown("### 💰 Ingresos por día de la semana (todos los ítems)")
        ingresos_por_dia = df.groupby("weekday_name")["total_linea"].sum().reindex(
            ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"], fill_value=0.0
        )
        fig2 = go.Figure()
        fig2.add_bar(x=ingresos_por_dia.index, y=ingresos_por_dia.values, name="Ingresos")
        fig2.update_layout(xaxis_title="Día de la semana", yaxis_title="CLP")
        st.plotly_chart(apply_dark_theme(fig2), use_container_width=True)

        tabla = pd.DataFrame({
            "Día": ingresos_por_dia.index,
            "Cortes (servicios)": cortes_por_dia.values,
            "Ingresos": ingresos_por_dia.values
        })
        tabla["Ingresos"] = tabla["Ingresos"].apply(money)
        st.dataframe(tabla, use_container_width=True, hide_index=True)

# ===============
# Configuración
# ===============
elif page == "⚙️ Configuración":
    st.title("⚙️ Configuración")

    st.markdown("### 📊 Reparto de Ingresos")
    with st.form("form_porcentajes"):
        col1, col2, col3, col4 = st.columns(4)
        cur_salary = st.session_state.get("pct_salary", 30)
        cur_shop = st.session_state.get("pct_shop", 20)
        cur_savings = st.session_state.get("pct_savings", 35)
        cur_invest = st.session_state.get("pct_invest", 15)
        with col1:
            new_salary = st.number_input("💼 Sueldo (%)", 0, 100, cur_salary, step=1)
        with col2:
            new_shop = st.number_input("🏪 Barbería (%)", 0, 100, cur_shop, step=1)
        with col3:
            new_savings = st.number_input("💰 Ahorro (%)", 0, 100, cur_savings, step=1)
        with col4:
            new_invest = st.number_input("📈 Inversión (%)", 0, 100, cur_invest, step=1)

        total_pct = new_salary + new_shop + new_savings + new_invest
        if total_pct != 100:
            st.warning(f"⚠️ Suman {total_pct}%. Debe ser 100%.")
        else:
            st.success("✅ Suma 100%.")

        if st.form_submit_button("💾 Guardar Porcentajes"):
            st.session_state["pct_salary"] = new_salary
            st.session_state["pct_shop"] = new_shop
            st.session_state["pct_savings"] = new_savings
            st.session_state["pct_invest"] = new_invest
            st.success("Guardado ✅")

    st.caption("Los porcentajes se usan en Resumen → Distribución de Ingresos.")
