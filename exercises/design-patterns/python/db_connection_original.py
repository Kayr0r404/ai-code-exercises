class DatabaseConnection:
    def __init__(self, db_type, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, retry_attempts=3,
                 pool_size=5, charset='utf8'):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        self.connection_timeout = connection_timeout
        self.retry_attempts = retry_attempts
        self.pool_size = pool_size
        self.charset = charset
        self.connection = None

    def connect(self):
        print(f"Connecting to {self.db_type} database...")

        if self.db_type == 'mysql':
            connection_string = f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            connection_string += f"?charset={self.charset}"
            connection_string += f"&connectionTimeout={self.connection_timeout}"

            if self.use_ssl:
                connection_string += "&useSSL=true"

            print(f"MySQL Connection: {connection_string}")

        elif self.db_type == 'postgresql':
            connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

            if self.use_ssl:
                connection_string += "?sslmode=require"

            print(f"PostgreSQL Connection: {connection_string}")

        elif self.db_type == 'mongodb':
            connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            connection_string += f"?retryAttempts={self.retry_attempts}"
            connection_string += f"&poolSize={self.pool_size}"

            if self.use_ssl:
                connection_string += "&ssl=true"

            print(f"MongoDB Connection: {connection_string}")

        elif self.db_type == 'redis':
            print(f"Redis Connection: {self.host}:{self.port}/{self.database}")

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

        print("Connection successful!")
        return self.connection
