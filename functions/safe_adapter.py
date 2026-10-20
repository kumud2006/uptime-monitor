"""Requests adapter using validated public-IP connections."""

from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.poolmanager import PoolManager

from safe_connection import create_safe_connection


class SafeHTTPConnection(HTTPConnection):
    def _new_conn(self):
        return create_safe_connection(
            (self._dns_host, self.port),
            timeout=self.timeout,
            source_address=self.source_address,
            socket_options=self.socket_options,
        )


class SafeHTTPSConnection(HTTPSConnection):
    def _new_conn(self):
        return create_safe_connection(
            (self._dns_host, self.port),
            timeout=self.timeout,
            source_address=self.source_address,
            socket_options=self.socket_options,
        )


class SafeHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = SafeHTTPConnection


class SafeHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = SafeHTTPSConnection


class SafePoolManager(PoolManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool_classes_by_scheme = {
            "http": SafeHTTPConnectionPool,
            "https": SafeHTTPSConnectionPool,
        }


class SafeHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = SafePoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            **pool_kwargs,
        )
