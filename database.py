import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# A URL de conexão deve ser configurada nos "Secrets" do Streamlit Cloud
def get_engine():
    # Exemplo de URL: postgresql://postgres:[SENHA]@db.supabase.co:5432/postgres
    url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(url)

def init_db():
    """Cria a tabela no banco de dados se não existir."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS denuncias (
                id SERIAL PRIMARY KEY,
                external_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                origem VARCHAR(100),
                rua VARCHAR(255),
                numero VARCHAR(50),
                bairro VARCHAR(100),
                zona VARCHAR(50),
                latitude FLOAT,
                longitude FLOAT,
                descricao TEXT,
                status VARCHAR(50) DEFAULT 'Pendente'
            );
        """))
        conn.commit()

def salvar_registro(dados):
    """Salva a denúncia e retorna o ID gerado."""
    engine = get_engine()
    with engine.connect() as conn:
        # Lógica para gerar ID Externo (Ex: 0001/2026)
        res = conn.execute(text("SELECT COUNT(*) FROM denuncias"))
        novo_id = f"{(res.scalar() + 1):04d}/{datetime.now().year}"
        
        sql = text("""
            INSERT INTO denuncias (external_id, origem, rua, numero, bairro, zona, latitude, longitude, descricao)
            VALUES (:ext, :orig, :rua, :num, :bair, :zona, :lat, :lon, :desc)
        """)
        conn.execute(sql, {**dados, "ext": novo_id})
        conn.commit()
    return novo_id

def carregar_dados():
    """Lê todos os dados do banco para o DataFrame."""
    engine = get_engine()
    return pd.read_sql("SELECT * FROM denuncias ORDER BY id DESC", engine)
