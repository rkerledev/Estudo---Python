"""API de tarefas com FastAPI + SQLite (CRUD completo)."""

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

BANCO = Path("tarefas.db")


# ---------- Banco de dados ----------

def conectar():
    """Abre a conexão e faz as linhas virarem dicionários (acesso por nome da coluna)."""
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabela():
    with conectar() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tarefas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo    TEXT    NOT NULL,
                concluida INTEGER NOT NULL DEFAULT 0
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda uma vez quando a API liga: garante que a tabela existe."""
    criar_tabela()
    yield


app = FastAPI(title="API de Tarefas", lifespan=lifespan)


# ---------- Modelos (validação dos dados) ----------

class TarefaCriar(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)


class TarefaAtualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    concluida: bool | None = None


class TarefaSaida(BaseModel):
    id: int
    titulo: str
    concluida: bool


def linha_para_tarefa(linha) -> TarefaSaida:
    return TarefaSaida(
        id=linha["id"], titulo=linha["titulo"], concluida=bool(linha["concluida"])
    )


def buscar_ou_404(conn, id_tarefa: int):
    linha = conn.execute(
        "SELECT * FROM tarefas WHERE id = ?", (id_tarefa,)
    ).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return linha


# ---------- Rotas (endpoints) ----------

@app.post("/tarefas", response_model=TarefaSaida, status_code=201)
def criar_tarefa(dados: TarefaCriar):
    titulo = dados.titulo.strip()
    if not titulo:
        raise HTTPException(status_code=422, detail="A tarefa não pode ser vazia.")
    with conectar() as conn:
        cursor = conn.execute("INSERT INTO tarefas (titulo) VALUES (?)", (titulo,))
        linha = buscar_ou_404(conn, cursor.lastrowid)
    return linha_para_tarefa(linha)


@app.get("/tarefas", response_model=list[TarefaSaida])
def listar_tarefas(concluida: bool | None = None):
    """Lista tudo. Use ?concluida=true ou ?concluida=false para filtrar."""
    sql = "SELECT * FROM tarefas"
    params = ()
    if concluida is not None:
        sql += " WHERE concluida = ?"
        params = (int(concluida),)
    sql += " ORDER BY id"
    with conectar() as conn:
        linhas = conn.execute(sql, params).fetchall()
    return [linha_para_tarefa(l) for l in linhas]


@app.get("/tarefas/{id_tarefa}", response_model=TarefaSaida)
def obter_tarefa(id_tarefa: int):
    with conectar() as conn:
        linha = buscar_ou_404(conn, id_tarefa)
    return linha_para_tarefa(linha)


@app.patch("/tarefas/{id_tarefa}", response_model=TarefaSaida)
def atualizar_tarefa(id_tarefa: int, dados: TarefaAtualizar):
    with conectar() as conn:
        atual = buscar_ou_404(conn, id_tarefa)
        novo_titulo = dados.titulo.strip() if dados.titulo is not None else atual["titulo"]
        if not novo_titulo:
            raise HTTPException(status_code=422, detail="A tarefa não pode ser vazia.")
        nova_concluida = (
            int(dados.concluida) if dados.concluida is not None else atual["concluida"]
        )
        conn.execute(
            "UPDATE tarefas SET titulo = ?, concluida = ? WHERE id = ?",
            (novo_titulo, nova_concluida, id_tarefa),
        )
        linha = buscar_ou_404(conn, id_tarefa)
    return linha_para_tarefa(linha)


@app.delete("/tarefas/{id_tarefa}", status_code=204)
def remover_tarefa(id_tarefa: int):
    with conectar() as conn:
        buscar_ou_404(conn, id_tarefa)
        conn.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
    return Response(status_code=204)
