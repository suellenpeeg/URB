import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    # Puxa a URL diretamente dos Secrets configurados na sua imagem
    return create_engine(st.secrets["connections"]["postgresql"]["url"])

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # Criação da tabela com o campo 'observacoes' solicitado
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS denuncias (
                id SERIAL PRIMARY KEY,
                external_id TEXT,
                created_at TIMESTAMP,
                origem TEXT,
                tipo TEXT,
                num_encaminhamento TEXT,
                rua TEXT,
                numero TEXT,
                bairro TEXT,
                zona TEXT,
                ponto_referencia TEXT,
                latitude TEXT,
                longitude TEXT,
                link_maps TEXT,
                descricao TEXT,
                observacoes TEXT,
                quem_recebeu TEXT,
                status TEXT DEFAULT 'Pendente',
                acao_noturna TEXT DEFAULT 'FALSE'
            );
        """))
        conn.commit()

def load_data():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM denuncias ORDER BY id DESC", engine)
