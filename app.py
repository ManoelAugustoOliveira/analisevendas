import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================== configuração_pagina ==================================================#

st.set_page_config(page_title="Análise de vendas Superloja", page_icon=":bar_chart", layout="wide")


@st.cache(allow_output_mutation=True)
# read_data
def get_data(__path__):
    df = pd.read_csv(__path__, sep=',')
    df['Row ID'] = df['Row ID'].astype(str)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Year'] = df['Year'].astype(str)
    df['Month'] = df['Month'].astype(str)
    df['Year-Month'] = df['Year'] + '-' + df['Month']
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Postal Code'] = df['Postal Code'].astype(str)
    return df


data = get_data("datasets/train.csv")

# ==================================================== Sobre ==========================================================#

st.sidebar.write("""Utilize os filtros abaixo:""")
st.title('Análise de vendas Superloja')
st.markdown('Conjunto de dados de varejo de uma superloja global por 4 anos.')
st.subheader("Descrição dos indicadores:")
st.write("""
    As informações analisadas tem por objetivo traçar um panorama referente aos padrões de vendas da Superloja,
    bem como disponibilizar a visualização de alguns indicadores listados abaixo.
    """)
st.markdown('- Total de vendas por período.')
st.markdown('- Total de vendas por Categoria/Sub-Categoria.')
st.markdown('- Total de vendas por Estado/Cidade.')
st.markdown('- Ticket médio.')
st.markdown('- Total de clientes atendidos.')
st.markdown('----')

# ===================================================== Dashboard =====================================================#

st.header('Report: Análise de vendas')
st.markdown('')

# filtros
regiao = st.sidebar.multiselect(
    'Região',
    options=data['Region'].unique(),
    default=data['Region'].unique()
)

segmento = st.sidebar.multiselect(
    'Segmento',
    options=data['Segment'].unique(),
    default=data['Segment'].unique()
)

categoria = st.sidebar.multiselect(
    'Categoria',
    options=data['Category'].unique(),
    default=data['Category'].unique()
)

data_selection = data.query(
    " Segment == @segmento & Region == @regiao & Category == @categoria "
)

# metricas
total_vendas = round(data_selection['Sales'].sum(), 2)
total_pedidos = len(data_selection['Order ID'].unique())
total_clientes = len(data_selection['Customer ID'].unique())
total_pedidos_clientes = round(total_pedidos / total_clientes, 2)
vendas_por_pedido = round(total_vendas / total_pedidos, 2)
media_mensal = round(total_vendas / len(data_selection['Year-Month'].unique()))

# formatacao_metricas
valor_real = "R$ {:,.2f}".format(total_vendas).replace(",", "X").replace(".", ",").replace("X", ".")
valor_pedidos = '{0:,}'.format(total_pedidos).replace(',', '.')
valor_clientes = '{0:,}'.format(total_clientes).replace(',', '.')
pedidos_por_cliente = '{0:,}'.format(total_clientes).replace(',', '.')
ticket_medio = "R$ {:,.2f}".format(vendas_por_pedido).replace(",", "X").replace(".", ",").replace("X", ".")
media_mes = "R$ {:,.2f}".format(media_mensal).replace(",", "X").replace(".", ",").replace("X", ".")

left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.metric('Total de Vendas', valor_real, delta=f'Média mensal: {media_mes}', delta_color='off')

with middle_column:
    st.metric('Total de pedidos', valor_pedidos, delta=f'Ticket medio: {ticket_medio}')

with right_column:
    st.metric('Total de clientes atendidos', valor_clientes, delta=f'Pedidos por cliente: {total_pedidos_clientes}')

st.markdown('-----')
# gráficos
# Vendas por ano mês
vendas_por_ano_mes = (data_selection.groupby(by=["Year-Month"]).sum()[["Sales"]].sort_values(by="Year-Month"))
fig_vendas_ano_mes = px.bar(
    vendas_por_ano_mes,
    x=vendas_por_ano_mes.index,
    y='Sales',
    title="<b>Vendas por período</b>",
    color_discrete_sequence=["#0083B8"] * len(vendas_por_ano_mes),
    template="plotly_white", text_auto='.2s'
)
fig_vendas_ano_mes.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)
           ),
    hovermode="x unified"
)
st.plotly_chart(fig_vendas_ano_mes, use_container_width=True)

# Vendas por sub-categoria
vendas_por_subcategory = (data_selection.groupby(by=["Sub-Category"]).sum()[["Sales"]].sort_values(by="Sales"))
fig_vendas_subcategory = px.bar(
    vendas_por_subcategory,
    x='Sales',
    y=vendas_por_subcategory.index,
    title="<b>Vendas por Sub-Categoria</b>",
    color_discrete_sequence=["#0083B8"] * len(vendas_por_subcategory),
    template="plotly_white",
)
fig_vendas_subcategory.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)
           ),
    hovermode="y unified"
)

st.markdown('----------')

# vendas por segmento
fig_segment = px.pie(data_selection, title="<b>Vendas por Segmento</b>", values='Sales', names='Segment', color='Segment',
                     color_discrete_map={'Consumer': 'darkblue',
                                         'Corporate': 'cyan',
                                         'Home Office': 'royalblue'}, hole=.6)

left_column, middle_column = st.columns(2)
left_column.plotly_chart(fig_vendas_subcategory, use_container_width=True)
middle_column.plotly_chart(fig_segment, use_container_width=True)

st.markdown('----------')

# Vendas por estado
vendas_por_estado = (data_selection.groupby(by=["State"]).sum()[["Sales"]].sort_values(by="Sales", ascending=False))
fig_vendas_estado = px.bar(
    vendas_por_estado,
    x=vendas_por_estado.index,
    y='Sales',
    title="<b>Vendas por estado</b>",
    color_discrete_sequence=["#0083B8"] * len(vendas_por_estado),
    template="plotly_white",
)
fig_vendas_estado.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)
           ),
    hovermode="y unified",
)

st.plotly_chart(fig_vendas_estado, use_container_width=True)


# ===================================================== Download data ================================================#

st.markdown('----------')
st.subheader('Data Overview')
st.write(data)


# Download_button
def get_data(__path__):
    df = pd.read_csv(__path__, sep=',')
    return df.to_csv().encode('utf-8')


data = get_data("datasets/train.csv")
st.download_button(
    label="Download_CSV",
    data=data,
    file_name='datasets/train.csv',
    mime='text/csv',
)
