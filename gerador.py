import sqlite3
import random
import flet as ft

NOMES_TIMES = [
    "Real Vila", "Inter do Vale", "União Central", "Atlético Campestre",
    "Estrela do Norte", "Sporting Litoral", "Cruzeiro do Sul", "Guarani Urbano",
    "Académica FC", "Imperial FC", "Vanguardas SC", "FC Metropolitano", "So kanela FC",
    "Lobos da Serra", "Dragões do Oeste", "Falcões do Norte", "Tigres do Sul",
    "Batinga FC", "Sao Thome FC"
]

NOMES_JOGADORES = [
    "Gabriel", "Lucas", "Matheus", "Pedro", "Enzo", "João", "Felipe", "Bruno",
    "Thiago", "Rodrigo", "Rafael", "Gustavo", "Vinicius", "Caio", "Daniel",
    "Murilo", "Vitor", "Diego", "Gerson", "Leandro", "André", "Marcelo",
    "Fábio", "Renan", "Cauã", "Davi", "Samuel", "Emanuel", "Hugo", "Wallace",
    "César", "Alex", "Wesley", "Iago", "Nathan", "Luan", "Rômulo", "Elias",
    "Bruno Henrique", "Jean", "Ruan", "Pablo", "Carlos", "Vinícius", "Luiz", "Rafael", "Guilherme", "Fernando", "Levi"
]

SOBRENOMES_JOGADORES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Costa",
    "Pereira", "Carvalho", "Rosa", "Almeida", "Mendes", "Ribeiro", "Barbosa",
    "Cardoso", "Moura", "Teixeira", "Campos", "Nunes", "Gomes", "Martins", "Rocha", "Dias", "Freitas", "Cavalcante", "Azevedo", "Monteiro",
]

LISTA_CORES = ["Azul", "Vermelho", "Preto",
               "Branco", "Amarelo", "Verde", "Laranja", "Roxo"]

# Aliases de compatibilidade para a loja.py
NOMES = NOMES_JOGADORES
SOBRENOMES = SOBRENOMES_JOGADORES

# Mapeamento de nomes de cores para cores do Flet
MAPA_CORES = {
    "Azul": ft.Colors.BLUE_700,
    "Vermelho": ft.Colors.RED_700,
    "Preto": ft.Colors.BLACK87,
    "Branco": ft.Colors.WHITE,
    "Amarelo": ft.Colors.AMBER_400,
    "Verde": ft.Colors.GREEN_700,
    "Laranja": ft.Colors.ORANGE_700,
    "Roxo": ft.Colors.PURPLE_700
}


def obter_cor_flet(cor_str):
    """Converte o nome da cor ou hex num valor de cor válido do Flet."""
    if not cor_str:
        return ft.Colors.BLUE_700
    if isinstance(cor_str, str) and cor_str in MAPA_CORES:
        return MAPA_CORES[cor_str]
    return cor_str


def criar_escudo_time(sigla="FC", cor_principal="Azul", cor_secundaria="Vermelho", cor_borda="Amarelo", cor_texto="Branco", tamanho=75):
    """
    🛡️ Cria e devolve o componente visual (ft.Container) do escudo do clube.
    Aplica as 4 cores configuradas no registo da equipa.
    """
    c1 = obter_cor_flet(cor_principal)
    c2 = obter_cor_flet(cor_secundaria)
    c3 = obter_cor_flet(cor_borda)
    c_txt = obter_cor_flet(cor_texto)

    largura = tamanho
    altura = int(tamanho * 1.15)
    tamanho_fonte = int(tamanho * 0.32)

    return ft.Container(
        content=ft.Stack([
            # Listras do Fundo
            ft.Row([
                ft.Container(width=int(largura * 0.28),
                             height=altura, bgcolor=c2),
                ft.Container(width=int(largura * 0.28),
                             height=altura, bgcolor=c1),
                ft.Container(width=int(largura * 0.28),
                             height=altura, bgcolor=c2),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),

            # Sigla / Nome do Clube
            ft.Container(
                content=ft.Text(
                    sigla[:3].upper(),
                    size=tamanho_fonte,
                    weight=ft.FontWeight.BOLD,
                    color=c_txt
                ),
                alignment=ft.alignment.center
            )
        ]),
        width=largura,
        height=altura,
        bgcolor=c1,
        padding=2,
        border=ft.border.all(max(2, int(tamanho * 0.05)), c3),
        border_radius=ft.border_radius.only(
            bottom_left=int(largura * 0.45),
            bottom_right=int(largura * 0.45),
            top_left=int(largura * 0.1),
            top_right=int(largura * 0.1)
        ),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        alignment=ft.alignment.center
    )


def sortear_cores():
    """Retorna uma tupla com 4 cores sorteadas aleatoriamente."""
    return (
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES),
        random.choice(LISTA_CORES)
    )


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


def gerar_elenco(id_time, nivel_base=1):
    """Gera um plantel de 18 jogadores com teto de 99 nos atributos e estrelas dinâmicas."""
    elenco = []
    distribuicao = ['GOL', 'GOL', 'ZAG', 'ZAG', 'ZAG', 'ZAG', 'ZAG', 'ZAG',
                    'MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'ATA', 'ATA', 'ATA', 'ATA']

    for posicao in distribuicao:
        nome = f"{random.choice(NOMES_JOGADORES)} {random.choice(SOBRENOMES_JOGADORES)}"

        if posicao == 'GOL':
            vel = random.randint(nivel_base * 10, nivel_base * 20)
            fin = random.randint(nivel_base * 15, nivel_base * 30)
            dri = random.randint(nivel_base * 10, nivel_base * 25)
            pas = random.randint(nivel_base * 10, nivel_base * 20)
            defesa = random.randint(nivel_base * 15, nivel_base * 35)
        else:
            vel = random.randint(nivel_base * 10, nivel_base * 25)
            fin = random.randint(nivel_base * 10, nivel_base * 25)
            dri = random.randint(nivel_base * 10, nivel_base * 25)
            pas = random.randint(nivel_base * 10, nivel_base * 25)
            defesa = random.randint(
                nivel_base * 10, nivel_base * 35) if posicao == 'ZAG' else random.randint(nivel_base * 5, nivel_base * 15)

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


def gerar_time_torneio(nome_time, estrelas):
    """Gera um time BOT para torneios com 11 titulares e cores aleatórias."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    c1, c2, c3, c4 = sortear_cores()

    cursor.execute("""
        INSERT INTO times (nome, is_bot, cor_1, cor_2, cor_3, cor_4, moedas_free, moedas_missao)
        VALUES (?, 1, ?, ?, ?, ?, 0, 0)
    """, (nome_time, c1, c2, c3, c4))

    id_time = cursor.lastrowid

    min_stat = 40 + (estrelas * 8)
    max_stat = 50 + (estrelas * 8)

    posicoes = ["GOL", "DEF", "DEF", "DEF", "DEF",
                "MEI", "MEI", "MEI", "ATA", "ATA", "ATA"]

    for pos in posicoes:
        nome_j = f"{random.choice(NOMES_JOGADORES)} {random.choice(SOBRENOMES_JOGADORES)}"
        vel = min(random.randint(min_stat, max_stat), 99)
        fin = min(random.randint(min_stat, max_stat), 99)
        dri = min(random.randint(min_stat, max_stat), 99)
        pas = min(random.randint(min_stat, max_stat), 99)
        dfe = min(random.randint(min_stat, max_stat), 99)

        cursor.execute("""
            INSERT INTO jogadores (id_time, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
        """, (id_time, nome_j, pos, estrelas, vel, fin, dri, pas, dfe))

    conn.commit()
    conn.close()
    return id_time


def criar_time_usuario(id_usuario, nome_time, cor_1="Azul", cor_2="Vermelho", cor_3="Amarelo", cor_4="Branco"):
    """Cria a equipa do jogador com moedas e 18 jogadores iniciais."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO times (id_usuario, nome, is_bot, cor_1, cor_2, cor_3, cor_4, moedas_free, moedas_missao) 
        VALUES (?, ?, 0, ?, ?, ?, ?, 1000, 50)
    ''', (id_usuario, nome_time, cor_1, cor_2, cor_3, cor_4))

    id_time = cursor.lastrowid
    jogadores = gerar_elenco(id_time, nivel_base=1)

    cursor.executemany('''
        INSERT INTO jogadores (id_time, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jogadores)

    conn.commit()
    conn.close()
    print(f"✅ Equipa '{nome_time}' criada com sucesso!")


def criar_time_bot(nome_time, nivel_estrelas=1):
    """Cria uma equipa BOT completa com cores aleatórias para partidas amistosas/simulações."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    c1, c2, c3, c4 = sortear_cores()

    cursor.execute('''
        INSERT INTO times (id_usuario, nome, is_bot, cor_1, cor_2, cor_3, cor_4) 
        VALUES (NULL, ?, 1, ?, ?, ?, ?)
    ''', (nome_time, c1, c2, c3, c4))

    id_time = cursor.lastrowid
    jogadores = gerar_elenco(id_time, nivel_base=nivel_estrelas)

    cursor.executemany('''
        INSERT INTO jogadores (id_time, nome, posicao, titular, estrelas, velocidade, finalizacao, drible, passe, defesa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jogadores)

    conn.commit()
    conn.close()
    print(f"🤖 BOT '{nome_time}' criado com cores aleatórias!")
