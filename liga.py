import flet as ft
import sqlite3
import random
import gerador
import partida


def obter_escudo(id_time, tamanho=30):
    """Busca as configurações do escudo no banco de dados e gera o escudo escalado."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT formato, simbolo, cor_1, cor_2, cor_3, cor_4 
        FROM times WHERE id = ?
    """, (id_time,))
    row = cursor.fetchone()
    conn.close()

    if row:
        fmt, sim, c1, c2, c3, c4 = row
        # Se sim for None ou vazio, sorteia um da lista de ícones disponíveis
        simbolo_final = sim if sim else random.choice(
            list(gerador.ICONES.keys()))
        return gerador.criar_escudo_time(
            formato=fmt or "Losango",
            simbolo=simbolo_final,
            cor_principal=c1 or "Azul",
            cor_secundaria=c2 or "Vermelho",
            cor_borda=c3 or "Amarelo",
            cor_texto=c4 or "Branco",
            tamanho=tamanho
        )
    return gerador.criar_escudo_time(tamanho=tamanho)


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
        cor_fundo = "#1E3A8A" if t["is_user"] else (
            "#065F46" if pos <= 2 else None)

        escudo_widget = obter_escudo(t["id"], tamanho=28)

        celula_equipa = ft.DataCell(
            ft.Row([
                escudo_widget,
                ft.Text(
                    t["nome"],
                    weight=ft.FontWeight.BOLD if t["is_user"] else ft.FontWeight.NORMAL,
                    color=ft.colors.AMBER_400 if t["is_user"] else ft.colors.WHITE
                )
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

        rows.append(
            ft.DataRow(
                color=cor_fundo,
                cells=[
                    ft.DataCell(ft.Text(
                        f"{pos}º", weight=ft.FontWeight.BOLD if pos <= 2 else ft.FontWeight.NORMAL)),
                    celula_equipa,
                    ft.DataCell(
                        ft.Text(str(t["pts"]), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(str(t["j"]))),
                    ft.DataCell(ft.Text(str(t["v"]))),
                    ft.DataCell(ft.Text(str(t["e"]))),
                    ft.DataCell(ft.Text(str(t["d"]))),
                    ft.DataCell(ft.Text(str(t["sg"]))),
                ]
            )
        )

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Pos")),
            ft.DataColumn(ft.Text("Equipa")),
            ft.DataColumn(ft.Text("Pts")),
            ft.DataColumn(ft.Text("J")),
            ft.DataColumn(ft.Text("V")),
            ft.DataColumn(ft.Text("E")),
            ft.DataColumn(ft.Text("D")),
            ft.DataColumn(ft.Text("SG")),
        ],
        rows=rows
    )

    titulo_texto = f"📊 LIGA DIVISÃO {dados['divisao']} - RODADA {min(rodada, max_rodadas)}/{max_rodadas}"
    header_title = ft.Text(titulo_texto, size=22,
                           weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400)

    if rodada <= max_rodadas:
        painel_acao = ft.Column([
            ft.Text("🟢 ZONA DE SUBIDA: 1º e 2º Lugares",
                    size=12, color=ft.colors.GREEN_400),
            ft.Container(height=5),
            ft.ElevatedButton(
                f"JOGAR RODADA {rodada}",
                icon=ft.icons.PLAY_ARROW,
                bgcolor=ft.colors.GREEN_600,
                color=ft.colors.WHITE,
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
                size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400, text_align=ft.TextAlign.CENTER
            )
            proxima_divisao = 1
        else:
            msg_resultado = ft.Text(
                f"⚠️ Terminaste em {posicao_jogador}º Lugar.\nNão alcançaste os 2 primeiros lugares e permaneces na 2ª Divisão.",
                size=16, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400, text_align=ft.TextAlign.CENTER
            )
            proxima_divisao = 2

        painel_acao = ft.Column([
            msg_resultado,
            ft.Container(height=10),
            ft.ElevatedButton(
                "🔄 REINICIAR LIGA (NOVA TEMPORADA)",
                icon=ft.icons.REFRESH,
                bgcolor=ft.colors.CYAN_600,
                color=ft.colors.WHITE,
                height=45,
                on_click=lambda e: reiniciar_liga_temporada(
                    nova_divisao=proxima_divisao)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    btn_voltar = ft.OutlinedButton(
        "Voltar ao Hub",
        icon=ft.icons.ARROW_BACK,
        on_click=lambda e: ao_voltar_hub(id_usuario)
    )

    page.add(
        header_title,
        ft.Container(height=10),
        tabela,
        ft.Container(height=15),
        painel_acao,
        ft.Container(height=10),
        btn_voltar
    )
