from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
from psycopg2.extensions import connection as _pgconn
from dblib.db_api import DBToolSuite
import dblib.result_collector as rc
import dblib.util as dbutil

DOLT_USER = "postgres"
DOLT_PASSWORD = "password"
DOLT_HOST = "localhost"
DOLT_PORT = 5432


class DoltToolSuite(DBToolSuite):
    """
    A suite of tools for interacting with a Dolt database on a shared connection.
    """

    @classmethod
    def get_default_connection_uri(cls) -> str:
        return dbutil.format_db_uri(
            DOLT_USER, DOLT_PASSWORD, DOLT_HOST, DOLT_PORT, "postgres"
        )

    @classmethod
    def init_for_bench(
        cls,
        collector: rc.ResultCollector,
        db_name: str,
        autocommit: bool,
    ):
        uri = dbutil.format_db_uri(
            DOLT_USER, DOLT_PASSWORD, DOLT_HOST, DOLT_PORT, db_name
        )

        conn = psycopg2.connect(uri)
        if autocommit:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return cls(
            connection=conn,
            collector=collector,
            connection_uri=uri,
            autocommit=autocommit,
        )

    def __init__(
        self,
        connection: _pgconn,
        collector: rc.ResultCollector,
        connection_uri: str,
        autocommit: bool,
    ):
        super().__init__(connection, result_collector=collector)
        self._connection_uri = connection_uri
        self.autocommit = autocommit

    def get_uri_for_db_setup(self) -> str:
        """Returns the connection URI for database setup operations (e.g., psql)."""
        return self._connection_uri

    def _prepare_commit(self, message: str = "") -> None:
        try:
            cmd = "SELECT dolt_add('.');"
            super().execute_sql(cmd)
            cmd = f"SELECT dolt_commit('-m', '{message}');"
            super().execute_sql(cmd)
        except Exception as e:
            # Ignore commit errors (e.g., no changes to commit).
            print(f"Commit failed: {e}")

    def _create_branch_impl(self, branch_name: str, parent_id: str) -> None:
        # if parent_id:
        #     self.execute_sql("SELECT dolt_branch(%s, %s);", (branch_name, parent_id))
        # else:
        self.execute_sql("SELECT dolt_branch(%s);", (branch_name,))

    def _connect_branch_impl(self, branch_name: str) -> None:
        super().execute_sql("SELECT DOLT_CHECKOUT(%s);", (branch_name,))

    def _get_current_branch_impl(self) -> tuple[str, str]:
        name, head = self.execute_sql(
            "SELECT active_branch(), "
            "COALESCE((SELECT hash FROM dolt_branches WHERE name = active_branch()), hashof('HEAD'));"
        )[0]
        return name or "", head
