import asyncpg
import os

async def connect_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))

async def create_users_table():
    conn = await connect_db()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            style TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
async def save_user_style(user_id, username, style):
    conn = await connect_db()
    await conn.execute('''
        INSERT INTO users (user_id, username, style)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO UPDATE SET style = $3
    ''', user_id, username, style)
async def get_user_style(user_id):
    conn = await connect_db()
    row = await conn.fetchrow('SELECT style FROM users WHERE user_id = $1', user_id)
    await conn.close()
    return row['style'] if row else None
