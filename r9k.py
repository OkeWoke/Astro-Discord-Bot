import sqlite3
import threading
import database
import hashlib
from PIL import Image

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

        # Check for text in message
        h = hashlib.sha256(message.content.lower().encode('utf-8')).hexdigest()
        h_exists = h in self.cache
        # Check for image attached to message
        img_h = None
        img_h_exists = False
        if message.attachments != []:
            file = message.attachments[0]
            if file.filename[file.filename.rfind("."):] in [".jpg",".JPG",".png",".PNG",".gif",".GIF"]:
                # Discord API Attachment.read() returns bytes
                file_bytes = await file.read()
                img_h = hashlib.sha256(file_bytes.hexdigest())
                img_h_exists = img_h in self.cache
        should_delete = False
        self.mutex.acquire()
        try:
            if h_exists or img_h_exists:
                should_delete = True
            else:
                conn = database.get_connection()
                c = conn.cursor()
                # All the new hashes
                new_hashes = [msg_hash for msg_hash in [h, img_h] if msg_hash is not None]
                for new_hash in new_hashes:
                    c.execute('INSERT INTO message (hash) VALUES (?)', (new_hash,))
                    conn.commit()
                    self.cache.add(h)
                conn.close()
        finally:
            self.mutex.release()
        if should_delete:
            await message.delete(delay=0.5)
