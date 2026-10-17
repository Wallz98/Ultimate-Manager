import sqlite3
import hashlib


def inicializar_banco():
    """Inicializa a estrutura do banco de dados com suporte a formato, simbolo, escudo, energia, foto, diamantes e cores personalizadas."""
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')

    # 1. Tabela: Usuários (Com nivel, exp e diamantes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        nivel INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        diamantes INTEGER DEFAULT 0
    )
    ''')

    # 2. Tabela: Times (Com formato, simbolo, escudo e cores independentes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER, 
        nome TEXT NOT NULL,
        formato TEXT DEFAULT 'Clássico',
        simbolo TEXT DEFAULT 'Estrela',
        escudo TEXT DEFAULT NULL,
        is_bot BOOLEAN DEFAULT 0,
        cor_1 TEXT DEFAULT 'Azul',
        cor_2 TEXT DEFAULT 'Vermelho',
        cor_3 TEXT DEFAULT 'Amarelo',
        cor_4 TEXT DEFAULT 'Branco',
        nivel_estadio INTEGER DEFAULT 1,
        moedas_free INTEGER DEFAULT 0,
        moedas_missao INTEGER DEFAULT 0,
        id_patrocinador INTEGER DEFAULT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id) ON DELETE CASCADE
    )
    ''')

    # Migrações preventivas para a tabela 'times'
    colunas_novas_times = [
        ('formato', "TEXT DEFAULT 'Clássico'"),
        ('simbolo', "TEXT DEFAULT 'Estrela'"),
        ('escudo', "TEXT DEFAULT NULL"),
        ('cor_1', "TEXT DEFAULT 'Azul'"),
        ('cor_2', "TEXT DEFAULT 'Vermelho'"),
        ('cor_3', "TEXT DEFAULT 'Amarelo'"),
        ('cor_4', "TEXT DEFAULT 'Branco'")
    ]
    for col, tipo in colunas_novas_times:
        try:
            cursor.execute(f"ALTER TABLE times ADD COLUMN {col} {tipo}")
        except sqlite3.OperationalError:
            pass

    # 3. Tabela: Jogadores (com suporte a 'energia' e 'foto')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jogadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_time INTEGER,
        nome TEXT NOT NULL,
        posicao TEXT NOT NULL,
        titular BOOLEAN DEFAULT 0,
        estrelas INTEGER DEFAULT 1,
        velocidade INTEGER DEFAULT 10,
        finalizacao INTEGER DEFAULT 10,
        drible INTEGER DEFAULT 10,
        passe INTEGER DEFAULT 10,
        defesa INTEGER DEFAULT 10,
        energia INTEGER DEFAULT 100,
        foto TEXT DEFAULT NULL,
        FOREIGN KEY (id_time) REFERENCES times (id) ON DELETE CASCADE
    )
    ''')

    # Migrações preventivas para a tabela 'jogadores'
    colunas_novas_jogadores = [
        ('energia', "INTEGER DEFAULT 100"),
        ('foto', "TEXT DEFAULT NULL")
    ]
    for col, tipo in colunas_novas_jogadores:
        try:
            cursor.execute(f"ALTER TABLE jogadores ADD COLUMN {col} {tipo}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def criar_usuario(login, email, senha):
    """Cria um novo utilizador registando a password encriptada com SHA-256."""
    senha_criptografada = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO usuarios (login, email, senha_hash, nivel, exp, diamantes)
        VALUES (?, ?, ?, 1, 0, 50)
        ''', (login, email, senha_criptografada))
        conn.commit()
        print(f"✅ Utilizador '{login}' criado com sucesso!")
    except sqlite3.IntegrityError:
        print("⚠ Aviso: Este login ou e-mail já estão em uso.")
    finally:
        conn.close()


if __name__ == "__main__":
    inicializar_banco()
