import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from sheets_db import SheetsDB

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="LabStock — Inventario Técnico",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
    h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

    .stApp { background-color: #0a0f1e; color: #e2e8f0; }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1e2d45;
    }

    .metric-card {
        background: #111827;
        border: 1px solid #1e2d45;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .metric-card.cyan::before  { background: #00e5ff; }
    .metric-card.purple::before { background: #7c3aed; }
    .metric-card.green::before  { background: #10b981; }
    .metric-card.red::before    { background: #f43f5e; }

    .metric-label {
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }
    .metric-card.cyan .metric-value   { color: #00e5ff; }
    .metric-card.purple .metric-value { color: #a78bfa; }
    .metric-card.green .metric-value  { color: #10b981; }
    .metric-card.red .metric-value    { color: #f43f5e; }

    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-success { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
    .badge-warning { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
    .badge-danger  { background: rgba(244,63,94,0.15);  color: #fda4af; border: 1px solid rgba(244,63,94,0.3); }

    div[data-testid="stForm"] {
        background: #111827;
        border: 1px solid #1e2d45;
        border-radius: 12px;
        padding: 1.5rem;
    }

    .stButton > button {
        font-family: 'DM Mono', monospace;
        font-weight: 500;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label {
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748b;
    }

    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #e2e8f0;
        margin-bottom: 1rem;
    }
    .section-title span { color: #00e5ff; }

    .stDataFrame { border: 1px solid #1e2d45; border-radius: 8px; }

    hr { border-color: #1e2d45; }
</style>
""", unsafe_allow_html=True)

# ─── INIT DB ───────────────────────────────────────────────────
@st.cache_resource
def get_db():
    return SheetsDB()

db = get_db()

CAJONES = [
    'BIOQUIMICA', 'BIOLOGIA MOLECULAR', 'COAGULACION',
    'CONTROL DE CALIDAD', 'GASES Y ELECTROLITOS', 'HbA1C',
    'HEMATOLOGIA', 'INMUNOLOGIA', 'MICROBIOLOGIA', 'URIANALISIS'
]

CAJON_COLORS = {
    'BIOQUIMICA':          '#93c5fd',
    'BIOLOGIA MOLECULAR':  '#fcd34d',
    'COAGULACION':         '#f9a8d4',
    'CONTROL DE CALIDAD':  '#86efac',
    'GASES Y ELECTROLITOS':'#5eead4',
    'HbA1C':               '#fdba74',
    'HEMATOLOGIA':         '#fca5a5',
    'INMUNOLOGIA':         '#c4b5fd',
    'MICROBIOLOGIA':       '#6ee7b7',
    'URIANALISIS':         '#fde68a',
}

# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧪 LabStock")
    st.markdown("---")
    page = st.radio(
        "Navegación",
        ["📊 Dashboard", "📦 Inventario", "🔄 Movimientos", "📈 Reportes", "📥 Importar Excel"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Filtrar por Cajón**")
    cajon_filter = st.selectbox("Cajón", ["Todos"] + CAJONES, label_visibility="collapsed")
    st.markdown("---")
    st.caption("LabStock v1.0 — Taller Técnico")

# ─── LOAD DATA ─────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_productos():
    return db.get_productos()

@st.cache_data(ttl=30)
def load_movimientos():
    return db.get_movimientos()

def refresh():
    st.cache_data.clear()
    st.rerun()

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<div class="section-title">Panel <span>Principal</span></div>', unsafe_allow_html=True)

    productos = load_productos()
    movimientos = load_movimientos()

    # ── Stats ──
    total_prods  = len(productos)
    total_stock  = int(productos['stock'].sum()) if not productos.empty else 0
    sin_stock    = int((productos['stock'] == 0).sum()) if not productos.empty else 0
    stock_bajo   = int(((productos['stock'] > 0) & (productos['stock'] <= productos['stock_minimo'])).sum()) if not productos.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card cyan"><div class="metric-label">Total Productos</div><div class="metric-value">{total_prods}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card purple"><div class="metric-label">Unidades en Stock</div><div class="metric-value">{total_stock}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card red"><div class="metric-label">Sin Stock</div><div class="metric-value">{sin_stock}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card green"><div class="metric-label">Stock Bajo</div><div class="metric-value">{stock_bajo}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown("### ⚠️ Productos con Stock Crítico")
        if not productos.empty:
            criticos = productos[productos['stock'] <= productos['stock_minimo']].copy()
            criticos = criticos.sort_values('stock')
            if criticos.empty:
                st.success("✅ ¡Todo el stock está en niveles óptimos!")
            else:
                def color_stock(val):
                    if val == 0: return 'color: #f43f5e; font-weight: bold'
                    return 'color: #f59e0b; font-weight: bold'
                st.dataframe(
                    criticos[['codigo','nombre','cajon','stock','stock_minimo']].rename(columns={
                        'codigo':'Código','nombre':'Producto','cajon':'Cajón',
                        'stock':'Stock','stock_minimo':'Mínimo'
                    }),
                    use_container_width=True, hide_index=True,
                    column_config={"Stock": st.column_config.NumberColumn(format="%d")}
                )
        else:
            st.info("No hay productos cargados aún.")

    with col_right:
        st.markdown("### 📦 Stock por Cajón")
        if not productos.empty:
            stock_por_cajon = productos.groupby('cajon')['stock'].sum().reset_index()
            stock_por_cajon.columns = ['Cajón', 'Stock']
            fig = px.bar(
                stock_por_cajon, x='Stock', y='Cajón', orientation='h',
                color='Cajón',
                color_discrete_map={k: v for k, v in CAJON_COLORS.items()},
                template='plotly_dark'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(17,24,39,0.8)',
                showlegend=False,
                height=350,
                margin=dict(l=0, r=10, t=10, b=0),
                font=dict(family='DM Mono')
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    # ── Últimos movimientos ──
    st.markdown("### 🔄 Últimos Movimientos")
    if not movimientos.empty:
        ultimos = movimientos.tail(8).iloc[::-1].copy()
        ultimos['tipo'] = ultimos['tipo'].apply(
            lambda t: f"{'⬇️ ENTRADA' if t=='entrada' else '⬆️ SALIDA'}"
        )
        st.dataframe(
            ultimos[['fecha','tipo','producto_nombre','cajon','cantidad','nota']].rename(columns={
                'fecha':'Fecha','tipo':'Tipo','producto_nombre':'Producto',
                'cajon':'Cajón','cantidad':'Cant.','nota':'Nota'
            }),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No hay movimientos registrados.")

# ══════════════════════════════════════════════════════════════
# INVENTARIO
# ══════════════════════════════════════════════════════════════
elif page == "📦 Inventario":
    st.markdown('<div class="section-title">Inventario <span>Completo</span></div>', unsafe_allow_html=True)

    productos = load_productos()

    tab1, tab2 = st.tabs(["📋 Ver Inventario", "➕ Agregar Producto"])

    with tab1:
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search = st.text_input("🔍 Buscar por código o nombre", placeholder="Ej: BIO-001 o Glucosa...")
        with col_filter:
            filtro = st.selectbox("Cajón", ["Todos"] + CAJONES, key="inv_filter")

        if not productos.empty:
            df = productos.copy()
            if search:
                df = df[df['codigo'].str.contains(search, case=False, na=False) |
                        df['nombre'].str.contains(search, case=False, na=False)]
            if filtro != "Todos":
                df = df[df['cajon'] == filtro]

            def stock_status(row):
                if row['stock'] == 0:
                    return '🔴 Sin stock'
                elif row['stock'] <= row['stock_minimo']:
                    return '🟡 Bajo'
                return '🟢 OK'

            df['estado'] = df.apply(stock_status, axis=1)
            st.caption(f"{len(df)} producto(s) encontrado(s)")
            st.dataframe(
                df[['codigo','nombre','cajon','stock','stock_minimo','estado']].rename(columns={
                    'codigo':'Código','nombre':'Producto','cajon':'Cajón',
                    'stock':'Stock','stock_minimo':'Stock Mínimo','estado':'Estado'
                }),
                use_container_width=True, hide_index=True,
                column_config={
                    "Stock": st.column_config.NumberColumn(format="%d"),
                    "Stock Mínimo": st.column_config.NumberColumn(format="%d"),
                }
            )
        else:
            st.info("No hay productos. Agrega uno o importa desde Excel.")

    with tab2:
        with st.form("form_agregar"):
            st.markdown("**Datos del Producto**")
            col1, col2 = st.columns(2)
            with col1:
                nuevo_codigo = st.text_input("Código *", placeholder="Ej: BIO-001")
                nuevo_cajon  = st.selectbox("Cajón *", CAJONES)
            with col2:
                nuevo_nombre = st.text_input("Nombre del Producto *", placeholder="Ej: Reactivo Glucosa")
                nuevo_stock  = st.number_input("Stock Inicial", min_value=0, value=0)

            nuevo_minstock = st.number_input("Stock Mínimo (alerta)", min_value=0, value=5)

            submitted = st.form_submit_button("✅ Agregar Producto", use_container_width=True)
            if submitted:
                if not nuevo_codigo or not nuevo_nombre:
                    st.error("Código y Nombre son obligatorios")
                elif not productos.empty and nuevo_codigo in productos['codigo'].values:
                    st.error(f"Ya existe el código {nuevo_codigo}")
                else:
                    db.add_producto(nuevo_codigo, nuevo_nombre, nuevo_cajon, nuevo_stock, nuevo_minstock)
                    st.success(f"✅ Producto '{nuevo_nombre}' agregado correctamente")
                    refresh()

# ══════════════════════════════════════════════════════════════
# MOVIMIENTOS
# ══════════════════════════════════════════════════════════════
elif page == "🔄 Movimientos":
    st.markdown('<div class="section-title">Registro de <span>Movimientos</span></div>', unsafe_allow_html=True)

    productos   = load_productos()
    movimientos = load_movimientos()

    tab1, tab2 = st.tabs(["📥 Registrar Movimiento", "📋 Historial"])

    with tab1:
        if productos.empty:
            st.warning("⚠️ No hay productos cargados. Importa o agrega productos primero.")
        else:
            col_e, col_s = st.columns(2)

            # ENTRADA
            with col_e:
                st.markdown("### 📥 Entrada de Stock")
                with st.form("form_entrada"):
                    opciones = [f"[{r['codigo']}] {r['nombre']} (Stock: {r['stock']})"
                                for _, r in productos.iterrows()]
                    sel = st.selectbox("Producto", opciones)
                    cant_e = st.number_input("Cantidad", min_value=1, value=1, key="cant_e")
                    nota_e = st.text_input("Referencia / Nota", placeholder="Opcional", key="nota_e")
                    if st.form_submit_button("✅ Confirmar Entrada", use_container_width=True):
                        idx   = opciones.index(sel)
                        prod  = productos.iloc[idx]
                        db.registrar_movimiento(
                            prod['id'], prod['codigo'], prod['nombre'],
                            prod['cajon'], 'entrada', cant_e, nota_e
                        )
                        db.actualizar_stock(prod['id'], int(prod['stock']) + cant_e)
                        st.success(f"✅ +{cant_e} unidades de **{prod['nombre']}**")
                        refresh()

            # SALIDA
            with col_s:
                st.markdown("### 📤 Salida de Stock")
                with st.form("form_salida"):
                    opciones2 = [f"[{r['codigo']}] {r['nombre']} (Stock: {r['stock']})"
                                 for _, r in productos.iterrows()]
                    sel2 = st.selectbox("Producto", opciones2, key="sel_salida")
                    cant_s = st.number_input("Cantidad", min_value=1, value=1, key="cant_s")
                    nota_s = st.text_input("Referencia / Nota", placeholder="Opcional", key="nota_s")
                    if st.form_submit_button("✅ Confirmar Salida", use_container_width=True):
                        idx2  = opciones2.index(sel2)
                        prod2 = productos.iloc[idx2]
                        if cant_s > int(prod2['stock']):
                            st.error(f"❌ Stock insuficiente. Disponible: {prod2['stock']}")
                        else:
                            db.registrar_movimiento(
                                prod2['id'], prod2['codigo'], prod2['nombre'],
                                prod2['cajon'], 'salida', cant_s, nota_s
                            )
                            db.actualizar_stock(prod2['id'], int(prod2['stock']) - cant_s)
                            st.success(f"✅ -{cant_s} unidades de **{prod2['nombre']}**")
                            refresh()

    with tab2:
        st.markdown("### 📋 Historial Completo")
        if not movimientos.empty:
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                tipo_filter = st.selectbox("Tipo", ["Todos", "entrada", "salida"])
            with col_f2:
                cajon_f = st.selectbox("Cajón", ["Todos"] + CAJONES, key="mov_cajon")
            with col_f3:
                fecha_filter = st.date_input("Desde fecha", value=None)

            df_mov = movimientos.copy().iloc[::-1]
            if tipo_filter != "Todos":
                df_mov = df_mov[df_mov['tipo'] == tipo_filter]
            if cajon_f != "Todos":
                df_mov = df_mov[df_mov['cajon'] == cajon_f]
            if fecha_filter:
                df_mov = df_mov[pd.to_datetime(df_mov['fecha']).dt.date >= fecha_filter]

            df_mov['tipo'] = df_mov['tipo'].apply(lambda t: '⬇️ Entrada' if t == 'entrada' else '⬆️ Salida')
            st.caption(f"{len(df_mov)} movimiento(s)")
            st.dataframe(
                df_mov[['fecha','tipo','producto_codigo','producto_nombre','cajon','cantidad','nota']].rename(columns={
                    'fecha':'Fecha','tipo':'Tipo','producto_codigo':'Código',
                    'producto_nombre':'Producto','cajon':'Cajón',
                    'cantidad':'Cant.','nota':'Nota'
                }),
                use_container_width=True, hide_index=True
            )

            csv = df_mov.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Exportar CSV", csv, "movimientos.csv", "text/csv")
        else:
            st.info("No hay movimientos registrados aún.")

# ══════════════════════════════════════════════════════════════
# REPORTES
# ══════════════════════════════════════════════════════════════
elif page == "📈 Reportes":
    st.markdown('<div class="section-title">Reportes y <span>Análisis</span></div>', unsafe_allow_html=True)

    productos   = load_productos()
    movimientos = load_movimientos()

    if productos.empty:
        st.info("No hay datos suficientes para generar reportes.")
    else:
        tab1, tab2, tab3 = st.tabs(["📦 Stock Actual", "📊 Movimientos", "⚠️ Alertas"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                stock_cajon = productos.groupby('cajon')['stock'].sum().reset_index()
                fig1 = px.pie(
                    stock_cajon, values='stock', names='cajon',
                    title='Distribución de Stock por Cajón',
                    color='cajon',
                    color_discrete_map=CAJON_COLORS,
                    template='plotly_dark', hole=0.4
                )
                fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Mono'))
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                prods_cajon = productos.groupby('cajon').size().reset_index(name='cantidad')
                fig2 = px.bar(
                    prods_cajon, x='cajon', y='cantidad',
                    title='Cantidad de Productos por Cajón',
                    color='cajon',
                    color_discrete_map=CAJON_COLORS,
                    template='plotly_dark'
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(17,24,39,0.8)',
                    showlegend=False,
                    font=dict(family='DM Mono'),
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            if not movimientos.empty:
                df_mov = movimientos.copy()
                df_mov['fecha_dt'] = pd.to_datetime(df_mov['fecha'])
                df_mov['dia'] = df_mov['fecha_dt'].dt.date

                mov_dia = df_mov.groupby(['dia','tipo'])['cantidad'].sum().reset_index()
                fig3 = px.bar(
                    mov_dia, x='dia', y='cantidad', color='tipo',
                    title='Movimientos por Día',
                    color_discrete_map={'entrada': '#10b981', 'salida': '#f43f5e'},
                    template='plotly_dark', barmode='group'
                )
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(17,24,39,0.8)',
                    font=dict(family='DM Mono')
                )
                st.plotly_chart(fig3, use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    top_mov = df_mov.groupby('producto_nombre')['cantidad'].sum().nlargest(10).reset_index()
                    fig4 = px.bar(
                        top_mov, x='cantidad', y='producto_nombre', orientation='h',
                        title='Top 10 Productos con más Movimientos',
                        template='plotly_dark', color_discrete_sequence=['#00e5ff']
                    )
                    fig4.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(17,24,39,0.8)',
                        font=dict(family='DM Mono')
                    )
                    st.plotly_chart(fig4, use_container_width=True)

                with col4:
                    resumen = df_mov.groupby('tipo')['cantidad'].sum().reset_index()
                    fig5 = px.pie(
                        resumen, values='cantidad', names='tipo',
                        title='Total Entradas vs Salidas',
                        color='tipo',
                        color_discrete_map={'entrada':'#10b981','salida':'#f43f5e'},
                        template='plotly_dark', hole=0.5
                    )
                    fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Mono'))
                    st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("Registra movimientos para ver este reporte.")

        with tab3:
            sin_stock  = productos[productos['stock'] == 0]
            stock_bajo = productos[(productos['stock'] > 0) & (productos['stock'] <= productos['stock_minimo'])]

            st.markdown(f"### 🔴 Sin Stock ({len(sin_stock)} productos)")
            if not sin_stock.empty:
                st.dataframe(
                    sin_stock[['codigo','nombre','cajon','stock_minimo']].rename(columns={
                        'codigo':'Código','nombre':'Producto','cajon':'Cajón','stock_minimo':'Stock Mínimo'
                    }),
                    use_container_width=True, hide_index=True
                )
            else:
                st.success("No hay productos sin stock.")

            st.markdown(f"### 🟡 Stock Bajo ({len(stock_bajo)} productos)")
            if not stock_bajo.empty:
                st.dataframe(
                    stock_bajo[['codigo','nombre','cajon','stock','stock_minimo']].rename(columns={
                        'codigo':'Código','nombre':'Producto','cajon':'Cajón',
                        'stock':'Stock Actual','stock_minimo':'Stock Mínimo'
                    }),
                    use_container_width=True, hide_index=True
                )
            else:
                st.success("No hay productos con stock bajo.")

# ══════════════════════════════════════════════════════════════
# IMPORTAR EXCEL
# ══════════════════════════════════════════════════════════════
elif page == "📥 Importar Excel":
    st.markdown('<div class="section-title">Importar <span>Excel</span></div>', unsafe_allow_html=True)

    productos = load_productos()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Importar tu INVENTARIO.xlsx")
        st.info("Tu archivo tiene columnas: **codigo / producto / ubicacion / stock**. La app las detecta automáticamente.")

        archivo = st.file_uploader("Sube INVENTARIO.xlsx", type=['xlsx','xls','csv'], key="upload_prods")
        if archivo:
            try:
                if archivo.name.endswith('.csv'):
                    df_raw = pd.read_csv(archivo)
                else:
                    # Tu Excel tiene fila de encabezado en fila 2 (índice 1)
                    df_raw = pd.read_excel(archivo, header=1)

                # Renombrar columnas al formato conocido
                df_raw.columns = ['codigo','_c1','producto','_c3','ubicacion','stock']
                # Limpiar: quitar fila de encabezado repetida y filas sin código
                df_raw = df_raw[df_raw['codigo'] != 'codigo']
                df_raw = df_raw.dropna(subset=['codigo'])
                df_raw['codigo']    = df_raw['codigo'].astype(str).str.strip()
                df_raw['producto']  = df_raw['producto'].astype(str).str.strip()
                df_raw['ubicacion'] = df_raw['ubicacion'].astype(str).str.strip()
                # Eliminar duplicados de código (queda la primera aparición)
                df_raw = df_raw.drop_duplicates(subset=['codigo'])

                st.success(f"✅ Archivo leído correctamente: **{len(df_raw)} productos únicos**")
                st.markdown("**Vista previa (primeros 8):**")
                st.dataframe(df_raw[['codigo','producto','ubicacion']].head(8),
                             use_container_width=True, hide_index=True)

                st.markdown(f"**Cajones detectados en el archivo:**")
                cajones_excel = df_raw['ubicacion'].dropna().unique()
                cols_badges = st.columns(min(len(cajones_excel), 5))
                for i, c in enumerate(cajones_excel):
                    cols_badges[i % 5].success(c)

                if st.button("⬆️ Importar todos los productos", use_container_width=True, type="primary"):
                    existing_codes = set(productos['codigo'].values) if not productos.empty else set()
                    added   = 0
                    skipped = 0
                    errors  = []

                    progress = st.progress(0, text="Importando...")
                    total = len(df_raw)

                    for i, (_, row) in enumerate(df_raw.iterrows()):
                        codigo   = row['codigo']
                        nombre   = row['producto']
                        cajon    = row['ubicacion'] if row['ubicacion'] in CAJONES else CAJONES[0]
                        stk      = int(row['stock']) if str(row['stock']).isdigit() else 0

                        if codigo in existing_codes:
                            skipped += 1
                        else:
                            db.add_producto(codigo, nombre, cajon, stk, 5)
                            existing_codes.add(codigo)
                            added += 1

                        if i % 50 == 0:
                            progress.progress((i+1)/total, text=f"Importando {i+1}/{total}...")

                    progress.progress(1.0, text="¡Completado!")
                    refresh()
                    st.success(f"✅ **{added}** productos importados. **{skipped}** omitidos (código duplicado).")

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    with col2:
        st.markdown("### ℹ️ Formato de tu Excel")
        st.markdown("""
La app está configurada para leer exactamente tu archivo con esta estructura:

| codigo | producto | ubicacion | stock |
|--------|----------|-----------|-------|
| AB 04J71-10 | 1ml Pipette Tips | MOLECULAR | — |
| HEM-001 | Tubos EDTA | HEMATOLOGIA | — |

**Cajones válidos en el sistema:**
        """)
        for c in CAJONES:
            color = CAJON_COLORS.get(c, '#64748b')
            st.markdown(f"<span style='color:{color}'>●</span> {c}", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⬇️ Descargar Plantilla")
        plantilla = pd.DataFrame({
            'codigo':    ['HEM-001', 'BIO-001', 'MOL-001'],
            'producto':  ['Tubos EDTA 3mL', 'Reactivo Glucosa', 'Taq Polimerasa'],
            'ubicacion': ['HEMATOLOGIA', 'BIOQUIMICA', 'BIOLOGIA MOLECULAR'],
            'stock':     [0, 0, 0],
        })
        csv_p = plantilla.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar Plantilla CSV", csv_p,
                           "plantilla_inventario.csv", "text/csv", use_container_width=True)
