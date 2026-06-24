import unittest
import sys
from io import StringIO
from db_connection import (
    DatabaseConnectionFactory,
    MySQLConnection,
    PostgreSQLConnection,
    MongoDBConnection,
    RedisConnection,
)


class TestDatabaseConnectionFactory(unittest.TestCase):
    def setUp(self):
        self.recorder = StringIO()
        self._stdout = sys.stdout
        sys.stdout = self.recorder

    def tearDown(self):
        sys.stdout = self._stdout

    def output(self):
        return self.recorder.getvalue()

    # --- Factory dispatch ---

    def test_factory_creates_mysql(self):
        db = DatabaseConnectionFactory.create_connection(
            'mysql', host='localhost', port=3306, username='user',
            password='pass', database='mydb')
        self.assertIsInstance(db, MySQLConnection)

    def test_factory_creates_postgresql(self):
        db = DatabaseConnectionFactory.create_connection(
            'postgresql', host='pg.example.com', port=5432, username='pguser',
            password='pgpass', database='analytics')
        self.assertIsInstance(db, PostgreSQLConnection)

    def test_factory_creates_mongodb(self):
        db = DatabaseConnectionFactory.create_connection(
            'mongodb', host='mongo.example.com', port=27017, username='muser',
            password='mpass', database='logs')
        self.assertIsInstance(db, MongoDBConnection)

    def test_factory_creates_redis(self):
        db = DatabaseConnectionFactory.create_connection(
            'redis', host='redis.example.com', port=6379, username='',
            password='', database='0')
        self.assertIsInstance(db, RedisConnection)

    def test_factory_unsupported_type(self):
        with self.assertRaises(ValueError) as ctx:
            DatabaseConnectionFactory.create_connection(
                'oracle', host='localhost', port=1521, username='user',
                password='pass', database='db')
        self.assertIn("Unsupported database type: oracle", str(ctx.exception))

    # --- MySQL ---

    def test_mysql_connection_defaults(self):
        db = DatabaseConnectionFactory.create_connection(
            'mysql', host='localhost', port=3306, username='user',
            password='pass', database='mydb')
        conn = db.connect()
        out = self.output()
        self.assertIn("Connecting to mysql database...", out)
        self.assertIn("MySQL Connection: mysql://user:pass@localhost:3306/mydb?charset=utf8&connectionTimeout=30", out)
        self.assertIn("Connection successful!", out)
        self.assertIsNone(conn)

    def test_mysql_connection_with_ssl(self):
        db = DatabaseConnectionFactory.create_connection(
            'mysql', host='localhost', port=3306, username='user',
            password='pass', database='mydb', use_ssl=True)
        db.connect()
        out = self.output()
        self.assertIn("&useSSL=true", out)

    def test_mysql_connection_custom_timeout(self):
        db = DatabaseConnectionFactory.create_connection(
            'mysql', host='localhost', port=3306, username='user',
            password='pass', database='mydb', connection_timeout=60)
        db.connect()
        out = self.output()
        self.assertIn("&connectionTimeout=60", out)

    def test_mysql_connection_custom_charset(self):
        db = DatabaseConnectionFactory.create_connection(
            'mysql', host='localhost', port=3306, username='user',
            password='pass', database='mydb', charset='latin1')
        db.connect()
        out = self.output()
        self.assertIn("charset=latin1", out)

    # --- PostgreSQL ---

    def test_postgresql_connection(self):
        db = DatabaseConnectionFactory.create_connection(
            'postgresql', host='pg.example.com', port=5432, username='pguser',
            password='pgpass', database='analytics')
        db.connect()
        out = self.output()
        self.assertIn("Connecting to postgresql database...", out)
        self.assertIn("PostgreSQL Connection: postgresql://pguser:pgpass@pg.example.com:5432/analytics", out)
        self.assertIn("Connection successful!", out)

    def test_postgresql_connection_with_ssl(self):
        db = DatabaseConnectionFactory.create_connection(
            'postgresql', host='pg.example.com', port=5432, username='pguser',
            password='pgpass', database='analytics', use_ssl=True)
        db.connect()
        out = self.output()
        self.assertIn("?sslmode=require", out)

    # --- MongoDB ---

    def test_mongodb_connection(self):
        db = DatabaseConnectionFactory.create_connection(
            'mongodb', host='mongo.example.com', port=27017, username='muser',
            password='mpass', database='logs', retry_attempts=5, pool_size=10)
        db.connect()
        out = self.output()
        self.assertIn("Connecting to mongodb database...", out)
        self.assertIn("MongoDB Connection: mongodb://muser:mpass@mongo.example.com:27017/logs", out)
        self.assertIn("?retryAttempts=5&poolSize=10", out)
        self.assertIn("Connection successful!", out)

    def test_mongodb_connection_with_ssl(self):
        db = DatabaseConnectionFactory.create_connection(
            'mongodb', host='mongo.example.com', port=27017, username='muser',
            password='mpass', database='logs', use_ssl=True)
        db.connect()
        out = self.output()
        self.assertIn("&ssl=true", out)

    # --- Redis ---

    def test_redis_connection(self):
        db = DatabaseConnectionFactory.create_connection(
            'redis', host='redis.example.com', port=6379, username='',
            password='', database='0')
        db.connect()
        out = self.output()
        self.assertIn("Connecting to redis database...", out)
        self.assertIn("Redis Connection: redis.example.com:6379/0", out)
        self.assertIn("Connection successful!", out)

    # --- Direct instantiation ---

    def test_mysql_direct_instantiation(self):
        db = MySQLConnection('localhost', 3306, 'user', 'pass', 'mydb')
        db.connect()
        out = self.output()
        self.assertIn("MySQL Connection:", out)

    def test_postgresql_direct_instantiation(self):
        db = PostgreSQLConnection('pg.example.com', 5432, 'pguser', 'pgpass', 'analytics')
        db.connect()
        out = self.output()
        self.assertIn("PostgreSQL Connection:", out)

    def test_abstract_base_class_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            from db_connection import DatabaseConnection
            DatabaseConnection('localhost', 3306, 'u', 'p', 'd')


if __name__ == "__main__":
    unittest.main()
