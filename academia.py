import flet as ft
import sqlite3

# Configurações de Custo e Evolução
CUSTO_TREINO_ELENCO = 10  # Custo em Diamantes para o time todo
INCREMENTO = 1            # Pontos ganhos por treino


def calcular_estrelas(media):
    """Calcula o número de estrelas baseado na média dos atributos."""
    if media < 25:
        return 1
    elif media < 45:
        return 2
    elif media < 65:
        return 3
    elif media < 85:
        return 4
    else:
        return 5


def buscar_dados_academia(id_usuario):
    """Busca o saldo de diamantes da tabela usuarios e os jogadores do time."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, u.diamantes 
        FROM times t 
        INNER JOIN usuarios u ON u.id = t.id_usuario 
        WHERE t.id_usuario = ?
    """, (id_usuario,))
    time_data = cursor.fetchone()

    if not time_data:
        conn.close()
        return None, 0, []

    id_time, diamantes = time_data

    cursor.execute("""
        SELECT id, nome, posicao, estrelas, velocidade, finalizacao, drible, passe, defesa
        FROM jogadores
        WHERE id_time = ?
        ORDER BY 
            CASE posicao
                WHEN 'GOL' THEN 1
                WHEN 'ZAG' THEN 2
                WHEN 'MEI' THEN 3
                WHEN 'ATA' THEN 4
            END, nome ASC
    """, (id_time,))

    jogadores = cursor.fetchall()
    conn.close()
    return id_time, diamantes, jogadores


def executar_treino_elenco(id_usuario, id_time, tipo_treino, diamantes_atuais, callback_atualizar):
    """Aplica o treino coletivo em todos os jogadores do elenco."""
    if diamantes_atuais < CUSTO_TREINO_ELENCO:
        callback_atualizar(
            False, "💎 Diamantes insuficientes para o Treino de Elenco!")
        return

    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    # 1. Deduz os diamantes da tabela usuarios
    cursor.execute("UPDATE usuarios SET diamantes = diamantes - ? WHERE id = ?",
                   (CUSTO_TREINO_ELENCO, id_usuario))

    # 2. Mapeia quais colunas vão evoluir com base no foco
    if tipo_treino == "FISICO":
        colunas = ["velocidade"]
        nome_treino = "Físico (Velocidade)"
    elif tipo_treino == "TACTICO":
        colunas = ["passe", "drible"]
        nome_treino = "Tático (Passe & Posicionamento)"
    elif tipo_treino == "TECNICO":
        colunas = ["finalizacao", "defesa"]
        nome_treino = "Técnico (Ataque/Reflexos & Defesa)"
    else:
        colunas = ["velocidade", "finalizacao", "drible", "passe", "defesa"]
        nome_treino = "Geral"

    # 3. Atualiza todos os jogadores do time
    cursor.execute(
        "SELECT id, velocidade, finalizacao, drible, passe, defesa FROM jogadores WHERE id_time = ?", (id_time,))
    jogadores = cursor.fetchall()

    for j in jogadores:
        id_j, vel, fin, dri, pas, def_stat = j
        stats = {"velocidade": vel, "finalizacao": fin,
                 "drible": dri, "passe": pas, "defesa": def_stat}

        # Aplica incremento respeitando a trava de 99
        for col in colunas:
            stats[col] = min(stats[col] + INCREMENTO, 99)

        # Recalcula média e estrelas
        media = sum(stats.values()) / 5.0
        novas_estrelas = calcular_estrelas(media)

        cursor.execute("""
            UPDATE jogadores 
            SET velocidade = ?, finalizacao = ?, drible = ?, passe = ?, defesa = ?, estrelas = ?
            WHERE id = ?
        """, (stats["velocidade"], stats["finalizacao"], stats["drible"], stats["passe"], stats["defesa"], novas_estrelas, id_j))

    conn.commit()
    conn.close()

    callback_atualizar(
        True, f"🏋️ Treino de Elenco {nome_treino} concluído! (+{INCREMENTO} para o time)")


def carregar_academia(page: ft.Page, id_usuario: int, ao_voltar_hub):
    page.clean()
    page.title = "FootManager - Treino de Elenco"
    page.bgcolor = "#0F172A"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    id_time, diamantes, jogadores = buscar_dados_academia(id_usuario)

    saldo_diamantes_text = ft.Text(
        f"{diamantes}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    msg_status = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    def recarrega_tela(sucesso, mensagem):
        msg_status.value = mensagem
        msg_status.color = ft.colors.GREEN_400 if sucesso else ft.colors.RED_400
        carregar_academia(page, id_usuario, ao_voltar_hub)

    # --- CABEÇALHO ---
    header = ft.Row([
        ft.Column([
            ft.Text("🏋️ TREINO DE ELENCO", size=24,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(
                f"Treine todo o plantel de uma só vez! Custo: {CUSTO_TREINO_ELENCO} 💎", size=13, color=ft.colors.GREY_400),
        ]),
        ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.DIAMOND,
                            color=ft.colors.CYAN_300, size=22),
                    saldo_diamantes_text
                ], spacing=5),
                bgcolor="#1E293B", padding=10, border_radius=10, border=ft.border.all(1, ft.colors.CYAN_500)
            ),
            ft.ElevatedButton("Voltar ao Hub", icon=ft.icons.ARROW_BACK,
                              height=45, on_click=lambda e: ao_voltar_hub(id_usuario))
        ], spacing=15)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=950)

    # --- PAINEL DE BOTÕES DE TREINO COLETIVO ---
    pode_treinar_elenco = (diamantes >= CUSTO_TREINO_ELENCO)

    btn_fisico = ft.ElevatedButton(
        "⚡ Treino Físico (+1 VEL)",
        icon=ft.icons.FLASH_ON,
        disabled=not pode_treinar_elenco,
        bgcolor=ft.colors.BLUE_700 if pode_treinar_elenco else ft.colors.GREY_800,
        color=ft.colors.WHITE,
        height=45,
        on_click=lambda e: executar_treino_elenco(
            id_usuario, id_time, "FISICO", diamantes, recarrega_tela)
    )

    btn_tactico = ft.ElevatedButton(
        "🧠 Treino Tático (+1 PAS/DRI)",
        icon=ft.icons.PSYCHOLOGY,
        disabled=not pode_treinar_elenco,
        bgcolor=ft.colors.PURPLE_700 if pode_treinar_elenco else ft.colors.GREY_800,
        color=ft.colors.WHITE,
        height=45,
        on_click=lambda e: executar_treino_elenco(
            id_usuario, id_time, "TACTICO", diamantes, recarrega_tela)
    )

    btn_tecnico = ft.ElevatedButton(
        "🎯 Treino Técnico (+1 FIN/DEF)",
        icon=ft.icons.SPORTS_SOCCER,
        disabled=not pode_treinar_elenco,
        bgcolor=ft.colors.GREEN_700 if pode_treinar_elenco else ft.colors.GREY_800,
        color=ft.colors.WHITE,
        height=45,
        on_click=lambda e: executar_treino_elenco(
            id_usuario, id_time, "TECNICO", diamantes, recarrega_tela)
    )

    painel_treinos_coletivos = ft.Container(
        content=ft.Column([
            ft.Text("Escolha o Foco do Treino do Elenco:", size=16,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Row([btn_fisico, btn_tactico, btn_tecnico],
                   spacing=15, wrap=True)
        ], spacing=10),
        bgcolor="#1E293B",
        padding=15,
        border_radius=12,
        border=ft.border.all(1, ft.colors.CYAN_700),
        width=950
    )

    # --- LISTA VISUAL DOS JOGADORES ---
    def criar_card_visual(j):
        id_j, nome, pos, estrelas, vel, fin, dri, pas, def_stat = j
        is_gol = (pos == "GOL")

        l_fin = "RFL" if is_gol else "FIN"
        l_dri = "POS" if is_gol else "DRI"
        l_pas = "REP" if is_gol else "PAS"

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"[{pos}] {nome}", size=14, weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE, no_wrap=True),
                    ft.Text("⭐ " * estrelas, size=11)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color=ft.colors.GREY_800),
                ft.Row([
                    ft.Text(f"VEL: {vel}", size=11, color=ft.colors.GREY_300),
                    ft.Text(f"{l_fin}: {fin}", size=11,
                            color=ft.colors.GREY_300),
                    ft.Text(f"{l_dri}: {dri}", size=11,
                            color=ft.colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(f"{l_pas}: {pas}", size=11,
                            color=ft.colors.GREY_300),
                    ft.Text(f"DEF: {def_stat}", size=11,
                            color=ft.colors.GREY_300),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            width=220,
            padding=12,
            bgcolor="#1E293B",
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_800)
        )

    cards_jogadores = [criar_card_visual(j) for j in jogadores]

    grid_jogadores = ft.Row(
        controls=cards_jogadores,
        wrap=True,
        spacing=15,
        run_spacing=15,
        alignment=ft.MainAxisAlignment.START,
        width=950
    )

    conteudo_principal = ft.Column(
        controls=[
            header,
            msg_status,
            painel_treinos_coletivos,
            ft.Divider(color=ft.colors.GREY_800, height=20),
            ft.Text("📊 Elenco Atual:", size=18,
                    weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            grid_jogadores
        ],
        width=950,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(conteudo_principal)


if __name__ == "__main__":
    def main(page: ft.Page):
        carregar_academia(page, id_usuario=1,
                          ao_voltar_hub=lambda id_u: print("Voltar ao Hub"))

    ft.app(target=main)
