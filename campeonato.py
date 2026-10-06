import flet as ft
import sqlite3
import random
import gerador
import partida


def criar_torneio_8_times(id_usuario):
    """Prepara a lista de 8 times para o mata-mata (1 do usuário + 7 bots)."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nome FROM times WHERE id_usuario = ?", (id_usuario,))
    time_user = cursor.fetchone()

    # Pega nomes de clubes reais
    nomes_disponiveis = [t for t in gerador.NOMES_TIMES if t != time_user[1]]
    random.shuffle(nomes_disponiveis)

    times_torneio = [{"id": time_user[0],
                      "nome": time_user[1], "is_user": True}]

    for i in range(7):
        nome_bot = nomes_disponiveis.pop(
        ) if nomes_disponiveis else f"Clube Bot {i+1}"
        estrelas_bot = random.randint(1, 5)
        id_bot = gerador.gerar_time_torneio(nome_bot, estrelas_bot)
        times_torneio.append(
            {"id": id_bot, "nome": nome_bot, "is_user": False})

    random.shuffle(times_torneio)
    conn.close()
    return times_torneio


def carregar_campeonato(page: ft.Page, id_usuario: int, ao_voltar_hub):
    page.clean()
    page.title = "FootManager - Copa Mata-Mata"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    if not hasattr(page, "torneio_participantes") or page.torneio_participantes is None:
        page.torneio_participantes = criar_torneio_8_times(id_usuario)

    participantes = page.torneio_participantes

    fases_nomes = {8: "QUARTAS DE FINAL", 4: "SEMIFINAL", 2: "GRANDE FINAL"}
    nome_fase_atual = fases_nomes.get(len(participantes), "FASE MATA-MATA")

    confrontos = []
    for i in range(0, len(participantes), 2):
        confrontos.append((participantes[i], participantes[i+1]))

    lista_jogos = ft.Column(
        spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def processar_resultado_partida(id_vencedor, t1, t2):
        # Se o usuário perdeu, é eliminado
        if id_vencedor != id_usuario:
            page.torneio_participantes = None
            exibir_eliminacao(t1 if t1["id"] != id_usuario else t2)
            return

        novos_participantes = []
        for a, b in confrontos:
            if a["is_user"] or b["is_user"]:
                novos_participantes.append(
                    t1 if t1["id"] == id_usuario else t2)
            else:
                novos_participantes.append(random.choice([a, b]))

        page.torneio_participantes = novos_participantes

        if len(novos_participantes) == 1:
            campeao = novos_participantes[0]
            page.torneio_participantes = None
            exibir_campeao(campeao)
        else:
            carregar_campeonato(page, id_usuario, ao_voltar_hub)

    def jogar_partida_usuario(t1, t2):
        id_adversario = t2["id"] if t1["is_user"] else t1["id"]

        partida.carregar_partida(
            page,
            id_usuario,
            id_adversario,
            lambda id_vencedor: processar_resultado_partida(
                id_vencedor, t1, t2)
        )

    def renderizar_chaves():
        lista_jogos.controls.clear()
        lista_jogos.controls.append(
            ft.Text(f"🏆 COPA MATA-MATA ({nome_fase_atual})", size=20,
                    weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400)
        )

        for idx, (t1, t2) in enumerate(confrontos, 1):
            eh_jogo_usuario = t1["is_user"] or t2["is_user"]
            destaque = ft.colors.BLUE_800 if eh_jogo_usuario else "#1E293B"

            if eh_jogo_usuario:
                botao_acao = ft.ElevatedButton(
                    "JOGAR PARTIDA",
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                    on_click=lambda e, a=t1, b=t2: jogar_partida_usuario(a, b)
                )
            else:
                botao_acao = ft.Text("Simulação Auto 🤖",
                                     size=12, color=ft.colors.GREY_400)

            card_jogo = ft.Container(
                content=ft.Row([
                    ft.Text(f"Jogo {idx}", size=12, color=ft.colors.GREY_400),
                    ft.Text(
                        f"{t1['nome']}", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text("VS", size=12, color=ft.colors.AMBER_400,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"{t2['nome']}", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    botao_acao
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                width=700, padding=15, bgcolor=destaque, border_radius=10
            )
            lista_jogos.controls.append(card_jogo)

        page.update()

    def exibir_eliminacao(adversario_vencedor):
        page.clean()
        page.add(
            ft.Column([
                ft.Text("❌ ELIMINADO DA COPA!", size=28,
                        weight=ft.FontWeight.BOLD, color=ft.colors.RED_500),
                ft.Text(
                    f"Foste derrotado por {adversario_vencedor['nome']}.", size=18, color=ft.colors.WHITE),
                ft.Container(height=20),
                ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.HOME,
                                  on_click=lambda e: ao_voltar_hub(id_usuario))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def exibir_campeao(campeao):
        page.clean()
        page.add(
            ft.Column([
                ft.Text("🎉 PARABÉNS! ÉS O CAMPEÃO DA COPA!", size=28,
                        weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400),
                ft.Text(f"Campeão: {campeao['nome']}",
                        size=22, color=ft.colors.WHITE),
                ft.Container(height=20),
                ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.HOME,
                                  on_click=lambda e: ao_voltar_hub(id_usuario))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    btn_voltar = ft.OutlinedButton(
        "Voltar ao Hub", icon=ft.icons.ARROW_BACK, on_click=lambda e: ao_voltar_hub(id_usuario))

    page.add(
        lista_jogos,
        ft.Container(height=20),
        btn_voltar
    )

    renderizar_chaves()
