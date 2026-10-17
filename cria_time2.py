import sqlite3
import flet as ft
import flet.canvas as cv
import database
import gerador
import hub
import escudos


def verificar_usuario_existente():
    """Verifica se já existe alguma conta/clube cadastrado no banco de dados."""
    conn = gerador.conectar_bd()
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
        hub.carregar_hub(page, id_usuario_existente)
        return

    # --- CONFIGURAÇÃO DA TELA DE CRIAÇÃO ---
    page.title = "Criar o Teu Clube - FootManager"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#0F172A"
    page.theme_mode = ft.ThemeMode.DARK

    def atualizar_escudo(e):
        canvas_escudo.shapes = escudos.gerar_escudo(
            drop_formato.value,
            gerador.obter_cor_flet(drop_cor1.value),
            gerador.obter_cor_flet(drop_cor2.value),
            gerador.obter_cor_flet(drop_cor3.value),
        )

        icone_centro.color = gerador.obter_cor_flet(drop_cor4.value)
        icone_centro.name = gerador.ICONES.get(
            drop_icone.value, ft.Icons.SPORTS_SOCCER)

        page.update()

    def salvar_clube(e):
        login_val = login_input.value.strip()
        nome_time_val = nome_input.value.strip()

        if not login_val or not nome_time_val:
            msg_status.value = "⚠️ Preenche o login e o nome do clube!"
            msg_status.color = ft.Colors.RED_400
            page.update()
            return

        try:
            database.criar_usuario(login_val, f"{login_val}@email.com", "1234")

            conn = gerador.conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM usuarios WHERE login = ?", (login_val,))
            res = cursor.fetchone()
            conn.close()

            if res:
                id_user = res[0]

                # SALVAMENTO COMPLETO: Passa formato e simbolo para persistência no banco
                gerador.criar_time_usuario(
                    id_usuario=id_user,
                    nome_time=nome_time_val,
                    cor_1=drop_cor1.value,
                    cor_2=drop_cor2.value,
                    cor_3=drop_cor3.value,
                    cor_4=drop_cor4.value,
                    formato=drop_formato.value,
                    simbolo=drop_icone.value
                )

                msg_status.value = "✅ Clube criado com sucesso! A carregar Hub..."
                msg_status.color = ft.Colors.GREEN_400
                page.update()

                hub.carregar_hub(page, id_user)

        except Exception as err:
            msg_status.value = f"❌ Erro ao guardar clube: {err}"
            msg_status.color = ft.Colors.RED_400
            page.update()

    opcoes_cores = [ft.dropdown.Option(c) for c in gerador.LISTA_CORES]
    opcoes_icones = [ft.dropdown.Option(i) for i in gerador.LISTA_SIMBOLOS]
    opcoes_formatos = [ft.dropdown.Option(f) for f in escudos.FORMATOS]

    drop_cor1 = ft.Dropdown(label="1ª Cor (Fundo)", value="Azul", options=opcoes_cores,
                            width=200, on_change=atualizar_escudo)
    drop_cor2 = ft.Dropdown(label="2ª Cor (Listras)", value="Vermelho", options=opcoes_cores,
                            width=200, on_change=atualizar_escudo)
    drop_cor3 = ft.Dropdown(label="3ª Cor (Borda)", value="Amarelo", options=opcoes_cores,
                            width=200, on_change=atualizar_escudo)
    drop_cor4 = ft.Dropdown(label="4ª Cor (Símbolo)", value="Branco", options=opcoes_cores,
                            width=200, on_change=atualizar_escudo)

    drop_icone = ft.Dropdown(label="Símbolo Central", value="Estrela", options=opcoes_icones,
                             width=200, on_change=atualizar_escudo)
    drop_formato = ft.Dropdown(label="Formato do Escudo", value="Clássico", options=opcoes_formatos,
                               width=200, on_change=atualizar_escudo)

    login_input = ft.TextField(label="Nome de Treinador (Login)", width=410)
    nome_input = ft.TextField(label="Nome do Clube", width=410)

    icone_centro = ft.Icon(
        name=gerador.ICONES["Estrela"], size=50, color=gerador.obter_cor_flet("Branco")
    )

    canvas_escudo = cv.Canvas(
        shapes=escudos.gerar_escudo(
            "Clássico",
            gerador.obter_cor_flet("Azul"),
            gerador.obter_cor_flet("Vermelho"),
            gerador.obter_cor_flet("Amarelo")
        ),
        width=escudos.LARGURA,
        height=escudos.ALTURA,
    )

    area_escudo = ft.Container(
        width=180,
        height=180,
        alignment=ft.alignment.center,
        content=ft.Container(
            width=escudos.LARGURA,
            height=escudos.ALTURA,
            content=ft.Stack([
                canvas_escudo,
                ft.Container(
                    content=icone_centro,
                    width=escudos.LARGURA,
                    height=escudos.ALTURA,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=18),
                ),
            ]),
        ),
    )

    msg_status = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)
    btn_salvar = ft.ElevatedButton(
        "Concluir e Criar Clube", icon=ft.Icons.CHECK, on_click=salvar_clube, height=45
    )

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
        bgcolor="#1E293B",
        border_radius=20,
        border=ft.border.all(1, "#334155"),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK54)
    )

    page.add(cartao_principal)


if __name__ == "__main__":
    ft.app(target=main)
