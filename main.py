import os
import sqlite3
import flet as ft

import database
import gerador
import hub
import cria_time2


def obter_id_usuario_com_time():
    """
    Verifica se existe algum utilizador na base de dados que já possua uma equipa.
    Garante a migração e sincronização das colunas de escudos e fotos na BD.
    """
    database.inicializar_banco()

    conn = gerador.conectar_bd()
    cursor = conn.cursor()
    try:
        gerador.garantir_colunas(cursor, conn)

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
    page.title = "FootManager"
    page.bgcolor = "#0F172A"

    database.inicializar_banco()
    id_usuario = obter_id_usuario_com_time()

    if id_usuario:
        hub.carregar_hub(page, id_usuario)
    else:
        cria_time2.main(page)


if __name__ == "__main__":
    # Caminho absoluto para a pasta assets, evitando falhas de diretório
    caminho_assets = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "assets")
    ft.app(target=main, assets_dir=caminho_assets)
