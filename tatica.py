import flet as ft
import sqlite3

# Definição das posições necessárias por formação
ESQUEMAS_TATICOS = {
    "4-4-2": {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 4, "ATA": 2},
    "4-3-3": {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 3, "ATA": 3},
    "3-5-2": {"GOL": 1, "ZAG": 3, "LAT": 0, "MEI": 5, "ATA": 2},
    "5-3-2": {"GOL": 1, "ZAG": 3, "LAT": 2, "MEI": 3, "ATA": 2},
    "4-5-1": {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 5, "ATA": 1},
}


def obter_jogadores(id_time):
    """Busca a lista de jogadores da equipa no banco de dados."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa
        FROM jogadores WHERE id_time = ? ORDER BY estrelas DESC, (velocidade+finalizacao+drible+passe+defesa) DESC
    """, (id_time,))
    jogadores = cursor.fetchall()
    conn.close()
    return jogadores


def obter_estilo_card(estrelas):
    """Estilos dinâmicos baseados no nível do jogador."""
    if estrelas <= 2:
        return {"border": ft.colors.BROWN_400, "bg": "#2A1810"}
    elif estrelas <= 4:
        return {"border": ft.colors.GREY_400, "bg": "#1E293B"}
    else:
        return {"border": ft.colors.AMBER_400, "bg": "#3B2607"}


def aplicar_auto_escalacao(id_time, formacao_escolhida):
    """Ajusta automaticamente os 11 titulares de acordo com as vagas da formação selecionada."""
    requisitos = ESQUEMAS_TATICOS.get(
        formacao_escolhida, ESQUEMAS_TATICOS["4-4-2"]).copy()
    jogadores = obter_jogadores(id_time)

    novos_titulares_ids = []

    # 1ª Passagem: Preenche as posições exatas com os melhores jogadores disponíveis
    for req_pos, qtd_necessaria in requisitos.items():
        compativeis = [j for j in jogadores if j[2] ==
                       req_pos and j[0] not in novos_titulares_ids]
        escolhidos = compativeis[:qtd_necessaria]
        novos_titulares_ids.extend([j[0] for j in escolhidos])

    # 2ª Passagem: Se faltar algum lugar no onze (ex: falta de LAT), preenche com os melhores restantes
    if len(novos_titulares_ids) < 11:
        restantes = [j for j in jogadores if j[0] not in novos_titulares_ids]
        faltam = 11 - len(novos_titulares_ids)
        novos_titulares_ids.extend([j[0] for j in restantes[:faltam]])

    # Atualiza a base de dados: define 1 para os escolhidos e 0 para os restantes
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jogadores SET titular = 0 WHERE id_time = ?", (id_time,))

    if novos_titulares_ids:
        format_ids = ','.join(['?'] * len(novos_titulares_ids))
        cursor.execute(
            f"UPDATE jogadores SET titular = 1 WHERE id IN ({format_ids})", novos_titulares_ids)

    conn.commit()
    conn.close()


def alternar_titularidade(id_jogador, titular_atual, id_time, id_usuario, page, ao_voltar_hub):
    """Permite ajustar manualmente a titularidade com limite máximo de 11."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    if titular_atual == 0:
        cursor.execute(
            "SELECT COUNT(*) FROM jogadores WHERE id_time = ? AND titular = 1", (id_time,))
        if cursor.fetchone()[0] >= 11:
            conn.close()
            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "⚠️ Limite de 11 titulares atingido! Remova um jogador primeiro."),
                bgcolor=ft.colors.RED_700, open=True
            )
            page.update()
            return

    cursor.execute("UPDATE jogadores SET titular = ? WHERE id = ?",
                   (0 if titular_atual == 1 else 1, id_jogador))
    conn.commit()
    conn.close()

    carregar_tatica(page, id_usuario, ao_voltar_hub)


def carregar_tatica(page: ft.Page, id_usuario: int, ao_voltar_hub):
    page.clean()
    page.title = "FootManager - Gestão Tática"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome FROM times WHERE id_usuario = ?", (id_usuario,))
    time = cursor.fetchone()
    conn.close()

    if not time:
        page.add(ft.Text("⚠️ Equipa não encontrada.", color=ft.colors.RED_400))
        return

    id_time, nome_time = time
    jogadores = obter_jogadores(id_time)

    titulares = [j for j in jogadores if j[3] == 1]
    suplentes = [j for j in jogadores if j[3] == 0]

    # --- CÁLCULO DA FORÇA DO TIME (MÉDIA DE ESTRELAS) ---
    if titulares:
        media_estrelas = sum(j[4] for j in titulares) / len(titulares)
        forca_texto = f"{media_estrelas:.1f}"
    else:
        forca_texto = "0.0"

    # --- CABEÇALHO COM FORÇA DA EQUIPA ---
    header = ft.Row([
        ft.Column([
            ft.Text("📋 PRANCHA TÁTICA", size=24,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(f"Clube: {nome_time} | Titulares: {len(titulares)}/11",
                    size=13, color=ft.colors.GREY_400),
        ]),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.STAR, color=ft.colors.AMBER_400, size=24),
                ft.Column([
                    ft.Text("FORÇA DO TIME", size=9,
                            weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400),
                    ft.Text(f"{forca_texto} ⭐", size=16,
                            weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400),
                ], spacing=0)
            ], spacing=8),
            bgcolor="#1E293B", padding=ft.padding.symmetric(horizontal=15, vertical=8), border_radius=10,
            border=ft.border.all(1, ft.colors.AMBER_400)
        ),
        ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.ARROW_BACK,
                          height=40, on_click=lambda e: ao_voltar_hub(id_usuario))
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=950)

    # --- EVENTO DE MUDANÇA DE FORMAÇÃO AUTOMÁTICA ---
    def ao_mudar_formacao(e):
        aplicar_auto_escalacao(id_time, e.control.value)
        carregar_tatica(page, id_usuario, ao_voltar_hub)

    seccao_esquema = ft.Container(
        content=ft.Row([
            ft.Text("Selecione o Esquema Tático:", size=15,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Dropdown(
                options=[ft.dropdown.Option(f)
                         for f in ESQUEMAS_TATICOS.keys()],
                value="4-4-2",
                width=180,
                bgcolor="#0F172A",
                color=ft.colors.WHITE,
                on_change=ao_mudar_formacao
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=950, bgcolor="#1E293B", padding=12, border_radius=12
    )

    # --- RENDERIZAÇÃO DOS CARDS ---
    def criar_linha_jogador(j):
        id_j, nome, pos, titular, estrelas, vel, fin, dri, pas, def_stat = j
        estilo = obter_estilo_card(estrelas)
        btn_txt = "Remover" if titular == 1 else "Promover"
        btn_cor = ft.colors.RED_400 if titular == 1 else ft.colors.GREEN_400

        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            pos, size=11, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        bgcolor="#0F172A", padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=5
                    ),
                    ft.Column([
                        ft.Text(nome, size=13, weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE),
                        ft.Text("⭐ " * estrelas, size=10),
                    ], spacing=2)
                ], spacing=10),
                ft.Row([
                    ft.Text(f"MED: {int((vel+fin+dri+pas+def_stat)/5)}",
                            size=11, color=ft.colors.GREY_300),
                    ft.OutlinedButton(
                        btn_txt,
                        style=ft.ButtonStyle(color=btn_cor),
                        on_click=lambda e: alternar_titularidade(
                            id_j, titular, id_time, id_usuario, page, ao_voltar_hub)
                    )
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=450, bgcolor=estilo["bg"], padding=10, border_radius=10,
            border=ft.border.all(1.5, estilo["border"])
        )

    coluna_titulares = ft.Column([
        ft.Text(f"🟢 TITULARES ({len(titulares)}/11)", size=16,
                weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
        ft.Column([criar_linha_jogador(j) for j in titulares], spacing=10)
    ], width=460)

    coluna_suplentes = ft.Column([
        ft.Text(f"⚪ SUPLENTES ({len(suplentes)})", size=16,
                weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400),
        ft.Column([criar_linha_jogador(j) for j in suplentes], spacing=10)
    ], width=460)

    page.add(
        header,
        ft.Container(height=10),
        seccao_esquema,
        ft.Container(height=15),
        ft.Row([coluna_titulares, coluna_suplentes], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
               vertical_alignment=ft.CrossAxisAlignment.START, width=950)
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        carregar_tatica(page, id_usuario=1,
                        ao_voltar_hub=lambda id_u: print("Voltar"))

    ft.app(target=main)
