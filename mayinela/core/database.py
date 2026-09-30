import aiosqlite
from pathlib import Path
from .config import settings

class Database:
    def __init__(self):
        self.path = settings.db_path

    async def init(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.path) as con:
            await con.execute('''
                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            await con.execute('''
                CREATE TABLE IF NOT EXISTS command_stats (
                    command TEXT PRIMARY KEY,
                    uses INTEGER NOT NULL DEFAULT 0
                )
            ''')
            await con.commit()

    async def inc(self, command):
        async with aiosqlite.connect(self.path) as con:
            await con.execute(
                'INSERT INTO command_stats(command, uses) VALUES(?,1) '
                'ON CONFLICT(command) DO UPDATE SET uses=uses+1',
                (command,)
            )
            await con.commit()

    async def get_stats(self):
        async with aiosqlite.connect(self.path) as con:
            cur = await con.execute(
                'SELECT command, uses FROM command_stats ORDER BY uses DESC'
            )
            return await cur.fetchall()

db = Database()
