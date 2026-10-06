import sqlite3
import flet as ft

# Mapeamento das táticas exigidas e a quantidade fixa de cada posição
TATICAS = {
    "4-4-2": {"GOL": 1, "ZAG": 4, "MEI": 4, "ATA": 2},
    "4-3-3": {"GOL": 1, "ZAG": 4, "MEI": 3, "ATA": 3},
    "3-5-2": {"GOL": 1, "ZAG": 3, "MEI": 5, "ATA": 2},
    "4-5-1": {"GOL": 1, "ZAG": 4, "MEI": 5, "ATA": 1},
    "5-3-2": {"GOL": 1, "ZAG": 5, "MEI": 3, "ATA": 2},
}


def buscar_dados_elenco(id_usuario):
    """Busca o time e todos os jogadores do banco de dados."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nome FROM times WHERE id_usuario = ?", (id_usuario,))
    time_data = cursor.fetchone()

    if not time_data:
        conn.close()
        return None, None, []

    id_time, nome_time = time_data

    cursor.execute("""
        SELECT id, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa
        FROM jogadores
        WHERE id_time = ?
        ORDER BY 
            CASE posicao
                WHEN 'GOL' THEN 1
                WHEN 'ZAG' THEN 2
                WHEN 'MEI' THEN 3
                WHEN 'ATA' THEN 4
                ELSE 5
            END,
            titular DESC,
            nome ASC
    """, (id_time,))

    jogadores_raw = cursor.fetchall()
    conn.close()

    jogadores = []
    for j in jogadores_raw:
        jogadores.append({
            "id": j[0],
            "nome": j[1],
            "posicao": j[2],
            "titular": bool(j[3]),
            "estrelas": j[4],
            "vel": j[5],
            "fin": j[6],
            "dri": j[7],
            "pas": j[8],
            "def": j[9]
        })

    return id_time, nome_time, jogadores


def salvar_titulares_db(jogadores):
    """Atualiza a coluna 'titular' de todos os jogadores no banco SQLite."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    for j in jogadores:
        cursor.execute(
            "UPDATE jogadores SET titular = ? WHERE id = ?",
            (1 if j["titular"] else 0, j["id"])
        )

    conn.commit()
    conn.close()


def criar_mini_card_titular(jogador, ao_remover):
    """Cria o mini-card visual exclusivo para os Titulares."""
    cores_posicao = {
        "GOL": ft.colors.AMBER_700,
        "ZAG": ft.colors.BLUE_700,
        "MEI": ft.colors.GREEN_700,
        "ATA": ft.colors.RED_700
    }

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        jogador["posicao"], size=9, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    bgcolor=cores_posicao.get(
                        jogador["posicao"], ft.colors.GREY_700),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_size=12,
                    icon_color=ft.colors.RED_400,
                    tooltip="Remover dos Titulares",
                    on_click=lambda e: ao_remover(jogador)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(jogador["nome"], size=11, weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE, no_wrap=True),
            ft.Text("⭐ " * jogador["estrelas"], size=8)
        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
        width=130,
        padding=8,
        bgcolor="#0F172A",
        border_radius=8,
        border=ft.border.all(1, ft.colors.AMBER_400),
        shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.BLACK38)
    )


def criar_card_reserva_completo(jogador, ao_escalar):
    """Cria a exibição original em card/linha para os jogadores do banco de reservas."""
    cores_posicao = {
        "GOL": ft.colors.AMBER_700,
        "ZAG": ft.colors.BLUE_700,
        "MEI": ft.colors.GREEN_700,
        "ATA": ft.colors.RED_700
    }
    cor_badge = cores_posicao.get(jogador["posicao"], ft.colors.GREY_700)

    if jogador["posicao"] == "GOL":
        r1, v1 = "VEL", jogador["vel"]
        r2, v2 = "RFL", jogador["fin"]
        r3, v3 = "POS", jogador["dri"]
        r4, v4 = "REP", jogador["pas"]
        r5, v5 = "DEF", jogador["def"]
    else:
        r1, v1 = "VEL", jogador["vel"]
        r2, v2 = "FIN", jogador["fin"]
        r3, v3 = "DRI", jogador["dri"]
        r4, v4 = "PAS", jogador["pas"]
        r5, v5 = "DEF", jogador["def"]

    btn_escalar = ft.ElevatedButton(
        text="Promover a Titular",
        icon=ft.icons.ADD_CIRCLE_OUTLINE,
        style=ft.ButtonStyle(color=ft.colors.GREEN_300, bgcolor="#0F172A"),
        on_click=lambda e: ao_escalar(jogador)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        jogador["posicao"], size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    bgcolor=cor_badge,
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=5
                ),
                ft.Text("⭐ " * jogador["estrelas"], size=11),
                ft.Text("RESERVA", size=10, weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREY_500)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Divider(height=8, color=ft.colors.TRANSPARENT),

            ft.Text(jogador["nome"], size=15, weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE, no_wrap=True),

            ft.Divider(height=8, color=ft.colors.GREY_800),

            ft.Column([
                ft.Row([
                    ft.Text(f"{r1}: {v1}", size=11, color=ft.colors.GREY_300),
                    ft.Text(f"{r2}: {v2}", size=11, color=ft.colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(f"{r3}: {v3}", size=11, color=ft.colors.GREY_300),
                    ft.Text(f"{r4}: {v4}", size=11, color=ft.colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(f"{r5}: {v5}", size=11, color=ft.colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.START),
            ], spacing=2),

            ft.Divider(height=8, color=ft.colors.TRANSPARENT),
            btn_escalar
        ]),
        width=210,
        padding=12,
        bgcolor="#1E293B",
        border_radius=12,
        border=ft.border.all(1, ft.colors.GREY_800),
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK26)
    )


def carregar_elenco(page: ft.Page, id_usuario: int, ao_voltar_hub):
    page.clean()
    page.title = "FootManager - Gestão de Elenco e Táticas"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO  # Torna toda a página rolável

    id_time, nome_time, jogadores = buscar_dados_elenco(id_usuario)

    if not jogadores:
        page.add(
            ft.Text("⚠️ Nenhum jogador encontrado no plantel.",
                    color=ft.colors.RED_400, size=18),
            ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.ARROW_BACK,
                              on_click=lambda e: ao_voltar_hub(id_usuario))
        )
        return

    drop_tatica = ft.Dropdown(
        label="Formação Tática",
        value="4-4-2",
        options=[ft.dropdown.Option(t) for t in TATICAS.keys()],
        width=160,
        color=ft.colors.WHITE,
        border_color=ft.colors.AMBER_400
    )

    txt_status = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

    painel_titulares = ft.Row(wrap=True, spacing=10, run_spacing=10)
    painel_reservas = ft.Column(spacing=20)

    def alterar_status_titular(jogador, novo_status):
        tatica_atual = TATICAS[drop_tatica.value]
        pos = jogador["posicao"]

        if novo_status:
            # Contagem atual de titulares na posição
            goleiros_atuais = sum(
                1 for j in jogadores if j["titular"] and j["posicao"] == "GOL")

            # Bloqueio estrito de 2 goleiros
            if pos == "GOL" and goleiros_atuais >= 1:
                txt_status.value = "⚠️ É proibido ter mais de 1 Goleiro no time titular!"
                txt_status.color = ft.colors.RED_400
                page.update()
                return

            # Validação do limite máximo da posição na tática
            titulares_posicao = sum(
                1 for j in jogadores if j["titular"] and j["posicao"] == pos)
            limite_posicao = tatica_atual[pos]

            if titulares_posicao >= limite_posicao:
                txt_status.value = f"⚠️ A tática {drop_tatica.value} permite no máximo {limite_posicao} {pos}(s)!"
                txt_status.color = ft.colors.RED_400
                page.update()
                return

            jogador["titular"] = True
            txt_status.value = f"✅ {jogador['nome']} adicionado ao time titular!"
            txt_status.color = ft.colors.GREEN_400
        else:
            jogador["titular"] = False
            txt_status.value = f"ℹ️ {jogador['nome']} movido para o banco de reservas."
            txt_status.color = ft.colors.AMBER_400

        renderizar_interface()

    def salvar_escalacao(e):
        tatica_atual = TATICAS[drop_tatica.value]
        contagem = {"GOL": 0, "ZAG": 0, "MEI": 0, "ATA": 0}

        for j in jogadores:
            if j["titular"]:
                contagem[j["posicao"]] += 1

        # Validação Rígida
        erros = []
        for pos, limite in tatica_atual.items():
            if contagem[pos] != limite:
                erros.append(f"{pos}: {contagem[pos]}/{limite}")

        if erros:
            txt_status.value = f"❌ Preencha os 11 titulares de acordo com o {drop_tatica.value}! Pendente: (" + ", ".join(
                erros) + ")"
            txt_status.color = ft.colors.RED_400
            page.update()
            return

        salvar_titulares_db(jogadores)
        txt_status.value = f"💾 Tática {drop_tatica.value} guardada com sucesso no banco de dados!"
        txt_status.color = ft.colors.GREEN_400
        page.update()

    def renderizar_interface(e=None):
        tatica_req = TATICAS[drop_tatica.value]

        # 1. Atualiza a Seção de Titulares (Apenas Mini Cards)
        painel_titulares.controls.clear()
        titulares = [j for j in jogadores if j["titular"]]

        for t in titulares:
            painel_titulares.controls.append(
                criar_mini_card_titular(
                    t, ao_remover=lambda j: alterar_status_titular(j, False))
            )

        if not titulares:
            painel_titulares.controls.append(
                ft.Text("Nenhum titular selecionado. Clique em 'Promover a Titular' nos reservas abaixo.",
                        color=ft.colors.GREY_500, size=13)
            )

        # 2. Atualiza a Seção de Reservas (Exibidos em Colunas por Posição)
        painel_reservas.controls.clear()
        seccoes_reservas = {"GOL": [], "ZAG": [], "MEI": [], "ATA": []}

        for j in jogadores:
            if not j["titular"]:
                card = criar_card_reserva_completo(
                    j, ao_escalar=lambda j_res: alterar_status_titular(j_res, True))
                seccoes_reservas[j["posicao"]].append(card)

        titulos_posicao = {
            "GOL": f"🧤 Goleiros Reservas (Exigido no titular: {tatica_req['GOL']})",
            "ZAG": f"🛡️ Zagueiros Reservas (Exigido no titular: {tatica_req['ZAG']})",
            "MEI": f"🧠 Meias Reservas (Exigido no titular: {tatica_req['MEI']})",
            "ATA": f"⚡ Atacantes Reservas (Exigido no titular: {tatica_req['ATA']})"
        }

        tem_reserva = False
        for chave in ["GOL", "ZAG", "MEI", "ATA"]:
            if seccoes_reservas[chave]:
                tem_reserva = True
                painel_reservas.controls.append(
                    ft.Text(
                        titulos_posicao[chave], size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                )
                painel_reservas.controls.append(
                    ft.Row(seccoes_reservas[chave],
                           wrap=True, spacing=15, run_spacing=15)
                )

        if not tem_reserva:
            painel_reservas.controls.append(
                ft.Text("Todos os jogadores do plantel estão atualmente escalados no time titular.",
                        color=ft.colors.GREEN_400, size=14)
            )

        page.update()

    drop_tatica.on_change = renderizar_interface

    topo = ft.Row([
        ft.Column([
            ft.Text("GESTÃO TÁTICA E ELENCO", size=24,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(f"Clube: {nome_time} | Total no Elenco: {len(jogadores)} Jogadores",
                    size=14, color=ft.colors.GREY_400),
        ]),
        ft.Row([
            drop_tatica,
            ft.ElevatedButton("Guardar Tática", icon=ft.icons.SAVE,
                              height=45, on_click=salvar_escalacao),
            ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.ARROW_BACK,
                              height=45, on_click=lambda e: ao_voltar_hub(id_usuario))
        ], spacing=10)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=920)

    secao_titulares = ft.Container(
        content=ft.Column([
            ft.Text("⭐ TIME TITULAR (MINI CARDS)", size=15,
                    weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400),
            painel_titulares
        ]),
        padding=15,
        bgcolor="#1E293B",
        border_radius=12,
        width=920,
        border=ft.border.all(1, ft.colors.AMBER_400)
    )

    page.add(
        ft.Column(
            controls=[
                topo,
                txt_status,
                secao_titulares,
                ft.Divider(color=ft.colors.GREY_800, height=20),
                ft.Text("📋 BANCO DE RESERVAS / PLANTEL", size=20,
                        weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                painel_reservas
            ],
            width=920,
            spacing=15
        )
    )

    renderizar_interface()


if __name__ == "__main__":
    def main(page: ft.Page):
        carregar_elenco(page, id_usuario=1,
                        ao_voltar_hub=lambda id_u: print("Voltar ao Hub"))

    ft.app(target=main)
