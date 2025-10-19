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

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

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
<meta name="theme-color" content="#0e1117">
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
/* ---------- BASE / FONDO ----------- */
:root {
  --bg-0: #0e1117;
  --bg-1: #121723;
  --bg-2: #1a1f2b;
  --bg-3: #1e2329;
  --txt-0: #fafafa;
  --txt-1: #d7dee9;
  --acc-1: #667eea;
  --acc-2: #764ba2;
  --border-1: rgba(255,255,255,.10);
  --border-2: rgba(255,255,255,.18);
}
html, body, .stApp { background-color: var(--bg-0) !important; color: var(--txt-0) !important; }
.main { background-color: var(--bg-0) !important; padding-top: .5rem; }

/* ---------- SIDEBAR OSCURO ---------- */
[data-testid="stSidebar"], section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #151a26 0%, #101521 100%) !important;
  border-right: 1px solid var(--border-1) !important;
}
[data-testid="stSidebar"] * { color: var(--txt-1) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
  color: var(--txt-1) !important;
}

/* ---------- CONTROLES (inputs/selects/fechas) ---------- */
.stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input,
.stNumberInput input, .stSelectbox > div > div {
  background-color: var(--bg-3) !important;
  color: var(--txt-0) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 10px !important;
}
div[data-baseweb="select"] > div { background-color: var(--bg-3) !important; color: var(--txt-0) !important; }
div[data-baseweb="select"] svg { color: var(--txt-0) !important; fill: var(--txt-0) !important; }

/* ---------- BOTONES ---------- */
.stButton>button {
  background: linear-gradient(135deg, var(--acc-1) 0%, var(--acc-2) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  padding: .55rem 1rem !important;
  font-weight: 700 !important;
  box-shadow: 0 6px 18px rgba(102,126,234,.35) !important;
}
.stButton>button:hover { transform: translateY(-1px); }

/* ---------- TÍTULOS Y TEXTO ---------- */
h1, h2, h3, h4, h5, h6, .stMarkdown, .stCaption, .stText, label, p, span, small {
  color: var(--txt-0) !important;
}
.stCaption { color: var(--txt-1) !important; }

/* ---------- MÉTRICAS (valores claritos) ---------- */
[data-testid="stMetricValue"], [data-testid="stMetricDelta"], [data-testid="stMetricLabel"] {
  color: var(--txt-0) !important;
}
[data-testid="metric-container"] {
  background: linear-gradient(135deg, var(--bg-3) 0%, #2a2f36 100%) !important;
  border: 1px solid var(--border-1);
  border-radius: 12px; padding: .8rem;
}

/* ---------- TABS ---------- */
.stTabs [data-baseweb="tab"] {
  height: 46px;
  background: var(--bg-3) !important;
  border-radius: 10px !important;
  color: var(--txt-1) !important;
  font-weight: 700 !important;
  padding: 10px 16px !important;
}

/* ---------- TABLAS / DATAFRAMES en oscuro ---------- */
div[data-testid="stDataFrame"] { background: var(--bg-1) !important; color: var(--txt-0) !important; }
div[data-testid="stDataFrame"] thead tr th { background: var(--bg-3) !important; color: var(--txt-0) !important; }
div[data-testid="stDataFrame"] tbody tr td { color: var(--txt-0) !important; }
.stTable thead tr th { background: var(--bg-3) !important; color: var(--txt-0) !important; }
.stTable tbody tr td { background: var(--bg-1) !important; color: var(--txt-0) !important; }

/* ---------- PLOTLY fondo transparente ---------- */
.js-plotly-plot { background: transparent !important; }

/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-3); border-radius: 4px; }
::-webkit-scrollbar-thumb { background: var(--acc-1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--acc-2); }

/* ---------- HEADER (compacto) ---------- */
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
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# DB — SQLite + SQLAlchemy
# =========================
DB_PATH = "barberia.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


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
        return f"$ {x:,.0f}".replace(",", ".")


def get_30min_intervals():
    times = []
    for hour in range(24):
        times.append(dt.time(hour, 0).strftime("%H:%M"))
        times.append(dt.time(hour, 30).strftime("%H:%M"))
    return times


def apply_dark_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fafafa"),
        title_font=dict(color="#fafafa", size=16),
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis=dict(type="category")
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
# Queries
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
                    "cliente": (r.client.name if r.client else "(sin cliente)"),
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
                    "id","ts","fecha","hora","cliente","item","tipo",
                    "cantidad","precio_unit","descuento","total_linea","ticket_id","tip"
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


def ensure_client(name: str, phone: str = "", notes: str = ""):
    name = name.strip()
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
    """Agrupa visitas por ticket SOLO para un cliente específico."""
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

        return sorted(visits.values(), key=lambda x: x["fecha_hora"], reverse=True)

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
# Resumen — NUEVA EXPERIENCIA
# ==========================
if page == "📊 Resumen":
    st.title("📊 Resumen")

    # -------- Vista y Período puntual (para KPIs + Distribución + Resumen items) ----------
    st.markdown("#### 🎛️ Vista y período")
    vista = st.radio(
        "Selecciona vista",
        ["Diario", "Semanal", "Mensual", "Anual"],
        horizontal=True,
        index=0,
        key="vista_resumen",
    )

    # Helpers de selección por vista
    def pick_diario():
        d = st.date_input("Día", value=date.today(), key="pick_dia")
        start = d
        end = d
        label = d.strftime("%d/%m/%Y")
        return start, end, label

    def pick_semanal():
        d = st.date_input(
            "Semana (elige cualquier día de la semana deseada)",
            value=date.today(),
            key="pick_semana",
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
        if m == 12:
            end = date(y, 12, 31)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        label = f"{start.strftime('%B %Y')}"
        return start, end, label

    def pick_anual():
        y = st.number_input("Año", min_value=2000, max_value=2100, value=date.today().year, step=1, key="pick_anio")
        start = date(y, 1, 1)
        end = date(y, 12, 31)
        label = f"{y}"
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

    # -------- Evolución de ingresos ----------
    st.markdown("### 📈 Evolución de Ingresos")
    st.caption("La granularidad se ajusta automáticamente a la vista seleccionada.")

    def rango_dia():
        col1, col2 = st.columns(2)
        with col1:
            d1 = st.date_input("Desde (día)", value=p_start, key="evo_d1")
        with col2:
            d2 = st.date_input("Hasta (día)", value=p_end, key="evo_d2")
        return d1, d2

    def rango_mes_con_anio():
        col1, col2 = st.columns(2)
        with col1:
            y = st.number_input("Año", min_value=2000, max_value=2100, value=p_start.year, key="evo_y")
        with col2:
            m = st.selectbox(
                "Mes",
                list(range(1, 13)),
                index=p_start.month - 1,
                key="evo_m",
                format_func=nombre_mes_es,
            )
        start = date
