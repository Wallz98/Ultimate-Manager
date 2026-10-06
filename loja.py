import sqlite3
import random
import flet as ft
import gerador

PACOTES = [
    {
        "id": "bronze",
        "nome": "Pacote Bronze",
        "preco_moedas": 500,
        "preco_diamantes": 0,
        "estrelas_min": 1,
        "estrelas_max": 2,
        "cor": ft.Colors.BROWN_400,
        "bg_cor": "#2A1810",
        "desc": "1x Jogador Bronze (1-2★)"
    },
    {
        "id": "prata",
        "nome": "Pacote Prata",
        "preco_moedas": 1500,
        "preco_diamantes": 0,
        "estrelas_min": 2,
        "estrelas_max": 3,
        "cor": ft.Colors.GREY_400,
        "bg_cor": "#1E293B",
        "desc": "1x Jogador Prata (2-3★)"
    },
    {
        "id": "ouro",
        "nome": "Pacote Ouro",
        "preco_moedas": 3000,
        "preco_diamantes": 0,
        "estrelas_min": 3,
        "estrelas_max": 4,
        "cor": ft.Colors.AMBER_400,
        "bg_cor": "#3B2607",
        "desc": "1x Jogador Ouro (3-4★)"
    },
    {
        "id": "elite",
        "nome": "Pacote Épico Elite",
        "preco_moedas": 0,
        "preco_diamantes": 25,
        "estrelas_min": 4,
        "estrelas_max": 5,
        "cor": ft.Colors.CYAN_300,
        "bg_cor": "#082F49",
        "desc": "1x Craque Garantido (4-5★)"
    }
]

POSICOES = ["GOL", "ZAG", "MEI", "ATA"]


def obter_saldos(id_usuario):
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.moedas_free, u.diamantes 
        FROM times t 
        INNER JOIN usuarios u ON u.id = t.id_usuario 
        WHERE t.id_usuario = ?
    """, (id_usuario,))
    res = cursor.fetchone()
    conn.close()
    return res if res else (None, 0, 0)


def descontar_saldo(id_usuario, id_time, moedas, diamantes):
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    if moedas > 0:
        cursor.execute(
            "UPDATE times SET moedas_free = moedas_free - ? WHERE id = ?", (moedas, id_time))
    if diamantes > 0:
        cursor.execute(
            "UPDATE usuarios SET diamantes = diamantes - ? WHERE id = ?", (diamantes, id_usuario))
    conn.commit()
    conn.close()


def gerar_jogador_pacote(id_time, min_est, max_est):
    estrelas = random.randint(min_est, max_est)
    posicao = random.choice(POSICOES)
    nome = f"{random.choice(gerador.NOMES)} {random.choice(gerador.SOBRENOMES)}"

    base_stat = 20 + (estrelas * 14)
    vel = min(99, random.randint(base_stat - 5, base_stat + 10))
    fin = min(99, random.randint(base_stat - 5, base_stat + 10))
    dri = min(99, random.randint(base_stat - 5, base_stat + 10))
    pas = min(99, random.randint(base_stat - 5, base_stat + 10))
    dfe = min(99, random.randint(base_stat - 5, base_stat + 10))

    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jogadores (id_time, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
        VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?)
    """, (id_time, nome, posicao, estrelas, vel, fin, dri, pas, dfe))
    conn.commit()
    conn.close()

    return {
        "nome": nome,
        "posicao": posicao,
        "estrelas": estrelas,
        "vel": vel,
        "fin": fin,
        "dri": dri,
        "pas": pas,
        "dfe": dfe
    }


def carregar_loja(page: ft.Page, id_usuario: int, ao_voltar):
    page.clean()
    page.title = "FootManager - Mercado de Pacotes"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    id_time, moedas, diamantes = obter_saldos(id_usuario)

    txt_moedas = ft.Text(f"{moedas}", size=16,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    txt_diamantes = ft.Text(f"{diamantes}", size=16,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                              on_click=lambda e: ao_voltar(id_usuario)),
                ft.Text("LOJA DE PACOTES", size=20,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ]),
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONETIZATION_ON,
                                color=ft.Colors.AMBER_400, size=20),
                        txt_moedas
                    ], spacing=5),
                    bgcolor="#0F172A", padding=8, border_radius=8
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DIAMOND,
                                color=ft.Colors.CYAN_300, size=20),
                        txt_diamantes
                    ], spacing=5),
                    bgcolor="#0F172A", padding=8, border_radius=8
                ),
            ], spacing=10)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=900, bgcolor="#1E293B", padding=12, border_radius=12
    )

    def abrir_pacote(pacote):
        nonlocal moedas, diamantes, id_time
        p_moedas = pacote["preco_moedas"]
        p_diamantes = pacote["preco_diamantes"]

        if p_moedas > 0 and moedas < p_moedas:
            page.snack_bar = ft.SnackBar(
                ft.Text("Moedas insuficientes!"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return

        if p_diamantes > 0 and diamantes < p_diamantes:
            page.snack_bar = ft.SnackBar(
                ft.Text("Diamantes insuficientes!"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return

        descontar_saldo(id_usuario, id_time, p_moedas, p_diamantes)
        id_time, moedas, diamantes = obter_saldos(id_usuario)

        txt_moedas.value = str(moedas)
        txt_diamantes.value = str(diamantes)

        jog = gerar_jogador_pacote(
            id_time, pacote["estrelas_min"], pacote["estrelas_max"])

        estrelas = jog["estrelas"]
        if estrelas >= 5:
            cor_raridade = ft.Colors.CYAN_300
            bg_card = "#0C4A6E"
        elif estrelas >= 4:
            cor_raridade = ft.Colors.AMBER_400
            bg_card = "#3B2607"
        elif estrelas >= 3:
            cor_raridade = ft.Colors.GREY_400
            bg_card = "#1E293B"
        else:
            cor_raridade = ft.Colors.BROWN_400
            bg_card = "#2A1810"

        def mini_stat(rotulo, valor):
            return ft.Column([
                ft.Text(rotulo, size=10, color=ft.Colors.GREY_400,
                        weight=ft.FontWeight.BOLD),
                ft.Text(str(valor), size=14, color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1)

        grid_stats = ft.Row([
            mini_stat("VEL", jog["vel"]),
            mini_stat("FIN", jog["fin"]),
            mini_stat("DRI", jog["dri"]),
            mini_stat("PAS", jog["pas"]),
            mini_stat("DEF", jog["dfe"]),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=270)

        card_jogador = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            jog["posicao"], size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        bgcolor=cor_raridade,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=4
                    ),
                    ft.Text("★" * estrelas, size=15, color=ft.Colors.AMBER_400)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=270),
                ft.Container(height=5),
                ft.Icon(name=ft.Icons.PERSON, size=60, color=ft.Colors.WHITE),
                ft.Text(jog["nome"], size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Divider(color="#334155", thickness=1),
                grid_stats
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            width=290,
            padding=16,
            bgcolor=bg_card,
            border_radius=15,
            border=ft.border.all(2, cor_raridade),
            shadow=ft.BoxShadow(blur_radius=15, color=cor_raridade)
        )

        def fechar_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor="#1E293B",
            title=ft.Text("🎉 NOVO JOGADOR REVELADO!", color=ft.Colors.AMBER_400,
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, size=16),
            content=card_jogador,
            actions=[
                ft.ElevatedButton(
                    "Adicionar ao Elenco",
                    icon=ft.Icons.CHECK,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    on_click=fechar_dialog
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    grid_pacotes = ft.Row(wrap=True, spacing=20,
                          alignment=ft.MainAxisAlignment.CENTER, width=900)

    for p in PACOTES:
        custo_txt = f"{p['preco_moedas']} Moedas" if p['preco_moedas'] > 0 else f"{p['preco_diamantes']} Diamantes"
        icone_custo = ft.Icons.MONETIZATION_ON if p['preco_moedas'] > 0 else ft.Icons.DIAMOND
        cor_custo = ft.Colors.AMBER_400 if p['preco_moedas'] > 0 else ft.Colors.CYAN_300

        card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CARD_GIFTCARD, size=48, color=p["cor"]),
                ft.Text(p["nome"], size=16, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Text(p["desc"], size=11, color=ft.Colors.GREY_400),
                ft.Container(height=5),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(icone_custo, size=16, color=cor_custo),
                        ft.Text(custo_txt, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    style=ft.ButtonStyle(
                        bgcolor="#0F172A", color=ft.Colors.WHITE),
                    on_click=lambda e, pac=p: abrir_pacote(pac)
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            width=200, height=220, bgcolor=p["bg_cor"], border_radius=12, padding=15, border=ft.border.all(1.5, p["cor"])
        )

        grid_pacotes.controls.append(card)

    page.add(
        header,
        ft.Container(height=20),
        grid_pacotes
    )
