"""Lista de tarefas simples em Python"""

import json
from pathlib import Path

ARQUIVO = Path("tarefas.json")


#----------- Persistência de dados -----------#
def carregar_tarefas():
    """Carrega as tarefas do arquivo JSON"""
    if  not ARQUIVO.exists():
        return []
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def salvar_tarefas(tarefas):    
    """Salva as tarefas no arquivo JSON"""
    with ARQUIVO.open("w", encoding="utf-8") as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=2)


 #----------- Funções de manipulação de tarefas -----------#


def proximo_id(tarefas): 
    """Gera  um novo id novo: o maior id existente + 1"""
    return max((t["id"] for t in tarefas), default=0) + 1


def ler_id(mensagem):
    """Pede um numero ao usuario e trata entradas inválida"""
    try:
            return int(input(mensagem))
    except ValueError:
            print("Digite um número inteiro válido.")
    return None


def buscar_por_id(tarefas, id_tarefa):
    """Busca uma tarefa pelo id"""
    for tarefa in tarefas:
        if tarefa["id"] == id_tarefa:
            return tarefa
    return None


# ----------Ações do menu ----------#

def adicionar(tarefas):
    titulo = input("título da tarefa: ").strip()
    if not titulo:
        print("A tarefa não pode ser vazia.")
        return
    tarefas.append({"id": proximo_id(tarefas), "titulo": titulo, "concluida": False})
    salvar_tarefas(tarefas)
    print("Tarefa adicionada!")


def listar(tarefas):
    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
        return
    print("\n---Suas tarefas---")
    for t in tarefas:
        marcador = "[x]" if t["concluida"] else "[ ]"
        print(f'{t["id"]:>3} {marcador} {t["titulo"]}')


def concluir(tarefas):
    id_tarefa = ler_id("Digite o ID da tarefa a ser concluída: ")
    if id_tarefa is None:
        return
    tarefa = buscar_por_id(tarefas, id_tarefa)
    if tarefa is None:
        print("Tarefa não encontrada.")
        return
    tarefa["concluida"] = True
    salvar_tarefas(tarefas)
    print("Tarefa concluída!")


    
def remover(tarefas):
        id_tarefa = ler_id("Id da tarefa a remover: ")
        if id_tarefa is None:
            return
        tarefa = buscar_por_id(tarefas, id_tarefa)
        if tarefa is None:
            print("Tarefa não encontrada.")
            return
        tarefas.remove(tarefa)
        salvar_tarefas(tarefas)
        print("Tarefa removida!")


# ---------- Menu principal ----------#


def menu():
    print(
        "\n=== GERENCIADOR DE TAREFAS ===\n" \
        "1. Adicionar tarefa\n" \
        "2. Listar tarefas\n" \
        "3. Concluir tarefa\n" \
        "4. Remover tarefa\n" \
        "0. Sair\n"
    )
    return input("Escolha uma opção: ").strip()


def  main():
    tarefas = carregar_tarefas()
    acoes = {"1": adicionar, "2": listar, "3": concluir, "4": remover}
    
    while True:
        opcao = menu()
        if opcao == "0":
            print("Ate mais!")
            break
        acao = acoes.get(opcao)
        if acao:
            acao(tarefas)
        else:
            print("Opção inválida.")



if __name__ == "__main__":
    main()
    