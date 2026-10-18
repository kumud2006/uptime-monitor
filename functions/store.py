import os
from functools import lru_cache

from azure.cosmos import CosmosClient


@lru_cache(maxsize=1)
def _database():
    client = CosmosClient.from_connection_string(os.environ["DB_CONNECTION"])
    return client.get_database_client(os.environ.get("DB_NAME", "uptime"))


def _container(name):
    return _database().get_container_client(name)


def list_targets():
    return list(
        _container("targets").query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
        )
    )


def upsert_target(doc):
    _container("targets").upsert_item(doc)


def add_check(doc):
    _container("checks").create_item(doc)


def checks_since(target_id, since_iso):
    return list(
        _container("checks").query_items(
            query=(
                "SELECT c.timestamp, c.latency_ms, c.ok FROM c "
                "WHERE c.target_id = @t AND c.timestamp >= @s "
                "ORDER BY c.timestamp ASC"
            ),
            parameters=[
                {"name": "@t", "value": target_id},
                {"name": "@s", "value": since_iso},
            ],
            partition_key=target_id,
        )
    )


def create_incident(doc):
    _container("incidents").create_item(doc)


def resolve_incident(target_id, incident_id, resolved_at):
    container = _container("incidents")
    doc = container.read_item(item=incident_id, partition_key=target_id)
    doc["resolved_at"] = resolved_at
    container.upsert_item(doc)


def list_incidents(limit=50):
    return list(
        _container("incidents").query_items(
            query=(
                f"SELECT TOP {int(limit)} "
                "c.id, c.name, c.started_at, c.resolved_at "
                "FROM c ORDER BY c.started_at DESC"
            ),
            enable_cross_partition_query=True,
        )
    )
