try:
    import oracledb
    HAS_ORACLE = True
except ImportError:
    HAS_ORACLE = False
    oracledb = None

import logging
from app.core.config import settings

logger = logging.getLogger("database")

class OracleClient:
    def __init__(self):
        self.user = settings.ORACLE_USER
        self.password = settings.ORACLE_PASSWORD
        self.dsn = settings.ORACLE_DSN
        self.pool = None

    async def connect(self):
        if not HAS_ORACLE:
            logger.warning("python-oracledb not installed. Database features will be disabled (Mock Mode).")
            return

        try:
            self.pool = oracledb.create_pool(
                user=self.user,
                password=self.password,
                dsn=self.dsn,
                min=1,
                max=5,
                increment=1
            )
            logger.info("Oracle Database connection pool established.")
        except Exception as e:
            logger.error(f"Failed to connect to Oracle Database: {e}")

    async def close(self):
        if self.pool:
            self.pool.close()
            logger.info("Oracle Database connection pool closed.")

    def run_query(self, sql: str):
        if not HAS_ORACLE:
            return [{"mock_column": "Database Driver Missing - Mock Data"}]

        if not self.pool:
            raise Exception("Database not connected")
        
        with self.pool.acquire() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                # Convert to list of dicts
                return [dict(zip(columns, row)) for row in rows]

# Global instance
db_client = OracleClient()
