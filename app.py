import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Painel de Atendimentos", layout="wide")

@st.cache_resource
def get_engine():
    db = st.secrets["database"]
    url = f"postgresql+psycopg2://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
    return create_engine(url)

engine = get_engine()

@st.cache_data(ttl=300)
def load_data(data_inicio, data_fim):
    query = text("""
        SELECT a.numatend, d.nomecc, a.datagrav, a.codope, a.codprest,
               p.nomeprest, p.assinaelet, a.numtexto, a.assinado
        FROM evomed a
        INNER JOIN cadope c ON a.codprest = c.codprest
        INNER JOIN cadprest p ON c.codprest = p.codprest
        INNER JOIN arqatend q ON q.numatend = a.numatend
        INNER JOIN cadcc d ON q.codcc = d.codcc
        WHERE a.datagrav >= :data_inicio AND a.datagrav < :data_fim
    """)
    df = pd.read_sql(query, engine, params={"data_inicio": data_inicio, "data_fim": data_fim})
    return df

# --- Filtro de período ---
st.sidebar.header("Filtros")

periodo = st.sidebar.date_input(
    "Período",
    value=(date.today() - timedelta(days=30), date.today()),
)

if len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    st.stop()

data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
data_fim_dt = datetime.combine(data_fim, datetime.min.time()) + timedelta(days=1)

# --- Carregamento e preparo dos dados ---
df = load_data(data_inicio_dt, data_fim_dt)

df["status_assinatura"] = df["assinado"].map({"S": "Assinado", "N": "Não assinado"})
df["possui_assinatura_eletronica"] = df["assinaelet"].apply(
    lambda x: "Sim" if x == "S" else "Não"
)
df["datagrav"] = pd.to_datetime(df["datagrav"])

# --- Filtros que dependem do df carregado ---
prestadores = st.sidebar.multiselect(
    "Prestador",
    options=sorted(df["nomeprest"].dropna().unique()),
)

centros_custo = st.sidebar.multiselect(
    "Centro de custo",
    options=sorted(df["nomecc"].dropna().unique()),
)

status_filtro = st.sidebar.multiselect(
    "Status da assinatura",
    options=df["status_assinatura"].unique(),
)

df_filtrado = df.copy()
if prestadores:
    df_filtrado = df_filtrado[df_filtrado["nomeprest"].isin(prestadores)]
if centros_custo:
    df_filtrado = df_filtrado[df_filtrado["nomecc"].isin(centros_custo)]
if status_filtro:
    df_filtrado = df_filtrado[df_filtrado["status_assinatura"].isin(status_filtro)]

if st.sidebar.button("Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

# --- Título e métricas ---
st.title("Painel de Atendimentos")
st.caption(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")

col1, col2, col3 = st.columns(3)
total = len(df_filtrado)
assinados = (df_filtrado["status_assinatura"] == "Assinado").sum()
pendentes = total - assinados

col1.metric("Total de textos", total)
col2.metric("Assinados", assinados)
col3.metric("Pendentes", pendentes, delta=f"{pendentes/total:.1%}" if total else "0%")

# --- Tabela detalhada ---
st.subheader("Detalhamento dos atendimentos")
st.dataframe(
    df_filtrado[[
        "numatend", "datagrav", "nomeprest", "nomecc", "numtexto",
        "status_assinatura", "possui_assinatura_eletronica"
    ]],
    use_container_width=True,
    hide_index=True,
)

# --- Pizza e ranking lado a lado ---
col_a, col_b = st.columns(2)

with col_a:
    fig_pizza = px.pie(
        df_filtrado,
        names="status_assinatura",
        title="Proporção de Assinaturas",
        color="status_assinatura",
        color_discrete_map={"Assinado": "#2ecc71", "Não assinado": "#e74c3c"},
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

with col_b:
    st.subheader("Pendências por prestador")
    ranking = (
        df_filtrado[df_filtrado["status_assinatura"] == "Não assinado"]
        .groupby("nomeprest")
        .size()
        .reset_index(name="pendentes")
        .sort_values("pendentes", ascending=False)
    )
    st.bar_chart(ranking.set_index("nomeprest"))