import asyncpg
import os
from typing import Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._db_config = {
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'istz22'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'min_size': 2,
            'max_size': 10,
            'command_timeout': 30
        }

    async def connect(self) -> None:
        """Создает пул соединений с базой данных"""
        try:
            self.pool = await asyncpg.create_pool(**self._db_config)
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise

    async def close(self) -> None:
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def init_db(self) -> None:
        """Инициализирует структуру базы данных"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS students (
                        id BIGSERIAL PRIMARY KEY,
                        tg_id BIGINT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        phone TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')

                # Добавляем индексы для оптимизации
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_students_tg_id 
                    ON students(tg_id)
                ''')

                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS schedule (
                        id SERIAL PRIMARY KEY,
                        day_of_week VARCHAR(20) NOT NULL,
                        num_subject SMALLINT NOT NULL CHECK (num_subject BETWEEN 1 AND 8),
                        subject_name VARCHAR(100) NOT NULL,
                        room_number VARCHAR(20),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')

                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_schedule_day 
                    ON schedule(day_of_week)
                ''')

                # Остальные таблицы с аналогичными улучшениями...

                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


# Singleton instance
db = Database()