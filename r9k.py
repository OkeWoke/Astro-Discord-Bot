import sqlite3
import threading
import database
import hashlib

class R9K:
    def __init__(self):
        self.mutex = threading.Lock()
        self.cache = set()

        c = database.get_connection().cursor()
        c.execute("CREATE TABLE IF NOT EXISTS message (hash text)")

        rows = c.execute('SELECT * FROM message')
        for row in rows:
            self.cache.add(row[0])
        c.close()

    async def handle_message(self, bot, message):
        if len(message.content) == 0:
            return

        h = hashlib.sha256(message.content.encode('utf-8')).hexdigest()
        self.mutex.acquire()
        try:
            if h in self.cache:
                await message.delete()
            else:
                c = database.get_connection().cursor()
                c.execute('INSERT INTO message (hash) VALUES (?)', (h,))
                c.close()
                self.cache.add(h)
        finally:
            self.mutex.release()
