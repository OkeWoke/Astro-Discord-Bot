import sqlite3
import threading
import database
import hashlib

class R9K:
    def __init__(self):
        self.mutex = threading.Lock()
        self.database = database.get_connection()
        self.cache = set()

        c = self.database.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS message (hash text)")

        rows = c.execute('SELECT * FROM message')
        for row in rows:
            self.cache.add(row[0])
        c.close()

    def handle_message(self, bot, message):
        t = threading.Thread(target=self.process, args=(bot,message,))
        t.start()

    def process(self, bot, message):
        if len(message.content) == 0:
            return

        h = hashlib.sha256(message.content.encode('utf-8')).hexdigest()
        self.mutex.acquire()
        try:
            if h in self.cache:
                bot.delete_message(message)
            else:
                c = self.database.cursor()
                c.execute('INSERT INTO message (hash) VALUES (?)', (h,))
                c.close()
                self.cache.add(h)
        finally:
            self.mutex.release()
