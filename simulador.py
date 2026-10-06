import sqlite3
import random


def carregar_forca_do_time(id_time):
    """Lê os 11 titulares da equipa e calcula a força dos setores."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    cursor.execute('SELECT nome FROM times WHERE id = ?', (id_time,))
    nome_res = cursor.fetchone()
    nome = nome_res[0] if nome_res else "Time Desconhecido"

    cursor.execute(
        'SELECT velocidade, finalizacao, drible, passe, defesa FROM jogadores WHERE id_time = ? AND titular = 1', (id_time,))
    jogadores = cursor.fetchall()
    conn.close()

    if not jogadores:
        return {"nome": nome, "ataque": 0, "meio": 0, "defesa": 0, "gols": 0}

    ataque = sum(j[0] + j[1] for j in jogadores)
    meio = sum(j[2] + j[3] for j in jogadores)
    defesa = sum(j[4] for j in jogadores)

    return {"nome": nome, "ataque": ataque, "meio": meio, "defesa": defesa, "gols": 0}


def calcular_posse_base(meio_casa, meio_fora):
    """
    Calcula uma estimativa de posse de bola realista baseada no meio-campo.
    Aplica limites normais do futebol (28% a 72%).
    """
    total = max(1, meio_casa + meio_fora)
    proporcao = meio_casa / total

    # Mapeia a proporção em torno de 50% com margem controlada
    base = 50 + (proporcao - 0.5) * 36
    posse_casa = int(max(28, min(72, base)))
    return posse_casa, 100 - posse_casa


def simular_partida(id_time_casa, id_time_fora):
    """Roda a partida rápida (backend/torneio) baseada na força das equipas."""
    casa = carregar_forca_do_time(id_time_casa)
    fora = carregar_forca_do_time(id_time_fora)

    for _ in range(10):
        poder_meio_total = max(1, casa['meio'] + fora['meio'])
        is_casa = random.randint(1, poder_meio_total) <= casa['meio']

        atacante = casa if is_casa else fora
        defensor = fora if is_casa else casa

        forca_chute = atacante['ataque'] + random.randint(0, 100)
        forca_bloqueio = (defensor['defesa'] * 1.3) + random.randint(0, 100)

        if forca_chute > forca_bloqueio:
            if random.random() > 0.52:
                atacante['gols'] += 1

    return casa['gols'], fora['gols']


def processar_recompensas(id_usuario, id_time_user, gols_casa, gols_fora):
    """Calcula moedas, EXP e Diamantes após a partida."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    if gols_casa > gols_fora:
        moedas_ganhas = 500
        exp_ganha = 150
    elif gols_casa == gols_fora:
        moedas_ganhas = 300
        exp_ganha = 75
    else:
        moedas_ganhas = 200
        exp_ganha = 30

    cursor.execute("""
        SELECT COALESCE(u.nivel, 1), COALESCE(u.exp, 0), COALESCE(u.diamantes, 0), COALESCE(t.moedas_free, 0)
        FROM usuarios u
        LEFT JOIN times t ON t.id_usuario = u.id
        WHERE u.id = ?
    """, (id_usuario,))

    dados = cursor.fetchone()
    if not dados:
        conn.close()
        return {
            "moedas_ganhas": moedas_ganhas,
            "exp_ganha": exp_ganha,
            "subiu_de_nivel": False,
            "novo_nivel": 1,
            "diamantes_ganhos": 0
        }

    nivel_atual, exp_atual, diamantes_atuais, moedas_atuais = dados

    novas_moedas = moedas_atuais + moedas_ganhas
    nova_exp = exp_atual + exp_ganha

    exp_necessaria = nivel_atual * 100
    subiu_de_nivel = False
    diamantes_ganhos = 0

    while nova_exp >= exp_necessaria:
        nova_exp -= exp_necessaria
        nivel_atual += 1
        diamantes_atuais += 50
        diamantes_ganhos += 50
        exp_necessaria = nivel_atual * 100
        subiu_de_nivel = True

    cursor.execute("""
        UPDATE usuarios 
        SET nivel = ?, exp = ?, diamantes = ? 
        WHERE id = ?
    """, (nivel_atual, nova_exp, diamantes_atuais, id_usuario))

    cursor.execute("""
        UPDATE times 
        SET moedas_free = ? 
        WHERE id_usuario = ?
    """, (novas_moedas, id_usuario))

    conn.commit()
    conn.close()

    return {
        "moedas_ganhas": moedas_ganhas,
        "exp_ganha": exp_ganha,
        "subiu_de_nivel": subiu_de_nivel,
        "novo_nivel": nivel_atual,
        "diamantes_ganhos": diamantes_ganhos
    }
