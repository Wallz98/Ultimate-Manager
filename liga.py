import flet as ft
import sqlite3
import random
import gerador
import partida


def obter_escudo(id_time, tamanho=28):
    """
    Busca as configurações do escudo (incluindo o símbolo) e a imagem no banco de dados,
    gerando o escudo em tamanho compacto (~28px) ideal para linhas de tabela.
    """
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT formato, simbolo, cor_1, cor_2, cor_3, cor_4, escudo 
            FROM times WHERE id = ?
        """, (id_time,))
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        cursor.execute("""
            SELECT formato, simbolo, cor_1, cor_2, cor_3, cor_4, NULL as escudo 
            FROM times WHERE id = ?
        """, (id_time,))
        row = cursor.fetchone()

    conn.close()

    # Ajusta o fator de escala para que o escudo fique compacto na tabela (~28px)
    escala = tamanho / 100.0

    if row:
        fmt, sim, c1, c2, c3, c4, esc_path = row
        return partida.obter_widget_escudo(
            escudo_path=esc_path,
            c1=c1,
            c2=c2,
            c3=c3,
            c4=c4,
            formato=fmt or "Clássico",
            simbolo=sim or "Bola",
            tamanho=escala,
            seed_id=id_time
        )

    return partida.obter_widget_escudo(
        escudo_path=None,
        c1=None, c2=None, c3=None, c4=None,
        formato="Clássico",
        simbolo="Bola",
        tamanho=escala,
        seed_id=id_time
    )

def premiar_subida_divisao(id_usuario, valor_premio=1500):
    """Premia o utilizador no banco de dados por subir de divisão."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE times SET moedas_free = moedas_free + ? WHERE id_usuario = ?",
        (valor_premio, id_usuario)
    )
    conn.commit()
    conn.close()


def criar_liga_10_times(id_usuario, divisao=2):
    """Gera 10 equipas para a Liga (1 utilizador + 9 bots)."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nome FROM times WHERE id_usuario = ?", (id_usuario,))
    time_user = cursor.fetchone()

    user_id = time_user[0] if time_user else id_usuario
    user_nome = time_user[1] if time_user else "Meu Time"

    nomes_disponiveis = [t for t in gerador.NOMES_TIMES if t != user_nome]
    random.shuffle(nomes_disponiveis)

    times_liga = [{
        "id": user_id,
        "nome": user_nome,
        "is_user": True,
        "pts": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0, "sg": 0
    }]

    estrelas_min, estrelas_max = (1, 2) if divisao == 2 else (3, 4)

    for i in range(9):
        nome_bot = nomes_disponiveis.pop(
        ) if nomes_disponiveis else f"Clube Div{divisao} {i+1}"
        id_bot = gerador.gerar_time_torneio(
            nome_bot, random.randint(estrelas_min, estrelas_max))
        times_liga.append({
            "id": id_bot,
            "nome": nome_bot,
            "is_user": False,
            "pts": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0, "sg": 0
        })

    conn.close()
    return times_liga


def carregar_liga(page: ft.Page, id_usuario: int, ao_voltar_hub):
    page.clean()
    page.title = "FootManager - Campeonato"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    if not hasattr(page, "liga_dados") or page.liga_dados is None:
        page.liga_dados = {
            "rodada_atual": 1,
            "max_rodadas": 10,
            "divisao": 2,
            "premiado": False,
            "times": criar_liga_10_times(id_usuario, divisao=2)
        }

    dados = page.liga_dados
    rodada = dados["rodada_atual"]
    max_rodadas = dados["max_rodadas"]
    times = dados["times"]

    times_ordenados = sorted(
        times, key=lambda x: (x["pts"], x["sg"], x["v"], x["gp"]), reverse=True
    )

    posicao_jogador = next(
        i + 1 for i, t in enumerate(times_ordenados) if t["is_user"])

    def reiniciar_liga_temporada(nova_divisao):
        """Reinicia os dados do campeonato para uma nova época."""
        page.liga_dados = {
            "rodada_atual": 1,
            "max_rodadas": 10,
            "divisao": nova_divisao,
            "premiado": False,
            "times": criar_liga_10_times(id_usuario, divisao=nova_divisao)
        }
        carregar_liga(page, id_usuario, ao_voltar_hub)

    def processar_resultado_partida_liga(gols_user, gols_bot, id_bot):
        user_team = next(t for t in times if t["is_user"])
        bot_team = next(t for t in times if t["id"] == id_bot)

        user_team["j"] += 1
        bot_team["j"] += 1
        user_team["gp"] += gols_user
        user_team["gc"] += gols_bot
        bot_team["gp"] += gols_bot
        bot_team["gc"] += gols_user

        if gols_user > gols_bot:
            user_team["v"] += 1
            user_team["pts"] += 3
            bot_team["d"] += 1
        elif gols_user < gols_bot:
            bot_team["v"] += 1
            bot_team["pts"] += 3
            user_team["d"] += 1
        else:
            user_team["e"] += 1
            bot_team["e"] += 1
            user_team["pts"] += 1
            bot_team["pts"] += 1

        user_team["sg"] = user_team["gp"] - user_team["gc"]
        bot_team["sg"] = bot_team["gp"] - bot_team["gc"]

        outros_bots = [t for t in times if not t["is_user"]
                       and t["id"] != id_bot]
        random.shuffle(outros_bots)

        for i in range(0, len(outros_bots) - 1, 2):
            b1, b2 = outros_bots[i], outros_bots[i+1]
            g1, g2 = random.randint(0, 3), random.randint(0, 3)

            b1["j"] += 1
            b2["j"] += 1
            b1["gp"] += g1
            b1["gc"] += g2
            b2["gp"] += g2
            b2["gc"] += g1

            if g1 > g2:
                b1["v"] += 1
                b1["pts"] += 3
                b2["d"] += 1
            elif g2 > g1:
                b2["v"] += 1
                b2["pts"] += 3
                b1["d"] += 1
            else:
                b1["e"] += 1
                b2["e"] += 1
                b1["pts"] += 1
                b2["pts"] += 1

            b1["sg"] = b1["gp"] - b1["gc"]
            b2["sg"] = b2["gp"] - b2["gc"]

        dados["rodada_atual"] += 1
        carregar_liga(page, id_usuario, ao_voltar_hub)

    def jogar_rodada_atual():
        bots_disponiveis = [t for t in times if not t["is_user"]]
        adversario = random.choice(bots_disponiveis)

        partida.carregar_partida(
            page,
            id_usuario,
            adversario["id"],
            lambda id_venc, g_u, g_b: processar_resultado_partida_liga(
                g_u, g_b, adversario["id"])
        )

    rows = []
    for idx, t in enumerate(times_ordenados):
        pos = idx + 1

        # Destaque de cor suave e contrastante para linhas
        if t["is_user"]:
            cor_fundo = "#1E40AF"  # Azul destacado para o utilizador
        elif pos <= 2:
            cor_fundo = "#064E3B"  # Verde escuro para zona de subida
        else:
            cor_fundo = "#0F172A" if idx % 2 == 0 else "#1E293B"  # Zebra sutil

        escudo_widget = obter_escudo(t["id"], tamanho=28)

        celula_equipa = ft.DataCell(
            ft.Row([
                escudo_widget,
                ft.Text(
                    t["nome"],
                    weight=ft.FontWeight.BOLD if t["is_user"] else ft.FontWeight.NORMAL,
                    color=ft.Colors.AMBER_400 if t["is_user"] else ft.Colors.WHITE,
                    size=13
                )
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

        rows.append(
            ft.DataRow(
                color=cor_fundo,
                cells=[
                    ft.DataCell(ft.Text(f"{pos}º", weight=ft.FontWeight.BOLD if pos <=
                                2 else ft.FontWeight.NORMAL, color=ft.Colors.WHITE)),
                    celula_equipa,
                    ft.DataCell(
                        ft.Text(str(t["pts"]), weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300)),
                    ft.DataCell(
                        ft.Text(str(t["j"]), color=ft.Colors.GREY_300)),
                    ft.DataCell(
                        ft.Text(str(t["v"]), color=ft.Colors.GREY_300)),
                    ft.DataCell(
                        ft.Text(str(t["e"]), color=ft.Colors.GREY_300)),
                    ft.DataCell(
                        ft.Text(str(t["d"]), color=ft.Colors.GREY_300)),
                    ft.DataCell(
                        ft.Text(str(t["sg"]), color=ft.Colors.GREY_300)),
                ]
            )
        )

    estilo_cabecalho = ft.TextStyle(
        weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300, size=12)

    tabela = ft.DataTable(
        heading_row_color="#0F172A",
        columns=[
            ft.DataColumn(ft.Text("Pos", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("Equipa", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("Pts", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("J", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("V", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("E", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("D", style=estilo_cabecalho)),
            ft.DataColumn(ft.Text("SG", style=estilo_cabecalho)),
        ],
        rows=rows,
        data_row_max_height=42,  # Mantém as linhas da tabela com altura elegante
    )

    # Cartão de fundo para dar destaque e excelente contraste à tabela
    cartao_tabela = ft.Container(
        content=tabela,
        bgcolor="#1E293B",
        border_radius=14,
        padding=10,
        border=ft.border.all(1, "#334155"),
        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK54)
    )

    titulo_texto = f"📊 LIGA DIVISÃO {dados['divisao']} - RODADA {min(rodada, max_rodadas)}/{max_rodadas}"
    header_title = ft.Text(titulo_texto, size=22,
                           weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)

    if rodada <= max_rodadas:
        painel_acao = ft.Column([
            ft.Text("🟢 ZONA DE SUBIDA: 1º e 2º Lugares",
                    size=12, color=ft.Colors.GREEN_400),
            ft.Container(height=5),
            ft.ElevatedButton(
                f"JOGAR RODADA {rodada}",
                icon=ft.Icons.PLAY_ARROW,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                height=45,
                on_click=lambda e: jogar_rodada_atual()
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    else:
        subiu = posicao_jogador <= 2

        if subiu:
            if not dados.get("premiado"):
                premiar_subida_divisao(id_usuario, valor_premio=2000)
                dados["premiado"] = True

            msg_resultado = ft.Text(
                f"🎉 PARABÉNS! Ficaste em {posicao_jogador}º Lugar e SUBISTE À 1ª DIVISÃO!\nBónus: +2000 Moedas!",
                size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER
            )
            proxima_divisao = 1
        else:
            msg_resultado = ft.Text(
                f"⚠️ Terminaste em {posicao_jogador}º Lugar.\nNão alcançaste os 2 primeiros lugares e permaneces na 2ª Divisão.",
                size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400, text_align=ft.TextAlign.CENTER
            )
            proxima_divisao = 2

        painel_acao = ft.Column([
            msg_resultado,
            ft.Container(height=10),
            ft.ElevatedButton(
                "🔄 REINICIAR LIGA (NOVA TEMPORADA)",
                icon=ft.Icons.REFRESH,
                bgcolor=ft.Colors.CYAN_600,
                color=ft.Colors.WHITE,
                height=45,
                on_click=lambda e: reiniciar_liga_temporada(
                    nova_divisao=proxima_divisao)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    btn_voltar = ft.OutlinedButton(
        "Voltar ao Hub",
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda e: ao_voltar_hub(id_usuario)
    )

    page.add(
        header_title,
        ft.Container(height=10),
        cartao_tabela,
        ft.Container(height=15),
        painel_acao,
        ft.Container(height=10),
        btn_voltar
    )
