import sqlite3

LOCAL_DB_PATH = 'data.db'

def get_db_connection():
    """Connexion à la base de données SQLite"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Active les foreign keys
    return conn

def init_db():
    """Initialise la base de données SQLite"""
    conn = get_db_connection()
    c = conn.cursor()

    # Table des joueurs
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            elo_standard REAL DEFAULT 500,
            elo_with_score REAL DEFAULT 500,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table des matchs
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER NOT NULL,
            score1 INTEGER NOT NULL,
            score2 INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player1_id) REFERENCES players(id) ON DELETE CASCADE,
            FOREIGN KEY (player2_id) REFERENCES players(id) ON DELETE CASCADE
        )
    """)
    
    # Historique avec CASCADE activé
    c.execute("""
        CREATE TABLE IF NOT EXISTS match_elo_changes (
            match_id INTEGER PRIMARY KEY,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER NOT NULL,
            p1_elo_standard_before REAL NOT NULL,
            p1_elo_with_score_before REAL NOT NULL,
            p1_change_standard REAL NOT NULL,
            p1_change_with_score REAL NOT NULL,
            p2_elo_standard_before REAL NOT NULL,
            p2_elo_with_score_before REAL NOT NULL,
            p2_change_standard REAL NOT NULL,
            p2_change_with_score REAL NOT NULL,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player1_id) REFERENCES players(id) ON DELETE CASCADE,
            FOREIGN KEY (player2_id) REFERENCES players(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] DB initialisée")