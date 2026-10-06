import math
import sqlite3
import flet as ft
import database
import gerador
import hub


def verificar_usuario_existente():
    """Verifica se já existe alguma conta/clube cadastrado no banco de dados."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios ORDER BY id ASC LIMIT 1")
        user = cursor.fetchone()
        conn.close()
        if user:
            return user[0]
    except sqlite3.OperationalError:
        conn.close()
    return None


def main(page: ft.Page):
    database.inicializar_banco()

    # --- VERIFICAÇÃO AUTOMÁTICA DE SESSÃO / USUÁRIO ---
    id_usuario_existente = verificar_usuario_existente()

    if id_usuario_existente:
        # Se já existe um usuário cadastrado, abre DIRETO no Hub!
        hub.carregar_hub(page, id_usuario_existente)
        return

    # --- SE NÃO EXISTIR USUÁRIO, CARREGA A TELA DE CRIAÇÃO ---
    page.title = "Criar o Teu Clube - FootManager"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#299B29"
    page.theme_mode = ft.ThemeMode.LIGHT

    cores = {
        "Azul": ft.colors.BLUE_700,
        "Vermelho": ft.colors.RED_700,
        "Preto": ft.colors.BLACK87,
        "Branco": ft.colors.WHITE,
        "Amarelo": ft.colors.AMBER,
        "Verde": ft.colors.GREEN_700,
        "Laranja": ft.colors.ORANGE_700,
        "Roxo": ft.colors.PURPLE_700
    }

    icones = {
        "Estrela": ft.icons.STAR_ROUNDED,
        "Escudo": ft.icons.SHIELD,
        "Raio": ft.icons.FLASH_ON,
        "Fogo": ft.icons.LOCAL_FIRE_DEPARTMENT,
        "Bola": ft.icons.SPORTS_SOCCER,
        "Medalha": ft.icons.MILITARY_TECH,
        "Coroa": ft.icons.WORKSPACE_PREMIUM,
        "Castelo": ft.icons.FORT
    }

    # Formatos com suporte a dimensões (largura, altura, border_radius_ext, border_radius_int, angulo)
    formatos = {
        "Clássico": (
            140, 160, 124, 144,
            ft.border_radius.only(
                bottom_left=70, bottom_right=70, top_left=10, top_right=10),
            ft.border_radius.only(
                bottom_left=62, bottom_right=62, top_left=6, top_right=6),
            0
        ),
        "Losango": (
            130, 130, 114, 114,
            ft.border_radius.all(16),
            ft.border_radius.all(10),
            math.pi / 4  # 45 graus
        ),
        "Redondo": (
            140, 140, 124, 124,
            ft.border_radius.all(70),
            ft.border_radius.all(62),
            0
        ),
        "Moderno": (
            140, 160, 124, 144,
            ft.border_radius.all(25),
            ft.border_radius.all(18),
            0
        ),
        "Gótico": (
            140, 160, 124, 144,
            ft.border_radius.only(
                bottom_left=25, bottom_right=25, top_left=50, top_right=50),
            ft.border_radius.only(
                bottom_left=18, bottom_right=18, top_left=42, top_right=42),
            0
        ),
        "Italiano": (
            140, 160, 124, 144,
            ft.border_radius.only(
                bottom_left=15, bottom_right=15, top_left=70, top_right=70),
            ft.border_radius.only(
                bottom_left=8, bottom_right=8, top_left=62, top_right=62),
            0
        )
    }

    def atualizar_escudo(e):
        miolo_escudo.bgcolor = cores[drop_cor1.value]

        listra1.bgcolor = cores[drop_cor2.value]
        listra2.bgcolor = cores[drop_cor2.value]
        listra3.bgcolor = cores[drop_cor2.value]

        escudo.bgcolor = cores[drop_cor3.value]

        icone_centro.color = cores[drop_cor4.value]
        icone_centro.name = icones[drop_icone.value]

        # Atualiza dimensões, bordas e rotações
        w_ext, h_ext, w_int, h_int, borda_ext, borda_int, angulo = formatos[drop_formato.value]

        escudo.width = w_ext
        escudo.height = h_ext
        escudo.border_radius = borda_ext
        escudo.rotate = ft.Rotate(angle=angulo)

        miolo_escudo.width = w_int
        miolo_escudo.height = h_int
        miolo_escudo.border_radius = borda_int

        # Desrotaciona o ícone para mantê-lo sempre em pé
        icone_centro.rotate = ft.Rotate(angle=-angulo)

        page.update()

    def salvar_clube(e):
        login_val = login_input.value.strip()
        nome_time_val = nome_input.value.strip()

        if not login_val or not nome_time_val:
            msg_status.value = "⚠️ Preenche o login e o nome do clube!"
            msg_status.color = ft.colors.RED_700
            page.update()
            return

        try:
            database.criar_usuario(login_val, f"{login_val}@email.com", "1234")

            conn = sqlite3.connect('meu_manager.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM usuarios WHERE login = ?", (login_val,))
            res = cursor.fetchone()
            conn.close()

            if res:
                id_user = res[0]
                gerador.criar_time_usuario(
                    id_usuario=id_user,
                    nome_time=nome_time_val,
                    cor_1=drop_cor1.value,
                    cor_2=drop_cor2.value,
                    cor_3=drop_cor3.value,
                    cor_4=drop_cor4.value
                )

                msg_status.value = "✅ Clube criado com sucesso! A carregar Hub..."
                msg_status.color = ft.colors.GREEN_700
                page.update()

                hub.carregar_hub(page, id_user)

        except Exception as err:
            msg_status.value = f"❌ Erro ao guardar clube: {err}"
            msg_status.color = ft.colors.RED_700
            page.update()

    opcoes_cores = [ft.dropdown.Option(c) for c in cores.keys()]
    opcoes_icones = [ft.dropdown.Option(i) for i in icones.keys()]
    opcoes_formatos = [ft.dropdown.Option(f) for f in formatos.keys()]

    drop_cor1 = ft.Dropdown(label="1ª Cor (Fundo)", value="Azul", options=opcoes_cores,
                            width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)
    drop_cor2 = ft.Dropdown(label="2ª Cor (Listras)", value="Vermelho", options=opcoes_cores,
                            width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)
    drop_cor3 = ft.Dropdown(label="3ª Cor (Borda)", value="Amarelo", options=opcoes_cores,
                            width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)
    drop_cor4 = ft.Dropdown(label="4ª Cor (Símbolo)", value="Branco", options=opcoes_cores,
                            width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)

    drop_icone = ft.Dropdown(label="Símbolo Central", value="Estrela", options=opcoes_icones,
                             width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)
    drop_formato = ft.Dropdown(label="Formato do Escudo", value="Clássico", options=opcoes_formatos,
                               width=200, color=ft.colors.BLACK, on_change=atualizar_escudo)

    login_input = ft.TextField(label="Nome de Treinador (Login)",
                               width=410, color=ft.colors.BLACK, border_color=ft.colors.GREY_400)
    nome_input = ft.TextField(label="Nome do Clube", width=410,
                              color=ft.colors.BLACK, border_color=ft.colors.GREY_400)

    listra1 = ft.Container(width=25, height=180, bgcolor=cores["Vermelho"])
    listra2 = ft.Container(width=25, height=180, bgcolor=cores["Vermelho"])
    listra3 = ft.Container(width=25, height=180, bgcolor=cores["Vermelho"])

    painel_listras = ft.Row([listra1, listra2, listra3],
                            spacing=30, alignment=ft.MainAxisAlignment.CENTER)

    icone_centro = ft.Icon(
        name=icones["Estrela"], size=50, color=cores["Branco"])

    w_e, h_e, w_i, h_i, borda_ext_i, borda_int_i, ang_i = formatos["Clássico"]

    miolo_escudo = ft.Container(
        content=ft.Stack([
            painel_listras,
            ft.Container(content=icone_centro, alignment=ft.alignment.center)
        ]),
        width=w_i,
        height=h_i,
        bgcolor=cores["Azul"],
        border_radius=borda_int_i,
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    escudo = ft.Container(
        content=miolo_escudo,
        width=w_e,
        height=h_e,
        bgcolor=cores["Amarelo"],
        padding=8,
        border_radius=borda_ext_i,
        alignment=ft.alignment.center,
        rotate=ft.Rotate(angle=ang_i),
        shadow=ft.BoxShadow(
            blur_radius=10, color=ft.colors.BLACK26, offset=ft.Offset(0, 5))
    )

    area_escudo = ft.Container(
        content=escudo,
        width=180,
        height=180,
        alignment=ft.alignment.center
    )

    msg_status = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)
    btn_salvar = ft.ElevatedButton(
        "Concluir e Criar Clube", icon=ft.icons.CHECK, on_click=salvar_clube, height=45)

    painel_direito = ft.Column([
        login_input,
        nome_input,
        ft.Row([drop_formato, drop_icone], spacing=10),
        ft.Row([drop_cor1, drop_cor2], spacing=10),
        ft.Row([drop_cor3, drop_cor4], spacing=10),
        ft.Container(height=10),
        btn_salvar,
        msg_status
    ])

    cartao_principal = ft.Container(
        content=ft.Row([area_escudo, painel_direito], spacing=40,
                       alignment=ft.MainAxisAlignment.CENTER),
        padding=40,
        bgcolor=ft.colors.WHITE,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLACK12)
    )

    page.add(cartao_principal)


if __name__ == "__main__":
    ft.app(target=main)
