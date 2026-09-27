import os
import logging
import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configurações de conexão
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ibge_db")
DB_USER = os.getenv("DB_USER", "user_etl")
DB_PASS = os.getenv("DB_PASS", "postgres_password")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def extract_ibge_data() -> list:
    """Extrai dados brutos da API de Municípios do IBGE."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    logging.info("Iniciando extração de dados do IBGE...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def transform_data(raw_data: list):
    """Limpa, padroniza e separa os dados em tabelas relacionais."""
    logging.info("Iniciando transformação de dados com Pandas...")

    # Normalização do JSON complexo
    df_flat = pd.json_normalize(raw_data)

    # 1. Tabela Regiões
    df_regioes = df_flat[[
        'microrregiao.mesorregiao.UF.regiao.id',
        'microrregiao.mesorregiao.UF.regiao.sigla',
        'microrregiao.mesorregiao.UF.regiao.nome'
    ]].copy()
    
    df_regioes.columns = ['id', 'sigla', 'nome']
    df_regioes = df_regioes.dropna(subset=['id']).drop_duplicates(subset=['id'])
    df_regioes['id'] = df_regioes['id'].astype(int)
    df_regioes['sigla'] = df_regioes['sigla'].astype(str).str.strip().str.upper()

    # 2. Tabela Estados (UF)
    df_estados = df_flat[[
        'microrregiao.mesorregiao.UF.id',
        'microrregiao.mesorregiao.UF.sigla',
        'microrregiao.mesorregiao.UF.nome',
        'microrregiao.mesorregiao.UF.regiao.id'
    ]].copy()
    
    df_estados.columns = ['id', 'sigla', 'nome', 'regiao_id']
    df_estados = df_estados.dropna(subset=['id', 'regiao_id']).drop_duplicates(subset=['id'])
    df_estados['id'] = df_estados['id'].astype(int)
    df_estados['regiao_id'] = df_estados['regiao_id'].astype(int)
    df_estados['sigla'] = df_estados['sigla'].astype(str).str.strip().str.upper()

    # 3. Tabela Municípios
    df_municipios = df_flat[[
        'id',
        'nome',
        'microrregiao.mesorregiao.UF.id'
    ]].copy()
    
    df_municipios.columns = ['id', 'nome', 'estado_id']
    
    # Tratamento de nulos antes da conversão de tipo
    df_municipios = df_municipios.dropna(subset=['id', 'nome', 'estado_id'])
    df_municipios = df_municipios.drop_duplicates(subset=['id'])
    
    # Conversão segura para inteiro
    df_municipios['id'] = df_municipios['id'].astype(int)
    df_municipios['estado_id'] = df_municipios['estado_id'].astype(int)
    df_municipios['nome'] = df_municipios['nome'].astype(str).str.strip()
    df_municipios['data_ingestao'] = datetime.now()

    logging.info("Transformação concluída com sucesso.")
    return df_regioes, df_estados, df_municipios

def load_data(df_regioes, df_estados, df_municipios):
    """Carrega os dados estruturados no banco de dados PostgreSQL."""
    logging.info("Conectando ao banco de dados PostgreSQL...")
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        # Inserção respeitando as chaves estrangeiras (FKs)
        logging.info("Inserindo dados na tabela 'regioes'...")
        df_regioes.to_sql('regioes', conn, if_exists='append', index=False)

        logging.info("Inserindo dados na tabela 'estados'...")
        df_estados.to_sql('estados', conn, if_exists='append', index=False)

        logging.info("Inserindo dados na tabela 'municipios'...")
        df_municipios.to_sql('municipios', conn, if_exists='append', index=False)

    logging.info("Carga de dados concluída com sucesso!")

if __name__ == "__main__":
    try:
        data = extract_ibge_data()
        regioes, estados, municipios = transform_data(data)
        load_data(regioes, estados, municipios)
    except Exception as e:
        logging.error(f"Falha na execução do pipeline: {e}")
        raise