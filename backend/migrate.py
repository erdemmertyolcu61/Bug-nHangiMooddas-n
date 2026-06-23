import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('movie_cache.db')
        conn.execute("ALTER TABLE quiz_rooms ADD COLUMN player_jokers TEXT DEFAULT '{}'")
        conn.commit()
        print("Migration done for movie_cache.db")
    except Exception as e:
        print("Migration error:", e)
    finally:
        conn.close()

migrate()
