"""Facades: abstract interfaces for external capabilities. Implementations live in the service's infrastructure."""

from .cache import Cache
from .event import Event, EventBus, EventHandler, EventPublisher, EventSubscriber
from .http_client import HttpClient, HttpResponse
from .id_generator import IdGenerator, uuid_hex
from .lifecycle import Lifecycle
from .security import PasswordHasher
from .transaction import DataSource, HasTransactionManager, Transaction, TransactionManager

__all__ = [
    "Cache",
    "DataSource",
    "Event",
    "EventBus",
    "EventHandler",
    "EventPublisher",
    "EventSubscriber",
    "HasTransactionManager",
    "HttpClient",
    "HttpResponse",
    "IdGenerator",
    "Lifecycle",
    "PasswordHasher",
    "Transaction",
    "TransactionManager",
    "uuid_hex",
]
