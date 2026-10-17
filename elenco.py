import base64
import os
import sqlite3
import flet as ft

TATICAS = {
    "4-4-2": {"GOL": 1, "ZAG": 4, "MEI": 4, "ATA": 2},
    "4-3-3": {"GOL": 1, "ZAG": 4, "MEI": 3, "ATA": 3},
    "3-5-2": {"GOL": 1, "ZAG": 3, "MEI": 5, "ATA": 2},
    "4-5-1": {"GOL": 1, "ZAG": 4, "MEI": 5, "ATA": 1},
    "5-3-2": {"GOL": 1, "ZAG": 5, "MEI": 3, "ATA": 2},
}


def buscar_arquivo_imagem(nome_ou_caminho):
    if not nome_ou_caminho:
        nome_ou_caminho = "Cartoonify (1).png"

    nome_base = os.path.basename(str(nome_ou_caminho)).strip().lower()

    bases = [
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__))
    ]

    pastas_busca = []
    for base in bases:
        pastas_busca.extend([
            os.path.join(base, "assets", "Player_img"),
            os.path.join(base, "assets", "Players_img"),
            os.path.join(base, "assets", "player_img"),
            os.path.join(base, "assets", "players_img"),
            os.path.join(base, "assets"),
            os.path.join(base, "Player_img"),
            os.path.join(base, "Players_img"),
            base
        ])

    for pasta in pastas_busca:
        if os.path.exists(pasta) and os.path.isdir(pasta):
            try:
                for arq in os.listdir(pasta):
                    if arq.lower() == nome_base:
                        return os.path.join(pasta, arq)
            except Exception:
                pass

    for pasta in pastas_busca:
        if os.path.exists(pasta) and os.path.isdir(pasta):
            try:
                for arq in os.listdir(pasta):
                    if arq.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        return os.path.join(pasta, arq)
            except Exception:
                pass

    return None


def criar_avatar_jogador(caminho_foto, tamanho=52, cor_borda=ft.Colors.CYAN_400):
    caminho_encontrado = buscar_arquivo_imagem(caminho_foto)

    if caminho_encontrado:
        try:
            with open(caminho_encontrado, "rb") as f:
                b64_str = base64.b64encode(f.read()).decode('utf-8')
            img_widget = ft.Image(
                src_base64=b64_str,
                width=tamanho,
                height=tamanho,
                fit=ft.ImageFit.COVER
            )
        except Exception:
            img_widget = ft.Icon(
                ft.Icons.PERSON, size=tamanho * 0.7, color=ft.Colors.GREY_400)
    else:
        img_widget = ft.Icon(ft.Icons.PERSON, size=tamanho *
                             0.7, color=ft.Colors.GREY_400)

    return ft.Container(
        content=img_widget,
        width=tamanho,
        height=tamanho,
        border_radius=tamanho / 2,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.border.all(1.5, cor_borda),
        alignment=ft.alignment.center
    )


def buscar_dados_elenco(id_usuario):
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
        SELECT id, nome, posicao, titular, estrelas, 
               COALESCE(foto, 'Cartoonify (1).png')
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
            "foto": j[5]
        })

    return id_time, nome_time, jogadores


def salvar_titulares_db(jogadores):
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
    cores_posicao = {
        "GOL": ft.colors.AMBER_700,
        "ZAG": ft.colors.BLUE_700,
        "MEI": ft.colors.GREEN_700,
        "ATA": ft.colors.RED_700
    }

    avatar = criar_avatar_jogador(
        jogador["foto"], tamanho=48, cor_borda=ft.colors.AMBER_400)

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        jogador["posicao"], size=10, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    bgcolor=cores_posicao.get(
                        jogador["posicao"], ft.colors.GREY_700),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_size=14,
                    icon_color=ft.colors.RED_400,
                    tooltip="Remover",
                    on_click=lambda e: ao_remover(jogador)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            avatar,

            ft.Text(
                jogador["nome"].split()[0],
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE,
                no_wrap=True,
                max_lines=1
            ),
            ft.Text("⭐ " * jogador["estrelas"], size=8)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=3),
        width=115,
        padding=8,
        bgcolor="#0F172A",
        border_radius=10,
        border=ft.border.all(1, ft.colors.AMBER_400),
        shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.BLACK38)
    )


def criar_card_reserva_completo(jogador, ao_escalar):
    cores_posicao = {
        "GOL": ft.colors.AMBER_700,
        "ZAG": ft.colors.BLUE_700,
        "MEI": ft.colors.GREEN_700,
        "ATA": ft.colors.RED_700
    }
    cor_badge = cores_posicao.get(jogador["posicao"], ft.colors.GREY_700)

    avatar = criar_avatar_jogador(
        jogador["foto"], tamanho=56, cor_borda=ft.colors.CYAN_400)

    btn_escalar = ft.ElevatedButton(
        text="Promover",
        icon=ft.icons.ADD,
        style=ft.ButtonStyle(color=ft.colors.GREEN_300, bgcolor="#0F172A"),
        on_click=lambda e: ao_escalar(jogador)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        jogador["posicao"], size=10, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    bgcolor=cor_badge,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ),
                ft.Text("⭐ " * jogador["estrelas"], size=8),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            avatar,

            ft.Text(
                jogador["nome"],
                size=12,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE,
                no_wrap=True,
                max_lines=1
            ),

            btn_escalar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        width=135,
        padding=10,
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
    page.scroll = ft.ScrollMode.AUTO

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
            goleiros_atuais = sum(
                1 for j in jogadores if j["titular"] and j["posicao"] == "GOL")

            if pos == "GOL" and goleiros_atuais >= 1:
                txt_status.value = "⚠️ É proibido ter mais de 1 Goleiro no time titular!"
                txt_status.color = ft.colors.RED_400
                page.update()
                return

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

        painel_titulares.controls.clear()
        titulares = [j for j in jogadores if j["titular"]]

        for t in titulares:
            painel_titulares.controls.append(
                criar_mini_card_titular(
                    t, ao_remover=lambda j: alterar_status_titular(j, False))
            )

        if not titulares:
            painel_titulares.controls.append(
                ft.Text("Nenhum titular selecionado.",
                        color=ft.colors.GREY_500, size=13)
            )

        painel_reservas.controls.clear()
        seccoes_reservas = {"GOL": [], "ZAG": [], "MEI": [], "ATA": []}

        for j in jogadores:
            if not j["titular"]:
                card = criar_card_reserva_completo(
                    j, ao_escalar=lambda j_res: alterar_status_titular(j_res, True))
                seccoes_reservas[j["posicao"]].append(card)

        titulos_posicao = {
            "GOL": f"🧤 Goleiros Reservas ({tatica_req['GOL']} exigidos)",
            "ZAG": f"🛡️ Zagueiros Reservas ({tatica_req['ZAG']} exigidos)",
            "MEI": f"🧠 Meias Reservas ({tatica_req['MEI']} exigidos)",
            "ATA": f"⚡ Atacantes Reservas ({tatica_req['ATA']} exigidos)"
        }

        tem_reserva = False
        for chave in ["GOL", "ZAG", "MEI", "ATA"]:
            if seccoes_reservas[chave]:
                tem_reserva = True
                painel_reservas.controls.append(
                    ft.Text(
                        titulos_posicao[chave], size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                )
                painel_reservas.controls.append(
                    ft.Row(seccoes_reservas[chave],
                           wrap=True, spacing=12, run_spacing=12)
                )

        if not tem_reserva:
            painel_reservas.controls.append(
                ft.Text("Todos os jogadores estão escalados no time titular.",
                        color=ft.colors.GREEN_400, size=14)
            )

        page.update()

    drop_tatica.on_change = renderizar_interface

    topo = ft.Row([
        ft.Column([
            ft.Text("GESTÃO TÁTICA E ELENCO", size=22,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(f"Clube: {nome_time} | Total: {len(jogadores)} Jogadores",
                    size=13, color=ft.colors.GREY_400),
        ]),
        ft.Row([
            drop_tatica,
            ft.ElevatedButton("Guardar Tática", icon=ft.icons.SAVE,
                              height=40, on_click=salvar_escalacao),
            ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.ARROW_BACK,
                              height=40, on_click=lambda e: ao_voltar_hub(id_usuario))
        ], spacing=10)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=920)

    secao_titulares = ft.Container(
        content=ft.Column([
            ft.Text("⭐ TIME TITULAR", size=15,
                    weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400),
            painel_titulares
        ]),
        padding=12,
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
                ft.Divider(color=ft.colors.GREY_800, height=15),
                ft.Text("📋 BANCO DE RESERVAS / PLANTEL", size=18,
                        weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                painel_reservas
            ],
            width=920,
            spacing=12
        )
    )

    renderizar_interface()
