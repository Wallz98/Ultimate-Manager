import flet as ft
import sqlite3
import random
import asyncio
import gerador
import simulador

# Mapeamento de cores para os escudos
CORES = {
    "Azul": ft.Colors.BLUE_700,
    "Vermelho": ft.Colors.RED_700,
    "Preto": ft.Colors.BLACK87,
    "Branco": ft.Colors.WHITE,
    "Amarelo": ft.Colors.AMBER_400,
    "Verde": ft.Colors.GREEN_700,
    "Laranja": ft.Colors.ORANGE_700,
    "Roxo": ft.Colors.PURPLE_700
}

PALETAS_VARIADAS = [
    (ft.Colors.PURPLE_800, ft.Colors.AMBER_400,
     ft.Colors.DEEP_PURPLE_900, ft.Colors.WHITE),
    (ft.Colors.GREEN_700, ft.Colors.WHITE,
     ft.Colors.LIGHT_GREEN_900, ft.Colors.YELLOW_400),
    (ft.Colors.RED_800, ft.Colors.BLACK, ft.Colors.RED_900, ft.Colors.AMBER_400),
    (ft.Colors.BLUE_800, ft.Colors.YELLOW_400, ft.Colors.BLUE_900, ft.Colors.WHITE),
    (ft.Colors.ORANGE_800, ft.Colors.BLACK,
     ft.Colors.DEEP_ORANGE_900, ft.Colors.WHITE),
    (ft.Colors.CYAN_700, ft.Colors.WHITE, ft.Colors.TEAL_900, ft.Colors.CYAN_200),
    (ft.Colors.PINK_700, ft.Colors.BLACK, ft.Colors.PINK_900, ft.Colors.WHITE),
    (ft.Colors.LIME_700, ft.Colors.BLUE_900, ft.Colors.GREEN_900, ft.Colors.WHITE),
    (ft.Colors.AMBER_700, ft.Colors.BLACK, ft.Colors.AMBER_900, ft.Colors.WHITE),
    (ft.Colors.INDIGO_800, ft.Colors.RED_500,
     ft.Colors.INDIGO_900, ft.Colors.WHITE)
]

ICONES_BOT = [
    ft.Icons.SHIELD,
    ft.Icons.FLASH_ON,
    ft.Icons.LOCAL_FIRE_DEPARTMENT,
    ft.Icons.SPORTS_SOCCER,
    ft.Icons.MILITARY_TECH,
    ft.Icons.WORKSPACE_PREMIUM,
    ft.Icons.FORT
]


def construir_escudo(cor1=None, cor2=None, cor3=None, cor4=None, formato="Clássico", tamanho=1.0, is_bot=False, seed_id=1):
    rnd = random.Random(seed_id)

    if is_bot or cor1 is None:
        c1, c2, c3, c4 = rnd.choice(PALETAS_VARIADAS)
    else:
        c1 = CORES.get(cor1, ft.Colors.BLUE_700) if isinstance(
            cor1, str) else cor1
        c2 = CORES.get(cor2, ft.Colors.RED_700) if isinstance(
            cor2, str) else cor2
        c3 = CORES.get(cor3, ft.Colors.AMBER_400) if isinstance(
            cor3, str) else cor3
        c4 = CORES.get(cor4, ft.Colors.WHITE) if isinstance(
            cor4, str) else cor4

    # Ajusta o formato/borda conforme a opção do time
    fmt = str(formato or "Clássico").lower()
    if "redond" in fmt or "círculo" in fmt or "circulo" in fmt:
        raio_borda = ft.border_radius.all(int(45 * tamanho))
    elif "losang" in fmt or "diamante" in fmt:
        raio_borda = ft.border_radius.only(
            top_left=int(40 * tamanho),
            bottom_right=int(40 * tamanho),
            top_right=int(6 * tamanho),
            bottom_left=int(6 * tamanho)
        )
    elif "quadrad" in fmt:
        raio_borda = ft.border_radius.all(int(10 * tamanho))
    else:  # "Clássico" / Padrão
        raio_borda = ft.border_radius.only(
            bottom_left=int(45 * tamanho), bottom_right=int(45 * tamanho),
            top_left=int(6 * tamanho), top_right=int(6 * tamanho)
        )

    icone_centro = ft.Icon(name=ft.Icons.STAR_ROUNDED,
                           size=35 * tamanho, color=c4)

    if is_bot:
        icone_escolhido = rnd.choice(ICONES_BOT)
        estilo_borda = rnd.randint(1, 3)
        icone_centro = ft.Icon(name=icone_escolhido,
                               size=35 * tamanho, color=c4)

        if estilo_borda == 1:
            raio_borda = ft.border_radius.all(int(20 * tamanho))
        elif estilo_borda == 2:
            raio_borda = ft.border_radius.only(
                bottom_left=int(20 * tamanho), bottom_right=int(20 * tamanho),
                top_left=int(40 * tamanho), top_right=int(40 * tamanho)
            )

    listra1 = ft.Container(
        width=12 * tamanho, height=100 * tamanho, bgcolor=c2)
    listra2 = ft.Container(
        width=12 * tamanho, height=100 * tamanho, bgcolor=c2)
    listra3 = ft.Container(
        width=12 * tamanho, height=100 * tamanho, bgcolor=c2)

    painel_listras = ft.Row([listra1, listra2, listra3],
                            spacing=6 * tamanho, alignment=ft.MainAxisAlignment.CENTER)

    miolo = ft.Container(
        content=ft.Stack([
            painel_listras,
            ft.Container(content=icone_centro, alignment=ft.alignment.center)
        ]),
        width=80 * tamanho,
        height=90 * tamanho,
        bgcolor=c1,
        border_radius=raio_borda,
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    return ft.Container(
        content=miolo,
        width=90 * tamanho,
        height=100 * tamanho,
        bgcolor=c3,
        padding=5 * tamanho,
        border_radius=raio_borda,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK38)
    )


def buscar_titulares_detalhados(id_time):
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, posicao, estrelas, velocidade, finalizacao, drible, passe, defesa 
        FROM jogadores 
        WHERE id_time = ? AND titular = 1 
        LIMIT 11
    """, (id_time,))
    jogadores = cursor.fetchall()
    conn.close()
    return jogadores


def criar_card_jogador_mini(nome, pos, estrelas):
    return ft.Container(
        content=ft.Column([
            ft.Text(pos, size=9, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.AMBER_400),
            ft.Text(nome.split()[0], size=10, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Text("★" * estrelas, size=8, color=ft.Colors.YELLOW_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
        width=75, height=50, padding=3,
        bgcolor="#334155", border_radius=6,
        border=ft.border.all(1, ft.Colors.BLUE_400)
    )


def criar_painel_elenco_horizontal(id_time):
    titulares = buscar_titulares_detalhados(id_time)
    grid = ft.Row(wrap=True, spacing=4, run_spacing=4, width=340)
    for t in titulares:
        grid.controls.append(criar_card_jogador_mini(t[0], t[1], t[2]))
    return grid


def obter_nomes_plantel(id_time):
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, posicao FROM jogadores WHERE id_time = ? AND titular = 1", (id_time,))
    jogadores = cursor.fetchall()
    conn.close()

    if not jogadores:
        return {"ATA": ["Atacante"], "MEI": ["Meio-Campista"], "DEF": ["Defensor"], "GOL": ["Goleiro"]}

    plantel = {"ATA": [], "MEI": [], "DEF": [], "GOL": []}
    for nome, pos in jogadores:
        if pos in ["ATA", "PE", "PD"]:
            plantel["ATA"].append(nome)
        elif pos in ["MEI", "MC", "VOL", "ME", "MD"]:
            plantel["MEI"].append(nome)
        elif pos in ["GOL"]:
            plantel["GOL"].append(nome)
        else:
            plantel["DEF"].append(nome)

    for k in plantel:
        if not plantel[k]:
            plantel[k] = [f"Jogador ({k})"]

    return plantel


def preparar_dados_partida(id_usuario, id_adversario=None):
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nome, COALESCE(formato, 'Clássico'), cor_1, cor_2, cor_3, cor_4 FROM times WHERE id_usuario = ?", (id_usuario,))
    user_time = cursor.fetchone()

    if user_time:
        cursor.execute(
            "SELECT COUNT(*) FROM jogadores WHERE id_time = ? AND titular = 1", (user_time[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "UPDATE jogadores SET titular = 1 WHERE id IN (SELECT id FROM jogadores WHERE id_time = ? LIMIT 11)", (user_time[0],))
            conn.commit()

    if id_adversario:
        cursor.execute(
            "SELECT id, nome, COALESCE(formato, 'Clássico'), cor_1, cor_2, cor_3, cor_4 FROM times WHERE id = ?", (id_adversario,))
        bot_time = cursor.fetchone()
    else:
        cursor.execute(
            "SELECT id, nome, COALESCE(formato, 'Clássico'), cor_1, cor_2, cor_3, cor_4 FROM times WHERE is_bot = 1 ORDER BY RANDOM() LIMIT 1")
        bot_time = cursor.fetchone()

    if not bot_time:
        conn.close()
        id_bot = gerador.gerar_time_torneio("FC Metropolitano", 2)
        conn = sqlite3.connect('meu_manager.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, COALESCE(formato, 'Clássico'), cor_1, cor_2, cor_3, cor_4 FROM times WHERE id = ?", (id_bot,))
        bot_time = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) FROM jogadores WHERE id_time = ? AND titular = 1", (bot_time[0],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "UPDATE jogadores SET titular = 1 WHERE id IN (SELECT id FROM jogadores WHERE id_time = ? LIMIT 11)", (bot_time[0],))
        conn.commit()

    conn.close()
    return user_time, bot_time


def carregar_partida(page: ft.Page, id_usuario: int, id_adversario: int, ao_finalizar_partida):
    page.clean()
    page.title = "FootManager - Em Campo"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    user_time, bot_time = preparar_dados_partida(id_usuario, id_adversario)

    id_time_user, nome_user, fmt_user, c1, c2, c3, c4 = user_time
    id_time_bot, nome_bot, fmt_bot, _, _, _, _ = bot_time

    plantel_user = obter_nomes_plantel(id_time_user)
    plantel_bot = obter_nomes_plantel(id_time_bot)

    escudo_user = construir_escudo(
        c1, c2, c3, c4, formato=fmt_user, tamanho=0.9, is_bot=False)
    escudo_bot = construir_escudo(
        formato=fmt_bot, tamanho=0.9, is_bot=True, seed_id=id_time_bot)

    gols_user = ft.Text(
        "0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    gols_bot = ft.Text(
        "0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    tempo_jogo = ft.Text(
        "00'", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
    status_partida = ft.Text(
        "Pronto para o Apito Inicial!", size=13, color=ft.Colors.GREY_400)

    painel_user = ft.Column([
        escudo_user,
        ft.Text(nome_user, size=15, weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=160)

    painel_bot = ft.Column([
        escudo_bot,
        ft.Text(nome_bot, size=15, weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=160)

    placar_central = ft.Column([
        tempo_jogo,
        ft.Row([gols_user, ft.Text("-", size=36, color=ft.Colors.GREY_500), gols_bot],
               alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        status_partida
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)

    arena_placar = ft.Container(
        content=ft.Row([painel_user, placar_central, painel_bot],
                       alignment=ft.MainAxisAlignment.SPACE_AROUND),
        width=750, padding=15, bgcolor="#1E293B", border_radius=18
    )

    cards_elenco_user = criar_painel_elenco_horizontal(id_time_user)
    cards_elenco_bot = criar_painel_elenco_horizontal(id_time_bot)

    secao_elencos = ft.Container(
        content=ft.Row([
            ft.Column([ft.Text("Titulares " + nome_user, size=12, color=ft.Colors.AMBER_400,
                      weight=ft.FontWeight.BOLD), cards_elenco_user], width=350),
            ft.VerticalDivider(width=1, color="#334155"),
            ft.Column([ft.Text("Titulares " + nome_bot, size=12, color=ft.Colors.AMBER_400,
                      weight=ft.FontWeight.BOLD), cards_elenco_bot], width=350),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=750, padding=12, bgcolor="#0F172A", border_radius=12, border=ft.border.all(1, "#334155")
    )

    remates_user = ft.Text("0", color=ft.Colors.WHITE,
                           weight=ft.FontWeight.BOLD)
    remates_bot = ft.Text("0", color=ft.Colors.WHITE,
                          weight=ft.FontWeight.BOLD)
    posse_user = ft.Text("50%", color=ft.Colors.CYAN_300,
                         weight=ft.FontWeight.BOLD)
    posse_bot = ft.Text("50%", color=ft.Colors.RED_300,
                        weight=ft.FontWeight.BOLD)

    painel_estatisticas = ft.Container(
        content=ft.Row([
            ft.Row(
                [ft.Text("Remates: ", color=ft.Colors.GREY_400, size=12), remates_user]),
            ft.Row([ft.Text("Posse: ", color=ft.Colors.GREY_400, size=12),
                   posse_user, ft.Text(" | ", color=ft.Colors.GREY_600), posse_bot]),
            ft.Row(
                [ft.Text("Remates: ", color=ft.Colors.GREY_400, size=12), remates_bot]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=750, padding=ft.padding.symmetric(horizontal=20, vertical=8), bgcolor="#0F172A", border_radius=10
    )

    feed_lances = ft.ListView(expand=True, spacing=8,
                              padding=12, auto_scroll=True)
    caixa_narracao = ft.Container(
        content=feed_lances, width=750, height=160, bgcolor="#020617", border_radius=15, border=ft.border.all(1, "#334155")
    )

    btn_iniciar = ft.ElevatedButton(
        "Apito Inicial", icon=ft.Icons.PLAY_ARROW, height=45)

    # Estado final do jogo mantido em referências mutáveis
    id_vencedor_final = [None]
    gols_user_final = [0]
    gols_bot_final = [0]

    def callback_continuar(e):
        try:
            ao_finalizar_partida(
                id_vencedor_final[0], gols_user_final[0], gols_bot_final[0])
        except TypeError:
            ao_finalizar_partida(id_vencedor_final[0])

    btn_continuar = ft.OutlinedButton(
        "Continuar", icon=ft.Icons.ARROW_FORWARD, visible=False, on_click=callback_continuar
    )

    async def simular_jogo_visual():
        btn_iniciar.disabled = True
        page.update()

        casa = simulador.carregar_forca_do_time(id_time_user)
        fora = simulador.carregar_forca_do_time(id_time_bot)

        posse_alvo_casa, _ = simulador.calcular_posse_base(
            casa['meio'], fora['meio'])

        stat_remates_casa = 0
        stat_remates_fora = 0

        feed_lances.controls.append(ft.Text(
            "🏁 O árbitro apita! Começa a partida!", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD))
        page.update()

        for lance in range(1, 11):
            await asyncio.sleep(0.5)
            minuto = lance * 9
            tempo_jogo.value = f"{minuto}'"

            flutuacao = random.randint(-3, 3)
            posse_atual_casa = max(25, min(75, posse_alvo_casa + flutuacao))
            posse_user.value = f"{posse_atual_casa}%"
            posse_bot.value = f"{100 - posse_atual_casa}%"

            poder_meio_total = max(1, casa['meio'] + fora['meio'])
            is_casa = random.randint(1, poder_meio_total) <= casa['meio']

            atacante = casa if is_casa else fora
            defensor = fora if is_casa else casa
            plantel_atq = plantel_user if is_casa else plantel_bot
            plantel_def = plantel_bot if is_casa else plantel_user

            forca_chute = atacante['ataque'] + random.randint(0, 100)
            forca_bloqueio = (defensor['defesa'] *
                              1.3) + random.randint(0, 100)

            nome_atq = random.choice(plantel_atq['ATA'])
            nome_mei = random.choice(plantel_atq['MEI'])
            nome_def = random.choice(plantel_def['DEF'])
            nome_gol = random.choice(plantel_def['GOL'])

            if forca_chute > forca_bloqueio:
                if is_casa:
                    stat_remates_casa += 1
                else:
                    stat_remates_fora += 1

                sorteio_desfecho = random.random()

                if sorteio_desfecho > 0.55:
                    atacante['gols'] += 1
                    cor_msg = ft.Colors.CYAN_300 if is_casa else ft.Colors.RED_400
                    feed_lances.controls.append(
                        ft.Text(f"⚽ [{minuto}'] GOOOOOOL DO {atacante['nome'].upper()}! {nome_mei} serve {nome_atq} que remata sem hipóteses!",
                                color=cor_msg, weight=ft.FontWeight.BOLD)
                    )
                elif sorteio_desfecho > 0.25:
                    feed_lances.controls.append(
                        ft.Text(f"💥 [{minuto}'] DEFENSAÇO! {nome_atq} remata forte mas {nome_gol} faz uma parada incrível!",
                                color=ft.Colors.AMBER_300)
                    )
                else:
                    feed_lances.controls.append(
                        ft.Text(f"📐 [{minuto}'] PRA FORA! {nome_atq} ganha espaço na área, mas remata por cima da baliza.",
                                color=ft.Colors.GREY_300)
                    )
            else:
                feed_lances.controls.append(
                    ft.Text(f"🛡 [{minuto}'] {nome_mei} tenta infiltrar na área, mas o defesa {nome_def} faz um bom corte.",
                            color=ft.Colors.GREY_400)
                )

            gols_user.value = str(casa['gols'])
            gols_bot.value = str(fora['gols'])
            remates_user.value = str(stat_remates_casa)
            remates_bot.value = str(stat_remates_fora)
            page.update()

        # Decisão por Penáltis em caso de empate
        if casa['gols'] == fora['gols']:
            feed_lances.controls.append(
                ft.Text("⚖ Partida empatada! Decisão nos PENÁLTIS...",
                        color=ft.Colors.AMBER_400, weight=ft.FontWeight.BOLD)
            )
            if random.choice([True, False]):
                casa['gols'] += 1
                feed_lances.controls.append(ft.Text(
                    f"⚽ {nome_user} venceu a disputa por penáltis!", color=ft.Colors.GREEN_400))
            else:
                fora['gols'] += 1
                feed_lances.controls.append(ft.Text(
                    f"⚽ {nome_bot} venceu a disputa por penáltis!", color=ft.Colors.RED_400))

            gols_user.value = str(casa['gols'])
            gols_bot.value = str(fora['gols'])

        tempo_jogo.value = "90'"
        status_partida.value = "FIM DE JOGO!"

        gols_user_final[0] = casa['gols']
        gols_bot_final[0] = fora['gols']

        if casa['gols'] > fora['gols']:
            id_vencedor_final[0] = id_usuario
        else:
            id_vencedor_final[0] = id_time_bot

        simulador.processar_recompensas(
            id_usuario, id_time_user, casa['gols'], fora['gols'])

        btn_iniciar.visible = False
        btn_continuar.visible = True
        page.update()

    btn_iniciar.on_click = lambda _: page.run_task(simular_jogo_visual)

    page.add(
        arena_placar,
        ft.Container(height=5),
        secao_elencos,
        ft.Container(height=5),
        painel_estatisticas,
        ft.Container(height=5),
        caixa_narracao,
        ft.Container(height=10),
        ft.Row([btn_iniciar, btn_continuar],
               alignment=ft.MainAxisAlignment.CENTER)
    )
