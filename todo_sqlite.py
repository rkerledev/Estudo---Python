"""Lista de tarefas no terminal, agora salvando os dados em um banco SQLite."""

import sqlite3
from pathlib import Path

BANCO = Path("tarefas.db")


# ---------- Banco de dados ----------

def conectar():
    """Abre a conexão com o banco (o arquivo é criado se não existir)."""
    return sqlite3.connect(BANCO)


def criar_tabela():
    """Cria a tabela 'tarefas' caso ela ainda não exista."""
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


# ---------- Funções auxiliares ----------

def ler_id(mensagem):
    """Pede um número ao usuário e trata entrada inválida."""
    try:
        return int(input(mensagem))
    except ValueError:
        print("Digite um número válido.")
        return None


# ---------- Ações do menu ----------

def adicionar():
    titulo = input("Título da tarefa: ").strip()
    if not titulo:
        print("A tarefa não pode ser vazia.")
        return
    with conectar() as conn:
        conn.execute("INSERT INTO tarefas (titulo) VALUES (?)", (titulo,))
    print("Tarefa adicionada!")


def listar():
    with conectar() as conn:
        linhas = conn.execute(
            "SELECT id, titulo, concluida FROM tarefas ORDER BY id"
        ).fetchall()
    if not linhas:
        print("Nenhuma tarefa cadastrada.")
        return
    print("\n--- Suas tarefas ---")
    for id_tarefa, titulo, concluida in linhas:
        marcador = "[x]" if concluida else "[ ]"
        print(f"{id_tarefa:>3} {marcador} {titulo}")


def concluir():
    id_tarefa = ler_id("Id da tarefa a concluir: ")
    if id_tarefa is None:
        return
    with conectar() as conn:
        cursor = conn.execute(
            "UPDATE tarefas SET concluida = 1 WHERE id = ?", (id_tarefa,)
        )
    if cursor.rowcount == 0:
        print("Tarefa não encontrada.")
    else:
        print("Tarefa concluída!")


def remover():
    id_tarefa = ler_id("Id da tarefa a remover: ")
    if id_tarefa is None:
        return
    with conectar() as conn:
        cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
    if cursor.rowcount == 0:
        print("Tarefa não encontrada.")
    else:
        print("Tarefa removida!")


# ---------- Programa principal ----------

def menu():
    print(
        "\n=== GERENCIADOR DE TAREFAS (SQLite) ===\n"
        "1 - Adicionar tarefa\n"
        "2 - Listar tarefas\n"
        "3 - Concluir tarefa\n"
        "4 - Remover tarefa\n"
        "0 - Sair"
    )
    return input("Escolha uma opção: ").strip()


def main():
    criar_tabela()
    acoes = {"1": adicionar, "2": listar, "3": concluir, "4": remover}

    while True:
        opcao = menu()
        if opcao == "0":
            print("Até mais!")
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()