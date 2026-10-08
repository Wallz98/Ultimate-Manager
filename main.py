import sqlite3
import flet as ft

import database
import gerador
import hub
import cria_time


def obter_id_usuario_com_time():
    """
    Verifica se existe algum utilizador na base de dados que já possua uma equipa.
    Retorna o ID do utilizador se encontrar, ou None se não houver equipas.
    """
    database.inicializar_banco()

    conn = gerador.conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.id 
            FROM usuarios u
            INNER JOIN times t ON t.id_usuario = u.id
            ORDER BY u.id ASC LIMIT 1
        """)
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else None
    except sqlite3.OperationalError:
        conn.close()
        return None


def main(page: ft.Page):
    # Configurações gerais da janela
    page.title = "FootManager"
    page.bgcolor = "#0F172A"

    # 1. Garante a inicialização das tabelas
    database.inicializar_banco()

    # 2. Verifica a existência de um clube registado
    id_usuario = obter_id_usuario_com_time()

    if id_usuario:
        # Se já existir equipa, abre o Hub diretamente
        hub.carregar_hub(page, id_usuario)
    else:
        # Se não existir equipa, direciona para a criação de clube
        cria_time.main(page)


if __name__ == "__main__":
    ft.app(target=main)
