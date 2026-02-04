import streamlit as st
import pandas as pd
from io import BytesIO
import folium
from streamlit_folium import st_folium
import backend as api # Importamos nosso arquivo de backend

# Configuração da Página
st.set_page_config(page_title="URB Fiscalização Cloud", layout="wide")

# Inicializa o banco se não existir (segurança)
try:
    api.init_db()
except Exception as e:
    st.error(f"Erro ao conectar no banco: {e}")

st.title("☁️ Sistema URB - Nuvem Segura")

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["Dashboard & Mapa", "Nova Denúncia", "Exportar Dados"])

# =======================================================
# 1. DASHBOARD & MAPA (O pino aparece automático aqui)
# =======================================================
if menu == "Dashboard & Mapa":
    st.subheader("📍 Monitoramento em Tempo Real")
    
    # Busca dados frescos do banco
    df = api.carregar_dados()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Ocorrências", len(df))
        col2.metric("Pendentes", len(df[df['status'] == 'Pendente']))
        col3.metric("Concluídas", len(df[df['status'] == 'Concluída']))
        
        st.divider()
        
        # --- MAPA INTELIGENTE ---
        # Filtra apenas quem tem GPS válido
        df_map = df[(df['latitude'].notnull()) & (df['longitude'].notnull()) & (df['latitude'] != 0)]
        
        if not df_map.empty:
            # Centraliza o mapa na média das ocorrências
            centro_lat = df_map['latitude'].mean()
            centro_lon = df_map['longitude'].mean()
            
            m = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)
            
            for _, row in df_map.iterrows():
                # Cor do pino baseada no status
                cor = "red" if row['status'] == 'Pendente' else "green"
                
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=f"<b>{row['external_id']}</b><br>{row['descricao']}",
                    tooltip=f"{row['bairro']} ({row['status']})",
                    icon=folium.Icon(color=cor, icon="info-sign")
                ).add_to(m)
            
            st_folium(m, width="100%", height=500)
        else:
            st.info("Nenhuma denúncia com geolocalização para exibir no mapa.")
            
    else:
        st.warning("O banco de dados está vazio.")

# =======================================================
# 2. NOVA DENÚNCIA (Conexão com Backend)
# =======================================================
elif menu == "Nova Denúncia":
    st.header("📝 Registrar Ocorrência")
    
    with st.form("form_denuncia"):
        c1, c2 = st.columns(2)
        origem = c1.selectbox("Origem", ["Telefone", "Whatsapp", "Ouvidoria", "Fiscalização"])
        zona = c2.selectbox("Zona", ["Norte", "Sul", "Leste", "Oeste", "Centro"])
        
        rua = st.text_input("Logradouro")
        c3, c4 = st.columns(2)
        numero = c3.text_input("Número")
        bairro = c4.text_input("Bairro")
        
        st.markdown("---")
        st.caption("Coordenadas para o Mapa (Pode pegar do Google Maps)")
        cc1, cc2 = st.columns(2)
        lat = cc1.number_input("Latitude", format="%.6f", value=0.0)
        lon = cc2.number_input("Longitude", format="%.6f", value=0.0)
        
        desc = st.text_area("Descrição da Ocorrência")
        
        btn = st.form_submit_button("💾 Salvar no Sistema")
        
    if btn:
        if not rua or not bairro:
            st.error("Rua e Bairro são obrigatórios.")
        else:
            # Prepara o pacote de dados
            payload = {
                "origem": origem, "zona": zona, "rua": rua, 
                "numero": numero, "bairro": bairro,
                "latitude": lat, "longitude": lon, "descricao": desc
            }
            
            # Envia para o backend
            try:
                novo_id = api.salvar_denuncia(payload)
                st.success(f"Sucesso! Protocolo gerado: {novo_id}")
                st.info("Ocorrência já disponível no Mapa e na Planilha.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# =======================================================
# 3. EXPORTAR DADOS (Excel)
# =======================================================
elif menu == "Exportar Dados":
    st.header("📂 Gerenciamento de Dados")
    
    df = api.carregar_dados()
    st.dataframe(df, use_container_width=True)
    
    # Lógica do Excel em memória (buffer)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Denuncias', index=False)
        
    st.download_button(
        label="📥 Baixar Planilha Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"relatorio_urb_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
        mime="application/vnd.ms-excel"
    )
