import streamlit as st
import database as db
import folium
from streamlit_folium import st_folium
from io import BytesIO

st.set_page_config(page_title="URB Fiscalização Cloud", layout="wide")
db.init_db()

menu = st.sidebar.selectbox("Navegação", ["Mapa Interativo", "Nova Denúncia", "Exportar Dados"])

if menu == "Mapa Interativo":
    st.title("📍 Localização Automática de Ocorrências")
    df = db.carregar_dados()
    
    # Filtra apenas registros com coordenadas válidas
    df_mapa = df.dropna(subset=['latitude', 'longitude'])
    
    if not df_mapa.empty:
        # Centraliza o mapa na média das coordenadas
        m = folium.Map(location=[df_mapa.latitude.mean(), df_mapa.longitude.mean()], zoom_start=13)
        
        for _, row in df_mapa.iterrows():
            folium.Marker(
                [row.latitude, row.longitude],
                popup=f"OS: {row.external_id}",
                tooltip=f"{row.bairro} - {row.status}",
                icon=folium.Icon(color="red" if row.status == "Pendente" else "green")
            ).add_to(m)
        
        st_folium(m, width="100%", height=500)
    else:
        st.info("Nenhuma coordenada registrada ainda.")

elif menu == "Exportar Dados":
    st.title("📂 Extração de Relatórios")
    df = db.carregar_dados()
    st.dataframe(df)

    # BOTÃO PARA PLANILHA EXCEL
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Denuncias')
    
    st.download_button(
        label="📥 Baixar Planilha (Excel)",
        data=output.getvalue(),
        file_name="relatorio_fiscalizacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
