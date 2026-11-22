<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="110" alt="Python Logo">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="110" alt="PostgreSQL Logo">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="110" alt="Docker Logo">
</p>

<div align="center">
  
![Projeto](https://img.shields.io/badge/Projeto-ETL__IBGE-blue)
![Linguagem](https://img.shields.io/badge/Python-3.13-yellow)
![Banco](https://img.shields.io/badge/PostgreSQL-15-336791)
![Infra](https://img.shields.io/badge/Docker-Compose-2496ED)
![Status](https://img.shields.io/badge/Status-Concluido-green)
  
</div>  

---

# 🔄 Pipeline ETL de Dados Abertos - IBGE (Batch)

## 📖 Sobre o Projeto

O **Pipeline ETL de Dados Abertos - IBGE** é uma solução de engenharia de dados desenvolvida para extrair, limpar, transformar e armazenar dados geográficos públicos do Brasil (Regiões, Estados e Municípios) de forma automatizada e containerizada.

O projeto utiliza **Python**, **Pandas**, **SQLAlchemy**, **PostgreSQL** e **Docker Compose**, garantindo reprodutibilidade, integridade referencial e isolamento completo do ambiente de execução.

---

## ⚙️ Funcionalidades

- 🌐 Extração automatizada de dados via API REST pública do IBGE
- 🧹 Desnormalização de JSON aninhado utilizando Pandas
- 🚫 Remoção de registros duplicados e tratamento de valores nulos (`NaN`)
- 🔤 Padronização de strings e conversão segura de tipos (*Type Casting*)
- 🕒 Geração de metadados de controle (`data_ingestao`)
- 🗄️ Modelagem relacional com Chaves Primárias (PK) e Estrangeiras (FK)
- 🐳 Orquestração e containerização completa com Docker Compose
- 🩺 Controle de inicialização entre serviços via *Healthcheck*

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Descrição |
|------------|------------|
| Python 3.13 | Linguagem principal do pipeline |
| Pandas | Limpeza, transformação e normalização dos dados |
| Requests | Consumo da API REST do IBGE |
| SQLAlchemy | ORM e gerenciamento de conexão/transações SQL |
| Psycopg2 | Driver de comunicação entre Python e PostgreSQL |
| PostgreSQL 15 | Banco de dados relacional para persistência |
| Docker & Compose | Containerização e orquestração dos serviços |

---

## 🗄️ Modelagem do Banco de Dados

Os dados são estruturados em três tabelas normalizadas respeitando a hierarquia geográfica do IBGE:

| Tabela | Colunas Principais | Relacionamento |
|--------|--------------------|----------------|
| `regioes` | `id`, `sigla`, `nome` | Chave Primária (`id`) |
| `estados` | `id`, `sigla`, `nome`, `regiao_id` | FK para `regioes(id)` |
| `municipios` | `id`, `nome`, `estado_id`, `data_ingestao` | FK para `estados(id)` |

---

## ⚙️ Etapas do Pipeline (ETL)

### 📥 1. Extract (Extração)

O script realiza uma requisição `GET` no endpoint oficial de localidades do IBGE:
- Validação de status HTTP (`raise_for_status()`).
- Captura de todos os 5.570 municípios brasileiros em formato JSON.

### 🔄 2. Transform (Transformação)

Utilizando `pd.json_normalize()`, o JSON complexo é achatado e dividido em três DataFrames:
- **Higienização:** Remoção de espaços extras (`str.strip()`) e padronização de siglas em caixa alta (`str.upper()`).
- **Integridade:** Descarte de registros nulos (`dropna`) e duplicados (`drop_duplicates`) antes da tipagem para inteiros (`astype(int)`).
- **Auditoria:** Adição da coluna `data_ingestao` com o timestamp exato do processamento.

### 📤 3. Load (Carga)

Com o **SQLAlchemy** (`postgresql+psycopg2`), os dados são inseridos em transação atômica (`engine.begin()`), respeitando a ordem de dependência das chaves estrangeiras:
1. `regioes` (5 registros)
2. `estados` (27 registros)
3. `municipios` (5.570 registros)

---

## 📂 Estrutura do Projeto

```bash
etl-ibge/
├── src/
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── init.sql
├── requirements.txt
├── .gitignore
└── README.md
