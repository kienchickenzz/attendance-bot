"""PostgreSQL connection pool with integrated query execution."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.abc import Query, Params

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Simple class to represent query result rows."""
    cells: Dict[str, Any]


class DbConnPool:
    """Database connection pool manager with integrated query execution."""

    def __init__(self, connection_url: Optional[str] = None ):
        """
        Initialize the database connection pool.
        
        Args:
            connection_url: PostgreSQL connection string (optional, can be set later)
        """
        self.connection_url = connection_url
        self.pool: AsyncConnectionPool | None = None

    async def connect( self, connection_url: Optional[ str ] = None ) -> AsyncConnectionPool:
        """
        Initialize and open the connection pool with retry logic.

        Args:
            connection_url: Optional connection URL to override the instance URL
        
        Returns:
            The connection pool instance
            
        Raises:
            ValueError: If connection fails or no URL provided
        """
        # Nếu đã có pool hợp lệ, trả về luôn để tránh tạo connection không cần thiết
        if self.pool:
            return self.pool
        
        url = connection_url or self.connection_url
        self.connection_url = url
        if not url:
            self._is_valid = False
            raise ValueError( "❌ Database connection URL not provided" )

        # Đóng pool cũ trước khi tạo mới (nếu có)
        await self.close()

        try:
            self.pool = AsyncConnectionPool(
                conninfo=url,
                min_size=1,        # Tối thiểu 1 connection để giảm overhead
                max_size=10,       # Tăng max_size để xử lý concurrent requests tốt hơn
                open=False,        # Không mở ngay, sẽ mở thủ công để kiểm soát tốt hơn
            )

            await self.pool.open()

            # Test the connection pool by executing a simple query
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            
            return self.pool
            
        except Exception as e:
            # Dọn dẹp khi thất bại
            await self.close()
            raise ValueError() from e

    async def execute_query(
        self,
        query: Query,
        params: Optional[ Params ],
        readonly: bool = False,
    ) -> Optional[List[QueryResult]]:
        """
        Execute a SQL query using a connection from the pool.
        
        Args:
            query: SQL query string to execute
            params: Optional list of query parameters for parameterized queries
            readonly: If True, execute in read-only transaction
            
        Returns:
            List of QueryResult objects for SELECT queries, None for DDL/DML without results
            
        Raises:
            ValueError: If pool is not connected or query execution fails
        """
        try:
            pool = self.pool
            # Đảm bảo pool đã được khởi tạo
            if not pool:
                pool = await self.connect()
                
            # Lấy connection từ pool và thực thi query
            async with pool.connection() as connection:
                return await self._execute_with_connection(
                    connection, query, params, readonly
                )
                
        except Exception as e:
            logger.error( f"❌ Error executing query" )
            raise

    async def _execute_with_connection(
        self, 
        connection: AsyncConnection, 
        query: Query, 
        params: Optional[ Params ], 
        force_readonly : bool
    ) -> Optional[ List[ QueryResult ] ]:
        """Execute query with the given connection from the pool."""
        transaction_started = False
        try:
            async with connection.cursor(row_factory=dict_row) as cursor:
                # Start read-only transaction if needed
                if force_readonly:
                    await cursor.execute("BEGIN TRANSACTION READ ONLY")
                    transaction_started = True

                # Execute the query with or without parameters
                if params:
                    await cursor.execute(query, params)
                else:
                    await cursor.execute(query)

                # For multiple statements, move to the last statement's results
                while cursor.nextset():
                    pass

                if cursor.description is None:  # No results (like DDL statements)
                    if not force_readonly:
                        await cursor.execute("COMMIT")
                    elif transaction_started:
                        await cursor.execute("ROLLBACK")
                        transaction_started = False
                    return None

                # Get results from the last statement only
                rows = await cursor.fetchall()

                # End the transaction appropriately
                if not force_readonly:
                    await cursor.execute("COMMIT")
                elif transaction_started:
                    await cursor.execute("ROLLBACK")
                    transaction_started = False

                # Convert to QueryResult format
                return [QueryResult(cells=dict(row)) for row in rows]

        except Exception as e:
            # Try to roll back the transaction if it's still active
            if transaction_started:
                try:
                    await connection.rollback()
                except Exception as rollback_error:
                    logger.error(f"❌ Error rolling back transaction: {rollback_error}")

            logger.error(f"❌ Error executing query ({query}): {e}")
            raise e

    async def close( self ) -> None:
        """Close the connection pool and clean up resources."""
        if self.pool:
            try:
                await self.pool.close()
                logger.info("✅ Database connection pool closed successfully")
            except Exception as e:
                logger.warning(f"❌ Error closing connection pool: {e}")
            finally:
                self.pool = None
