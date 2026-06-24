from abc import ABC, abstractmethod


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


class MySQLConnection(DatabaseConnection):
    def __init__(self, host, port, username, password, database, use_ssl=False,
                 connection_timeout=30, charset='utf8'):
        super().__init__(host, port, username, password, database, use_ssl)
        self.connection_timeout = connection_timeout
        self.charset = charset

    def connect(self):
        print(f"Connecting to mysql database...")
        connection_string = f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        connection_string += f"?charset={self.charset}"
        connection_string += f"&connectionTimeout={self.connection_timeout}"

        if self.use_ssl:
            connection_string += "&useSSL=true"

        print(f"MySQL Connection: {connection_string}")
        print("Connection successful!")
        return self.connection


class PostgreSQLConnection(DatabaseConnection):
    def connect(self):
        print(f"Connecting to postgresql database...")
        connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

        if self.use_ssl:
            connection_string += "?sslmode=require"

        print(f"PostgreSQL Connection: {connection_string}")
        print("Connection successful!")
        return self.connection


class MongoDBConnection(DatabaseConnection):
    def __init__(self, host, port, username, password, database, use_ssl=False,
                 retry_attempts=3, pool_size=5):
        super().__init__(host, port, username, password, database, use_ssl)
        self.retry_attempts = retry_attempts
        self.pool_size = pool_size

    def connect(self):
        print(f"Connecting to mongodb database...")
        connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        connection_string += f"?retryAttempts={self.retry_attempts}"
        connection_string += f"&poolSize={self.pool_size}"

        if self.use_ssl:
            connection_string += "&ssl=true"

        print(f"MongoDB Connection: {connection_string}")
        print("Connection successful!")
        return self.connection


class RedisConnection(DatabaseConnection):
    def connect(self):
        print(f"Connecting to redis database...")
        print(f"Redis Connection: {self.host}:{self.port}/{self.database}")
        print("Connection successful!")
        return self.connection


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
