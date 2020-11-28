import sqlite3
import threading
import database
import hashlib

class R9K:
    def __init__(self):
        self.mutex = threading.Lock()
        self.cache = set()
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS message (hash text)")

        rows = c.execute('SELECT * FROM message')
        for row in rows:
            self.cache.add(row[0])
        conn.commit()
        conn.close()

    async def handle_message(self, bot, message):
        if len(message.content) == 0:
            return

        h = hashlib.sha256(message.content.lower().encode('utf-8')).hexdigest()
        should_delete = False
        self.mutex.acquire()
        try:
            if h in self.cache:
                should_delete = True
            else:
                conn = database.get_connection()
                c = conn.cursor()
                c.execute('INSERT INTO message (hash) VALUES (?)', (h,))
                conn.commit()
                conn.close()
                self.cache.add(h)
        finally:
            self.mutex.release()
        if should_delete:
            await message.delete(delay=0.5)
