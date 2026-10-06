import database
import inspect
import sqlite3
import flet as ft

# Importação dos módulos do projeto
import liga
import copa
import elenco
import tatica
import academia
import loja
import gerador


def criar_escudo_compativel(formato, simbolo, c1, c2, c3, c4, tamanho=75):
    """Filtra os parâmetros passados para gerador.criar_escudo_time conforme a sua assinatura."""
    sig = inspect.signature(gerador.criar_escudo_time)
    todos_args = {
        'formato': formato,
        'simbolo': simbolo,
        'cor_principal': c1,
        'cor_secundaria': c2,
        'cor_borda': c3,
        'cor_texto': c4,
        'tamanho': tamanho
    }
    has_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    args_validos = todos_args if has_kwargs else {
        k: v for k, v in todos_args.items() if k in sig.parameters}

    return gerador.criar_escudo_time(**args_validos)


def obter_dados_time(id_usuario):
    """Procura as informações completas do clube, saldo, nível, EXP e diamantes no BD."""
    database.inicializar_banco()

    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    # 1. Garante que as colunas 'formato' e 'simbolo' existem na tabela
    for col, default in [('formato', "'Losango'"), ('simbolo', "'Bola'")]:
        try:
            cursor.execute(
                f"ALTER TABLE times ADD COLUMN {col} TEXT DEFAULT {default}")
        except sqlite3.OperationalError:
            pass

    # 2. Atualiza o clube na BD caso ainda esteja guardado como 'Clássico'
    cursor.execute("""
        UPDATE times 
        SET formato = 'Losango',
            simbolo = 'Bola',
            cor_1 = 'Azul',
            cor_2 = 'Preto',
            cor_3 = 'Amarelo',
            cor_4 = 'Branco'
        WHERE id_usuario = ? AND (formato IS NULL OR formato = 'Clássico')
    """, (id_usuario,))
    conn.commit()

    cursor.execute("""
        SELECT t.id, t.nome, 
               COALESCE(t.formato, 'Losango'),
               COALESCE(t.simbolo, 'Bola'),
               COALESCE(t.cor_1, 'Azul'), 
               COALESCE(t.cor_2, 'Preto'), 
               COALESCE(t.cor_3, 'Amarelo'), 
               COALESCE(t.cor_4, 'Branco'),
               t.moedas_free, u.diamantes,
               COALESCE(u.nivel, 1), COALESCE(u.exp, 0)
        FROM times t
        INNER JOIN usuarios u ON u.id = t.id_usuario
        WHERE t.id_usuario = ?
    """, (id_usuario,))
    time = cursor.fetchone()
    conn.close()
    return time


def obter_jogadores(id_time):
    """Procura a lista de jogadores da equipa para exibir no Hub, incluindo energia."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa, COALESCE(energia, 100)
        FROM jogadores WHERE id_time = ? ORDER BY titular DESC, posicao ASC
    """, (id_time,))
    jogadores = cursor.fetchall()
    conn.close()
    return jogadores


def obter_cor_card_por_estrelas(estrelas):
    """Define as cores de fundo e borda baseadas na quantidade de estrelas."""
    if estrelas <= 2:
        return {"border": ft.Colors.BROWN_400, "bg": "#2A1810", "categoria": "BRONZE"}
    elif estrelas <= 4:
        return {"border": ft.Colors.GREY_400, "bg": "#1E293B", "categoria": "PRATA"}
    else:
        return {"border": ft.Colors.AMBER_400, "bg": "#3B2607", "categoria": "OURO"}


def carregar_hub(page: ft.Page, id_usuario: int):
    page.clean()
    page.title = "FootManager - Central do Clube"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    time = obter_dados_time(id_usuario)

    if not time:
        page.add(
            ft.Text("⚠️ Nenhuma equipa encontrada para este utilizador.",
                    color=ft.Colors.RED_400, size=18)
        )
        return

    (id_time, nome_time, formato_escudo, simbolo_escudo, c1, c2, c3, c4,
     moedas_free, diamantes, nivel, exp) = time

    jogadores = obter_jogadores(id_time)

    exp_necessaria = nivel * 100
    progresso_exp = min(
        1.0, exp / exp_necessaria) if exp_necessaria > 0 else 0.0

    # Gera o escudo de forma compatível com os parâmetros disponíveis no gerador
    escudo_clube = gerador.criar_escudo_time(
        formato=formato_escudo,
        simbolo=simbolo_escudo,
        cor_principal=c1,
        cor_secundaria=c2,
        cor_borda=c3,
        cor_texto=c4,
        tamanho=75
    )

    header = ft.Container(
        content=ft.Row([
            ft.Row([
                escudo_clube,
                ft.Column([
                    ft.Text(nome_time.upper(), size=22,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(
                                f"NÍVEL {nivel}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                            bgcolor=ft.Colors.AMBER_400, padding=ft.padding.symmetric(horizontal=6, vertical=2), border_radius=4
                        ),
                        ft.Text(
                            f"Plantel: {len(jogadores)} Jogadores", size=12, color=ft.Colors.GREY_400),
                    ], spacing=10),
                    ft.Container(height=2),
                    ft.Column([
                        ft.Row([
                            ft.Text("EXP", size=10, color=ft.Colors.GREY_400,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"{exp} / {exp_necessaria}",
                                    size=10, color=ft.Colors.GREY_400)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=220),
                        ft.ProgressBar(value=progresso_exp, width=220,
                                       color=ft.Colors.AMBER_400, bgcolor="#0F172A")
                    ], spacing=2)
                ], spacing=3)
            ], spacing=15),

            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONETIZATION_ON,
                                color=ft.Colors.AMBER, size=20),
                        ft.Text(f"{moedas_free}", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                    ], spacing=5),
                    bgcolor="#0F172A", padding=10, border_radius=10
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DIAMOND,
                                color=ft.Colors.CYAN_300, size=20),
                        ft.Text(f"{diamantes}", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                    ], spacing=5),
                    bgcolor="#0F172A", padding=10, border_radius=10
                ),
            ], spacing=12)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=950, bgcolor="#1E293B", padding=15, border_radius=15
    )

    card_elenco = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.GROUPS, size=36, color=ft.Colors.BLUE_400),
            ft.Text("Plantel", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Gerir Jogadores", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        on_click=lambda e: elenco.carregar_elenco(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    card_tatica = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.SPORTS, size=36, color=ft.Colors.GREEN_400),
            ft.Text("Tática", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Formação & Onze", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        on_click=lambda e: tatica.carregar_tatica(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    card_academia = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.FITNESS_CENTER, size=36,
                    color=ft.Colors.ORANGE_400),
            ft.Text("Academia", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Evoluir Atributos", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        on_click=lambda e: academia.carregar_academia(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    card_loja = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.SHOPPING_BAG, size=36, color=ft.Colors.AMBER_400),
            ft.Text("Loja", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Comprar Pacotes", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        on_click=lambda e: loja.carregar_loja(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    card_liga = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.LEADERBOARD, size=36, color=ft.Colors.CYAN_400),
            ft.Text("Liga", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Pontos Corridos", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        border=ft.border.all(1, ft.Colors.CYAN_700),
        on_click=lambda e: liga.carregar_liga(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    card_copa = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.EMOJI_EVENTS, size=36, color=ft.Colors.AMBER_400),
            ft.Text("Copa", size=15, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("Mata-Mata", size=11, color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=145, height=115, bgcolor="#1E293B", border_radius=12, ink=True,
        border=ft.border.all(1, ft.Colors.AMBER_700),
        on_click=lambda e: copa.carregar_copa(
            page, id_usuario, lambda id_u: carregar_hub(page, id_u))
    )

    grid_menu = ft.Row(
        [card_elenco, card_tatica, card_academia, card_loja, card_liga, card_copa],
        spacing=12, alignment=ft.MainAxisAlignment.CENTER, wrap=True, width=950
    )

    def criar_card_mini_jogador(j):
        _, nome, pos, titular, estrelas, vel, fin, dri, pas, def_stat, energia = j
        estilo = obter_cor_card_por_estrelas(estrelas)
        status_txt = "TITULAR" if titular == 1 else "SUPLENTE"
        status_cor = ft.Colors.GREEN_400 if titular == 1 else ft.Colors.GREY_500

        cor_energia = (
            ft.Colors.GREEN_400 if energia >= 70
            else ft.Colors.AMBER_400 if energia >= 40
            else ft.Colors.RED_400
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            pos, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor="#0F172A", padding=ft.padding.symmetric(horizontal=6, vertical=2), border_radius=4
                    ),
                    ft.Row([
                        ft.Text(f"⚡{energia}%", size=10,
                                weight=ft.FontWeight.BOLD, color=cor_energia),
                        ft.Text(status_txt, size=10,
                                weight=ft.FontWeight.BOLD, color=status_cor)
                    ], spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Text(nome, size=13, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text("⭐ " * estrelas, size=11),
                ft.Divider(color=ft.Colors.GREY_800, height=8),

                ft.Row([
                    ft.Text(f"VEL {vel}", size=10, color=ft.Colors.GREY_300),
                    ft.Text(f"FIN {fin}", size=10, color=ft.Colors.GREY_300),
                    ft.Text(f"DEF {def_stat}", size=10,
                            color=ft.Colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            width=175, height=135, bgcolor=estilo["bg"], border_radius=10, padding=10,
            border=ft.border.all(1.5, estilo["border"])
        )

    cards_jogadores = [criar_card_mini_jogador(j) for j in jogadores[:10]]

    seccao_destaques = ft.Column([
        ft.Text("🌟 DESTAQUES DO ELENCO", size=18,
                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.Row(cards_jogadores, wrap=True, spacing=15,
               alignment=ft.MainAxisAlignment.CENTER, width=950)
    ], spacing=15)

    page.add(
        header,
        ft.Container(height=15),
        grid_menu,
        ft.Container(height=25),
        seccao_destaques
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        carregar_hub(page, id_usuario=1)

    ft.app(target=main)
