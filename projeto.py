import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from geopy.distance import geodesic

########################### Banco de dados ###########################
df_hospitais = pd.read_csv("bases/hospital.csv",sep=";")
df_hospitais['NOME'] = df_hospitais['NOME'].astype(str).str.strip()
df_funerarias = pd.read_csv("bases/funeraria.csv",sep=";")
df_funerarias['NOME'] = df_funerarias['NOME'].astype(str).str.strip()
df_cemiterios = pd.read_csv("bases/cemiterio.csv",sep=";")
df_cemiterios['NOME'] = df_cemiterios['NOME'].astype(str).str.strip()
df_cemiterios = df_cemiterios[df_cemiterios['TIPO'].str.contains('Cemitério em Fortaleza, Ceará', na=False)]
df_total = pd.concat([df_hospitais, df_funerarias, df_cemiterios], ignore_index=True)

########################### Sidebar ########################### 
with st.sidebar:
    st.title("Equipe:")
    st.text('MARCO ANTONIO SOLDON BRAGA FILHO')
    st.caption("Front-end")
    st.text('WILKER SANTOS DE SOUSA')
    st.caption("Engenheiro de dados")
    st.text('LUCAS ARAUJO FELIX PORTELA')
    st.caption("Cientista de dados")
    st.text('ALISON HERCULANO FERREIRA')
    st.caption("Backend")

tab0,tab1,tab2, = st.tabs(["Introdução","Visão Geral", "Mapa Interativo"])

########################### Aba 1: Introdução ###########################
with tab0:
    st.header('Projeto Descanse em Paz')
    st.image('imagens/Morte.jpg')
    st.write('Este trabalho tem como objetivo apresentar os cemitérios e funerárias mais próximos dos hospitais de Fortaleza, facilitando o acesso a esses serviços')
    st.write('A ideia mostrar localização dos hospitais, funerárias e cemitérios próximos entre si, permitindo que as pessoas encontrem facilmente esses locais quando necessário.')
    st.write('A seguir, apresentamos os dados coletados e as análises realizadas para identificar os principais hospitais, funerárias e cemitérios da cidade de Fortaleza.')
    st.write('Agradecemos a todos os envolvidos na coleta e análise dos dados, bem como aos profissionais de saúde e serviços funerários que desempenham um papel fundamental na comunidade.')
    st.write('Esperamos que este trabalho possa ser útil para aqueles que necessitam desses serviços em momentos difíceis.')

########################### Aba 2: Visão Geral ###########################
with tab1:
    st.title("Visão Geral dos Dados")

    col1, col2, col3 = st.columns(3)
    col1.metric("Hospitais", df_hospitais.shape[0])
    col2.metric("Funerárias", df_funerarias.shape[0])
    col3.metric("Cemitérios", df_cemiterios.shape[0])

    st.subheader("Distribuição das Notas")

    tipo_escolhido = st.selectbox(
        "Selecione o tipo de estabelecimento:",
        ["Hospitais", "Funerárias", "Cemitérios"]
    )

    df_hospitais['tipo'] = 'Hospital'
    df_funerarias['tipo'] = 'Funerária'
    df_cemiterios['tipo'] = 'Cemitério'
    df_avaliacoes = pd.concat([df_hospitais, df_funerarias, df_cemiterios], ignore_index=True)

    tipo_map = {
        "Hospitais": "Hospital",
        "Funerárias": "Funerária",
        "Cemitérios": "Cemitério"
    }

    df_filtrado = df_avaliacoes[df_avaliacoes['tipo'] == tipo_map[tipo_escolhido]]

    fig = px.histogram(
        df_filtrado,
        x="PONTUACAO",
        color="tipo",
        color_discrete_map={
            "Hospital": "lightcoral",
            "Funerária": "lightskyblue",
            "Cemitério": "lightgreen"
        }
    )
    fig.update_layout(
        legend_title_text='Tipo de Estabelecimento',
        xaxis_title="PONTUAÇÃO",
        yaxis_title="CONTAGEM"
    )
    fig.update_layout(legend_title_text='Tipo de Estabelecimento')
    st.plotly_chart(fig, use_container_width=True)

    # Mapa
    st.subheader("Mapa com Estabelecimentos")

    if tipo_escolhido == "Hospitais":
        df_tipo = df_hospitais.copy()
        cor = "red"
        icone = "plus"
    elif tipo_escolhido == "Funerárias":
        df_tipo = df_funerarias.copy()
        cor = "blue"
        icone = "bell"
    else:
        df_tipo = df_cemiterios.copy()
        cor = "green"
        icone = "cross"

    mapa = folium.Map(location=[-3.75, -38.52], zoom_start=12)

    for _, row in df_tipo.iterrows():
        popup_text = f"Nota: {row['PONTUACAO']}\n{row['LOCAL']}" if tipo_escolhido != "Hospitais" else f"{row['LOCAL']}"
        folium.Marker(
            [row['LAT'], row['LON']],
            tooltip=row['NOME'],
            popup=popup_text,
            icon=folium.Icon(
                color=cor, 
                icon=icone,
                prefix='fa'
            )
        ).add_to(mapa)

    st_folium(mapa, width=700, height=500)

    # Tabela
    df_tipo_ordenado = df_tipo.sort_values(by='PONTUACAO', ascending=False).reset_index(drop=True)
    st.subheader(f"Lista de {tipo_escolhido} ordenada por pontuação")
    st.dataframe(df_tipo_ordenado[['NOME', 'PONTUACAO', 'LOCAL']])


########################### Aba 3: Mapa Interativo ###########################
with tab2:
    st.title("Localizar Estabelecimentos Próximos")

    hosp_selecionado = st.selectbox("Escolha o hospital:", df_hospitais['NOME'].unique())
    nota_minima = st.slider("Nota mínima desejada:", 0.0, 5.0, 3.5, 0.1)
    dist_maxima = st.slider("Distância máxima (km):", 1.0, 30.0, 3.0, 0.5) 

    hosp = df_hospitais[df_hospitais['NOME'] == hosp_selecionado].iloc[0]
    coord_hosp = (hosp['LAT'], hosp['LON'])

    def filtrar_proximos(df):
        df_filtrado = df[df['PONTUACAO'] >= nota_minima].copy()
        df_filtrado['dist_km'] = df_filtrado.apply(
            lambda row: geodesic(coord_hosp, (row['LAT'], row['LON'])).km, axis=1
        )
        df_filtrado = df_filtrado[df_filtrado['dist_km'] <= dist_maxima]
        return df_filtrado.sort_values("dist_km")

    funerarias_proximas = filtrar_proximos(df_funerarias)
    cemiterios_proximos = filtrar_proximos(df_cemiterios)

    mapa = folium.Map(location=coord_hosp, zoom_start=13)

    #hospital
    folium.Marker(
        location=coord_hosp,
        tooltip=hosp['NOME'],
        popup=f"Hospital: {hosp['NOME']}\n{hosp['LOCAL']}",
        icon=folium.Icon(color="red", icon="plus", prefix='fa')
    ).add_to(mapa)

    #funerárias
    for _, row in funerarias_proximas.iterrows():
        folium.Marker(
            location=(row['LAT'], row['LON']),
            tooltip=row['NOME'],
            popup=f"Funerária - Nota: {row['PONTUACAO']}\n{row['LOCAL']}",
            icon=folium.Icon(color="blue", icon="bell", prefix='fa')
        ).add_to(mapa)

    #cemitérios
    for _, row in cemiterios_proximos.iterrows():
        folium.Marker(
            location=(row['LAT'], row['LON']),
            tooltip=row['NOME'],
            popup=f"Cemitério - Nota: {row['PONTUACAO']}\n{row['LOCAL']}",
            icon=folium.Icon(color="green", icon="cross", prefix='fa')
        ).add_to(mapa)

    st.subheader("Mapa com Estabelecimentos Próximos")
    st_folium(mapa, width=700, height=500)

    st.subheader("Funerárias mais próximas")
    st.dataframe(funerarias_proximas[['NOME', 'PONTUACAO', 'LOCAL', 'dist_km']])
    st.subheader("Cemitérios mais próximos")
    st.dataframe(cemiterios_proximos[['NOME', 'PONTUACAO', 'LOCAL', 'dist_km']])
