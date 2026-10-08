import math
import os
import random
import sqlite3
import sys
import flet as ft


def obter_caminho_bd():
    """
    Retorna o caminho do banco de dados compatível com Windows, Mac, Linux e Android.
    """
    nome_bd = 'meu_manager.db'

    flet_storage = os.environ.get("FLET_APP_STORAGE_DATA")
    android_private = os.environ.get("ANDROID_PRIVATE")

    if flet_storage:
        os.makedirs(flet_storage, exist_ok=True)
        return os.path.join(flet_storage, nome_bd)
    elif android_private:
        os.makedirs(android_private, exist_ok=True)
        return os.path.join(android_private, nome_bd)

    if "ANDROID_ARGUMENT" in os.environ or hasattr(sys, "getandroidapilevel"):
        pasta_home = os.path.expanduser("~")
        return os.path.join(pasta_home, nome_bd)

    return nome_bd


def conectar_bd():
    return sqlite3.connect(obter_caminho_bd())


def obter_coluna_id_times(cursor):
    """Detecta dinamicamente a chave primária da tabela 'times'."""
    cursor.execute("PRAGMA table_info(times)")
    colunas = [row[1] for row in cursor.fetchall()]
    if "id_time" in colunas:
        return "id_time"
    elif "id" in colunas:
        return "id"
    elif "id_clube" in colunas:
        return "id_clube"
    return "rowid"


def obter_coluna_fk_jogadores(cursor):
    """Detecta dinamicamente a chave estrangeira na tabela 'jogadores'."""
    cursor.execute("PRAGMA table_info(jogadores)")
    colunas = [row[1] for row in cursor.fetchall()]
    if "id_time" in colunas:
        return "id_time"
    elif "time_id" in colunas:
        return "time_id"
    elif "id_clube" in colunas:
        return "id_clube"
    return "id_time"


# --- LISTAS DE DADOS E NOMES ---
NOMES_TIMES = [
    "Real Vila", "Inter do Vale", "União Central", "Atlético Campestre",
    "Estrela do Norte", "Sporting Litoral", "Cruzeiro do Sul", "Guarani Urbano",
    "Académica FC", "Imperial FC", "Vanguardas SC", "FC Metropolitano", "So kanela FC",
    "Lobos da Serra", "Dragões do Oeste", "Falcões do Norte", "Tigres do Sul",
    "Batinga FC", "Sao Thome FC", "Flamengo", "Palmeiras", "São Paulo"
]

NOMES_JOGADORES = [
    "Gabriel", "Lucas", "Matheus", "Pedro", "Enzo", "João", "Felipe", "Bruno",
    "Thiago", "Rodrigo", "Rafael", "Gustavo", "Vinicius", "Caio", "Daniel",
    "Murilo", "Vitor", "Diego", "Gerson", "Leandro", "André", "Marcelo", "Jonathan",
    "Fábio", "Renan", "Cauã", "Davi", "Samuel", "Emanuel", "Hugo", "Wallace",
    "César", "Alex", "Wesley", "Iago", "Nathan", "Luan", "Rômulo", "Elias",
    "Bruno Henrique", "Jean", "Ruan", "Pablo", "Carlos", "Vinícius", "Luiz", "Rafael",
    "Guilherme", "Fernando", "Levi", "Zé"
]

SOBRENOMES_JOGADORES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Costa",
    "Pereira", "Carvalho", "Rosa", "Almeida", "Mendes", "Ribeiro", "Barbosa",
    "Cardoso", "Moura", "Teixeira", "Campos", "Nunes", "Gomes", "Martins", "Rocha",
    "Dias", "Freitas", "Cavalcante", "Azevedo", "Monteiro"
]

NOMES = NOMES_JOGADORES
SOBRENOMES = SOBRENOMES_JOGADORES

LISTA_CORES = ["Azul", "Vermelho", "Preto",
               "Branco", "Amarelo", "Verde", "Laranja", "Roxo"]
FORMATOS_ESCUDO = ["Clássico", "Losango",
                   "Redondo", "Moderno", "Gótico", "Italiano"]

MAPA_CORES = {
    "Azul": ft.Colors.BLUE_700,
    "Vermelho": ft.Colors.RED_700,
    "Preto": ft.Colors.BLACK87,
    "Branco": ft.Colors.WHITE,
    "Amarelo": ft.Colors.AMBER,
    "Verde": ft.Colors.GREEN_700,
    "Laranja": ft.Colors.ORANGE_700,
    "Roxo": ft.Colors.PURPLE_700
}
CORES = MAPA_CORES

ICONES = {
    "Estrela": ft.Icons.STAR_ROUNDED,
    "Escudo": ft.Icons.SHIELD,
    "Raio": ft.Icons.FLASH_ON,
    "Fogo": ft.Icons.LOCAL_FIRE_DEPARTMENT,
    "Bola": ft.Icons.SPORTS_SOCCER,
    "Medalha": ft.Icons.MILITARY_TECH,
    "Coroa": ft.Icons.WORKSPACE_PREMIUM,
    "Castelo": ft.Icons.FORT
}
LISTA_SIMBOLOS = list(ICONES.keys())


def garantir_colunas(cursor, conn=None):
    """Garante as colunas e atualiza permanentemente no BD os times que ficaram com 'Estrela'."""
    colunas = [
        ('formato', "'Clássico'"),
        ('simbolo', "'Estrela'"),
        ('escudo', "NULL"),
        ('cor_1', "'Azul'"),
        ('cor_2', "'Vermelho'"),
        ('cor_3', "'Amarelo'"),
        ('cor_4', "'Branco'")
    ]
    for col, default in colunas:
        try:
            cursor.execute(
                f"ALTER TABLE times ADD COLUMN {col} TEXT DEFAULT {default}")
        except sqlite3.OperationalError:
            pass

    col_id = obter_coluna_id_times(cursor)

    # Força a re-randomização e SALVA no BD todos os times que estão com 'Estrela' ou sem símbolo
    try:
        cursor.execute(
            f"SELECT {col_id} FROM times WHERE simbolo IS NULL OR simbolo = 'Estrela' OR simbolo = ''")
        bots = cursor.fetchall()
        for (id_t,) in bots:
            s_rand = random.choice(LISTA_SIMBOLOS)
            f_rand = random.choice(FORMATOS_ESCUDO)
            cursor.execute(
                f"UPDATE times SET simbolo = ?, formato = ? WHERE {col_id} = ?", (s_rand, f_rand, id_t))

        if conn:
            conn.commit()
        elif hasattr(cursor, 'connection') and cursor.connection:
            cursor.connection.commit()
    except Exception:
        pass


def obter_cor_flet(cor_str):
    if not cor_str:
        return ft.Colors.BLUE_700
    if isinstance(cor_str, str) and cor_str in MAPA_CORES:
        return MAPA_CORES[cor_str]
    return cor_str


def obter_formatos_escala(escala: float):
    return {
        "Clássico": (
            140 * escala, 160 * escala, 124 * escala, 144 * escala,
            ft.border_radius.only(
                bottom_left=70 * escala, bottom_right=70 * escala,
                top_left=10 * escala, top_right=10 * escala
            ),
            ft.border_radius.only(
                bottom_left=62 * escala, bottom_right=62 * escala,
                top_left=6 * escala, top_right=6 * escala
            ),
            0
        ),
        "Losango": (
            130 * escala, 130 * escala, 114 * escala, 114 * escala,
            ft.border_radius.all(16 * escala),
            ft.border_radius.all(10 * escala),
            math.pi / 4
        ),
        "Redondo": (
            140 * escala, 140 * escala, 124 * escala, 124 * escala,
            ft.border_radius.all(70 * escala),
            ft.border_radius.all(62 * escala),
            0
        ),
        "Moderno": (
            140 * escala, 160 * escala, 124 * escala, 144 * escala,
            ft.border_radius.all(25 * escala),
            ft.border_radius.all(18 * escala),
            0
        ),
        "Gótico": (
            140 * escala, 160 * escala, 124 * escala, 144 * escala,
            ft.border_radius.only(
                bottom_left=25 * escala, bottom_right=25 * escala,
                top_left=50 * escala, top_right=50 * escala
            ),
            ft.border_radius.only(
                bottom_left=18 * escala, bottom_right=18 * escala,
                top_left=42 * escala, top_right=42 * escala
            ),
            0
        ),
        "Italiano": (
            140 * escala, 160 * escala, 124 * escala, 144 * escala,
            ft.border_radius.only(
                bottom_left=15 * escala, bottom_right=15 * escala,
                top_left=70 * escala, top_right=70 * escala
            ),
            ft.border_radius.only(
                bottom_left=8 * escala, bottom_right=8 * escala,
                top_left=62 * escala, top_right=62 * escala
            ),
            0
        )
    }


def criar_escudo_time(
    formato="Losango",
    simbolo=None,
    cor_principal="Azul",
    cor_secundaria="Vermelho",
    cor_borda="Amarelo",
    cor_texto="Branco",
    tamanho=140,
    **kwargs
):
    formato = kwargs.get('formato', kwargs.get('escudo_formato', formato))
    simbolo = kwargs.get('simbolo', kwargs.get('icone', kwargs.get(
        'simbolo_escudo', kwargs.get('simbolo_time', simbolo))))

    cor_principal = kwargs.get('cor_1', kwargs.get('c1', cor_principal))
    cor_secundaria = kwargs.get('cor_2', kwargs.get('c2', cor_secundaria))
    cor_borda = kwargs.get('cor_3', kwargs.get('c3', cor_borda))
    cor_texto = kwargs.get('cor_4', kwargs.get('c4', cor_texto))

    # Caso venha sem símbolo ou seja o símbolo genérico 'Estrela', sorteia um ícone variado
    if not simbolo or simbolo == "Estrela" or simbolo not in ICONES:
        simbolo = random.choice(
            [s for s in LISTA_SIMBOLOS if s != "Estrela"] or LISTA_SIMBOLOS)

    bg_miolo = obter_cor_flet(cor_principal)
    bg_listras = obter_cor_flet(cor_secundaria)
    bg_borda = obter_cor_flet(cor_borda)
    color_icone = obter_cor_flet(cor_texto)

    icone_nome = ICONES.get(simbolo, ft.Icons.SPORTS_SOCCER)

    escala = tamanho / 140.0
    formatos = obter_formatos_escala(escala)

    fmt_chave = str(formato or "Losango")
    if fmt_chave not in formatos:
        fmt_chave = "Losango"

    w_ext, h_ext, w_int, h_int, borda_ext, borda_int, angulo = formatos[fmt_chave]

    listra1 = ft.Container(
        width=25 * escala, height=180 * escala, bgcolor=bg_listras)
    listra2 = ft.Container(
        width=25 * escala, height=180 * escala, bgcolor=bg_listras)
    listra3 = ft.Container(
        width=25 * escala, height=180 * escala, bgcolor=bg_listras)

    painel_listras = ft.Row(
        [listra1, listra2, listra3],
        spacing=30 * escala,
        alignment=ft.MainAxisAlignment.CENTER
    )

    icone_centro = ft.Icon(
        name=icone_nome,
        size=50 * escala,
        color=color_icone,
        rotate=ft.Rotate(angle=-angulo)
    )

    miolo_escudo = ft.Container(
        content=ft.Stack([
            painel_listras,
            ft.Container(content=icone_centro, alignment=ft.alignment.center)
        ]),
        width=w_int,
        height=h_int,
        bgcolor=bg_miolo,
        border_radius=borda_int,
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    escudo = ft.Container(
        content=miolo_escudo,
        width=w_ext,
        height=h_ext,
        bgcolor=bg_borda,
        padding=8 * escala,
        border_radius=borda_ext,
        alignment=ft.alignment.center,
        rotate=ft.Rotate(angle=angulo),
        shadow=ft.BoxShadow(
            blur_radius=10 * escala, color=ft.Colors.BLACK26, offset=ft.Offset(0, 5 * escala)
        )
    )

    return ft.Container(
        content=escudo,
        width=180 * escala,
        height=180 * escala,
        alignment=ft.alignment.center
    )


def sortear_cores():
    return (
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES)
    )


def calcular_estrelas(media):
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


def gerar_elenco(id_time, nivel_base=1, **kwargs):
    nivel = kwargs.get('nivel_time', nivel_base)
    elenco = []
    distribuicao = ['GOL', 'GOL', 'ZAG', 'ZAG', 'ZAG', 'ZAG', 'ZAG', 'ZAG',
                    'MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'ATA', 'ATA', 'ATA', 'ATA']

    for posicao in distribuicao:
        nome = f"{random.choice(NOMES_JOGADORES)} {random.choice(SOBRENOMES_JOGADORES)}"

        if posicao == 'GOL':
            vel = random.randint(nivel * 10, nivel * 20)
            fin = random.randint(nivel * 15, nivel * 30)
            dri = random.randint(nivel * 10, nivel * 25)
            pas = random.randint(nivel * 10, nivel * 20)
            defesa = random.randint(nivel * 15, nivel * 35)
        else:
            vel = random.randint(nivel * 10, nivel * 25)
            fin = random.randint(nivel * 10, nivel * 25)
            dri = random.randint(nivel * 10, nivel * 25)
            pas = random.randint(nivel * 10, nivel * 25)
            defesa = random.randint(
                nivel * 10, nivel * 35) if posicao == 'ZAG' else random.randint(nivel * 5, nivel * 15)

            if posicao == 'ATA':
                fin += 15
            elif posicao == 'MEI':
                pas += 15
                dri += 10
            elif posicao == 'ZAG':
                defesa += 15

        vel = min(vel, 99)
        fin = min(fin, 99)
        dri = min(dri, 99)
        pas = min(pas, 99)
        defesa = min(defesa, 99)

        media = (vel + fin + dri + pas + defesa) / 5.0
        estrelas = calcular_estrelas(media)
        titular = 1 if len(elenco) < 11 else 0

        elenco.append((id_time, nome, posicao, titular,
                      estrelas, vel, fin, dri, pas, defesa))

    return elenco


def gerar_time_torneio(nome_time, estrelas_bot=1):
    conn = conectar_bd()
    cursor = conn.cursor()
    garantir_colunas(cursor, conn)

    col_fk = obter_coluna_fk_jogadores(cursor)
    c1, c2, c3, c4 = sortear_cores()
    formato_bot = random.choice(FORMATOS_ESCUDO)
    simbolo_bot = random.choice(LISTA_SIMBOLOS)

    cursor.execute("""
        INSERT INTO times (nome, formato, simbolo, is_bot, cor_1, cor_2, cor_3, cor_4, moedas_free, moedas_missao)
        VALUES (?, ?, ?, 1, ?, ?, ?, ?, 0, 0)
    """, (nome_time, formato_bot, simbolo_bot, c1, c2, c3, c4))

    id_time = cursor.lastrowid

    min_stat = 40 + (estrelas_bot * 8)
    max_stat = 50 + (estrelas_bot * 8)
    posicoes = ["GOL", "ZAG", "ZAG", "ZAG", "ZAG",
                "MEI", "MEI", "MEI", "ATA", "ATA", "ATA"]

    for pos in posicoes:
        nome_j = f"{random.choice(NOMES_JOGADORES)} {random.choice(SOBRENOMES_JOGADORES)}"
        vel = min(random.randint(min_stat, max_stat), 99)
        fin = min(random.randint(min_stat, max_stat), 99)
        dri = min(random.randint(min_stat, max_stat), 99)
        pas = min(random.randint(min_stat, max_stat), 99)
        dfe = min(random.randint(min_stat, max_stat), 99)

        cursor.execute(f"""
            INSERT INTO jogadores ({col_fk}, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
        """, (id_time, nome_j, pos, estrelas_bot, vel, fin, dri, pas, dfe))

    conn.commit()
    conn.close()
    return id_time


def criar_time_usuario(id_usuario, nome_time, cor_1="Azul", cor_2="Vermelho", cor_3="Amarelo", cor_4="Branco", formato="Clássico", simbolo="Bola", **kwargs):
    conn = conectar_bd()
    cursor = conn.cursor()
    garantir_colunas(cursor, conn)

    col_fk = obter_coluna_fk_jogadores(cursor)

    cursor.execute("""
        INSERT INTO times (id_usuario, nome, formato, simbolo, is_bot, cor_1, cor_2, cor_3, cor_4, moedas_free, moedas_missao)
        VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, 1000, 50)
    """, (id_usuario, nome_time, formato, simbolo, cor_1, cor_2, cor_3, cor_4))

    id_time = cursor.lastrowid

    jogadores = gerar_elenco(id_time, nivel_base=1)

    cursor.executemany(f"""
        INSERT INTO jogadores ({col_fk}, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, jogadores)

    conn.commit()
    conn.close()
    return id_time


def criar_time_bot(nome_time, nivel_estrelas=1):
    conn = conectar_bd()
    cursor = conn.cursor()
    garantir_colunas(cursor, conn)

    col_fk = obter_coluna_fk_jogadores(cursor)
    c1, c2, c3, c4 = sortear_cores()
    formato_bot = random.choice(FORMATOS_ESCUDO)
    simbolo_bot = random.choice(LISTA_SIMBOLOS)

    cursor.execute('''
        INSERT INTO times (id_usuario, nome, formato, simbolo, is_bot, cor_1, cor_2, cor_3, cor_4, moedas_free, moedas_missao) 
        VALUES (NULL, ?, ?, ?, 1, ?, ?, ?, ?, 0, 0)
    ''', (nome_time, formato_bot, simbolo_bot, c1, c2, c3, c4))

    id_time = cursor.lastrowid
    jogadores = gerar_elenco(id_time, nivel_base=nivel_estrelas)

    cursor.executemany(f'''
        INSERT INTO jogadores ({col_fk}, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jogadores)

    conn.commit()
    conn.close()
    return id_time
