# Dashboard: Rendimento dos Responsáveis pelo Domicílio
# Projeto Integrador - Números que Falam

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Números que Falam: Rendimento dos Responsáveis")

st.sidebar.header("Dados")
arquivo = st.sidebar.file_uploader("Envie um CSV ou XLSX", type=["csv", "xlsx"])

if arquivo is None:
    # se ninguém enviou nada, usa o arquivo de exemplo
    df = pd.read_csv("exemplo_rendimento.csv")
    st.sidebar.info("Usando dados de EXEMPLO. Envie o seu arquivo do IBGE.")
elif arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

#  2 Limpar os dados (ETL) 
df = df.dropna()                        
df = df.drop_duplicates()               
df["Rendimento"] = pd.to_numeric(df["Rendimento"], errors="coerce")
df = df.dropna()

#  3 Filtros 
regioes = st.sidebar.multiselect(
    "Região", sorted(df["Regiao"].unique()), default=sorted(df["Regiao"].unique())
)
df = df[df["Regiao"].isin(regioes)]

ufs = st.sidebar.multiselect(
    "UF", sorted(df["UF"].unique()), default=sorted(df["UF"].unique())
)
df = df[df["UF"].isin(ufs)]

if df.empty:
    st.warning("Escolha pelo menos uma região e uma UF.")
    st.stop()

#  4. Estatísticas 
x = df["Rendimento"]

media = x.mean()
mediana = x.median()
moda = x.mode()[0]
q1 = x.quantile(0.25)
q3 = x.quantile(0.75)
iqr = q3 - q1
amplitude = x.max() - x.min()
desvio = x.std()

# regra 1,5 x IQR para outliers
limite_inf = q1 - 1.5 * iqr
limite_sup = q3 + 1.5 * iqr
outliers = df[(x < limite_inf) | (x > limite_sup)]

#  5 Cards (KPIs) 
st.subheader("Principais números")
c1, c2, c3 = st.columns(3)
c1.metric("Média", f"R$ {media:,.2f}")
c2.metric("Mediana", f"R$ {mediana:,.2f}")
c3.metric("IQR", f"R$ {iqr:,.2f}")

c4, c5, c6 = st.columns(3)
c4.metric("Desvio padrão", f"R$ {desvio:,.2f}")
c5.metric("Amplitude", f"R$ {amplitude:,.2f}")
c6.metric("Moda", f"R$ {moda:,.2f}")

st.write(f"Q1 = R$ {q1:,.2f}  |  Q3 = R$ {q3:,.2f}")

#  6 Gráficos 
st.subheader("Boxplot")
st.plotly_chart(px.box(df, y="Rendimento", points="all", hover_name="UF"))

st.subheader("Rendimento por UF")
st.plotly_chart(px.bar(df.sort_values("Rendimento"), x="UF", y="Rendimento", color="Regiao"))

#  7 Outliers 
st.subheader("Outliers (regra 1,5 x IQR)")
st.write(f"Limite inferior: R$ {limite_inf:,.2f}  |  Limite superior: R$ {limite_sup:,.2f}")
if outliers.empty:
    st.write("Nenhum outlier encontrado.")
else:
    st.dataframe(outliers)

#  8 Interpretação 
st.subheader("O que os números dizem")
if media > mediana:
    st.write("A média é maior que a mediana. Isso mostra que alguns valores muito altos "
             "puxam a média para cima. Para um gestor público, a mediana representa melhor "
             "o rendimento típico.")
else:
    st.write("A média e a mediana são parecidas, então os dados são mais equilibrados.")

st.write(f"O desvio padrão de R$ {desvio:,.2f} mostra o quanto os estados são diferentes entre si.")
