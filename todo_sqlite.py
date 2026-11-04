import sqlite3
from pathlib import Path

BANCO = Path ("tarefas.db")


# ----- BANCO DE DADOS -----

def conectar():
    """Conecta ao banco de dados SQLite e retorna a conexão."""
    return sqlite3.connect(BANCO)

def criar_tabela():
    """Cria a tabela de tarefas no banco de dados, se não existir."""
    with conectar() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                concluida BOOLEAN NOT NULL CHECK (concluida IN (0, 1))
            )
        ''')
        conn.commit()

