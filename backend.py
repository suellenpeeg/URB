import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import streamlit as st
from datetime import datetime

# =======================================================
# CONFIGURAÇÃO DO BANCO (POSTGRESQL)
# =======================================================

# Pega a senha dos segredos do Streamlit Cloud
def get_connection_string():
    return st.secrets["connections"]["postgresql"]["url"]

def get_engine():
    # Cria a conexão com o banco na nuvem
    return create_engine(get_connection_string())

# =======================================================
# CRIAÇÃO DA TABELA (Executa só na primeira vez)
# =======================================================
def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS denuncias (
                id SERIAL PRIMARY KEY,
                external_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                origem VARCHAR(100),
                rua VARCHAR(200),
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

# =======================================================
# FUNÇÕES DE AÇÃO (CRUD)
# =======================================================

def salvar_denuncia(dados):
    """Recebe um dicionário e salva no banco seguro"""
    engine = get_engine()
    
    # Gerar ID Externo (Ex: 001/2026)
    # Lógica simples: conta quantos tem e soma 1
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM denuncias"))
        count = result.scalar()
        novo_id = count + 1
        ano = datetime.now().year
        ext_id = f"{novo_id:03d}/{ano}"

    # Prepara o SQL de inserção
    sql = text("""
        INSERT INTO denuncias (external_id, origem, rua, numero, bairro, zona, latitude, longitude, descricao, status)
        VALUES (:ext, :orig, :rua, :num, :bair, :zona, :lat, :lon, :desc, 'Pendente')
    """)

    # Executa
    with engine.connect() as conn:
        conn.execute(sql, {
            "ext": ext_id,
            "orig": dados['origem'],
            "rua": dados['rua'],
            "num": dados['numero'],
            "bair": dados['bairro'],
            "zona": dados['zona'],
            "lat": dados['latitude'],
            "lon": dados['longitude'],
            "desc": dados['descricao']
        })
        conn.commit()
    
    return ext_id

def carregar_dados():
    """Lê o banco e retorna um DataFrame do Pandas"""
    engine = get_engine()
    # Pandas lê SQL direto, muito rápido
    df = pd.read_sql("SELECT * FROM denuncias ORDER BY id DESC", engine)
    return df
