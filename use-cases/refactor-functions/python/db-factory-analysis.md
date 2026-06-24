# Design Pattern Analysis — Factory Pattern (Database Connection Manager)

## Original code

`DatabaseConnection.__init__` accepts **11 parameters** — some shared by all databases, some specific to one type. The `connect()` method is a 60-line if/elif chain building connection strings differently for each database.

```python
class DatabaseConnection:
    def __init__(self, db_type, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, retry_attempts=3,
                 pool_size=5, charset='utf8'):
        # stores all params regardless of relevance

    def connect(self):
        if self.db_type == 'mysql':
            # MySQL-specific connection string logic
        elif self.db_type == 'postgresql':
            # PostgreSQL-specific logic
        elif self.db_type == 'mongodb':
            # MongoDB-specific logic
        elif self.db_type == 'redis':
            # Redis-specific logic
        else:
            raise ValueError(...)
```

### Problems

| Problem | Impact |
|---------|--------|
| Mammoth constructor | Caller must know/supply all 11 params even when most are irrelevant |
| Conditional branching | Adding a new database type means editing the `connect()` method — violates Open/Closed Principle |
| Mixed concerns | Redis connection string is fundamentally different from MongoDB's, yet they share a class |
| Hidden dependencies | MySQL's `charset` param is irrelevant for Redis but appears in every constructor call |

---

## Refactored design — Factory + Strategy

### 1. Abstract base class

```python
class DatabaseConnection(ABC):
    def __init__(self, host, port, username, password, database, use_ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        self.connection = None

    @abstractmethod
    def connect(self):
        pass
```

Only truly common parameters live here. Each subclass adds its own.

### 2. Concrete classes

| Class | Specific params | Connection signature |
|-------|----------------|---------------------|
| `MySQLConnection` | `connection_timeout`, `charset` | `mysql://user:pass@host:port/db?charset=utf8&connectionTimeout=30` |
| `PostgreSQLConnection` | (none beyond shared) | `postgresql://user:pass@host:port/db` + optional `?sslmode=require` |
| `MongoDBConnection` | `retry_attempts`, `pool_size` | `mongodb://user:pass@host:port/db?retryAttempts=3&poolSize=5` |
| `RedisConnection` | (none beyond shared) | `host:port/db` |

Each class owns its `connect()` method — no branching needed.

### 3. Factory

```python
class DatabaseConnectionFactory:
    _registry = {
        'mysql': MySQLConnection,
        'postgresql': PostgreSQLConnection,
        'mongodb': MongoDBConnection,
        'redis': RedisConnection,
    }

    @staticmethod
    def create_connection(db_type, **kwargs):
        cls = DatabaseConnectionFactory._registry.get(db_type)
        if cls is None:
            raise ValueError(f"Unsupported database type: {db_type}")
        return cls(**kwargs)
```

The registry is a plain dict — adding a new database is a one-line registration.

---

## Test results

```
Ran 17 tests in 0.002s — OK
```

Tests cover:
- Factory dispatches to the correct class for all 4 types
- Unsupported type raises `ValueError`
- Each connection type produces the correct output (connection string format, ssl params, custom settings)
- Direct instantiation of concrete classes works (they're real classes, not hidden behind the factory)
- Abstract base class cannot be instantiated (enforces the pattern)

---

## Reflection

### How did the pattern improve maintainability?

The original `connect()` method had all four database implementations tangled together. Adding PostgreSQL SSL support risked breaking MySQL charset handling because they shared the same method body. Now each connection type is isolated in its own class — you can't accidentally break one database while changing another.

**Before**: 1 class + 1 method with a 4-branch if/elif chain = 60 lines of conditional logic
**After**: 1 abstract base + 4 concrete classes + 1 factory = each class is ~15 lines, zero conditional logic

### What future changes will be easier?

- **Adding a new database type** (e.g., SQLite): create `SQLiteConnection(DatabaseConnection)`, add `'sqlite': SQLiteConnection` to the registry. Zero changes to existing code.
- **Changing MySQL's connection string format**: edit `MySQLConnection.connect()` — no risk of affecting PostgreSQL, MongoDB, or Redis.
- **Adding database-specific features** (e.g., connection pooling config for PostgreSQL): add a `pool_size` param to `PostgreSQLConnection.__init__` — it doesn't pollute other connection classes.
- **Testing in isolation**: `MySQLConnection` can be unit-tested without instantiating `MongoDBConnection` or mocking unrelated parameters.

### Unexpected challenges

The **parameter forwarding** through `**kwargs` in the factory is the trickiest part. The factory doesn't validate which kwargs belong to which concrete class — that validation happens at construction time. A mistyped parameter name produces a `TypeError` from the concrete class, which is less friendly than validation at the factory level. A more robust design could use a factory method per type or parameter validation, but that would add complexity that isn't justified for this example.

The **test stdout capture** also required careful setup/teardown. Since `connect()` uses `print()` for output, the tests redirect `sys.stdout` to a `StringIO` to verify connection strings. This is fragile — in a real codebase, the connection logic would return a string or structured data that tests can inspect without capturing I/O.

### Readability patterns to apply going forward

1. **Replace conditionals with polymorphic dispatch** — an if/elif chain based on a type string is a signal that Factory + Strategy can simplify the design.
2. **Small constructors** — if `__init__` needs more than ~5 parameters, consider whether the class is doing too much.
3. **Registry pattern** — a dict mapping type names to classes is simpler and more maintainable than a chain of `if/elif` statements, and makes registration extensible without modification.
4. **Abstract base classes as contracts** — `ABC` with `@abstractmethod` makes the interface explicit and prevents instantiation of incomplete implementations.
