import sqlite3


def adicionar_colunas_nivel():
    conn = sqlite3.connect('meu_manager.db')
    cursor = conn.cursor()

    # Adiciona a coluna nivel se não existir
    try:
        cursor.execute("ALTER TABLE times ADD COLUMN nivel INTEGER DEFAULT 1;")
        print("✅ Coluna 'nivel' adicionada com sucesso.")
    except sqlite3.OperationalError:
        print("ℹ️ Coluna 'nivel' já existe.")

    # Adiciona a coluna exp se não existir
    try:
        cursor.execute("ALTER TABLE times ADD COLUMN exp INTEGER DEFAULT 0;")
        print("✅ Coluna 'exp' adicionada com sucesso.")
    except sqlite3.OperationalError:
        print("ℹ️ Coluna 'exp' já existe.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    adicionar_colunas_nivel()
