import pymysql


def db_conn(app):
    connection = pymysql.connect(
        host=app.config['DATABASE_HOST'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASS'],
        db=app.config['DATABASE_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def db_init():
    connection = db_conn()
    try:
        # DROP DATABASE IF EXISTS testing;CREATE DATABASE testing CHARACTER SET utf8 COLLATE utf8_general_ci;USE testing;
        with connection.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    theme VARCHAR(255) NOT NULL,
                    text TEXT NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    state VARCHAR(50) DEFAULT 'open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )  ENGINE=INNODB;
            """
            cursor.execute(sql)
        connection.commit()

        with connection.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS comments (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    ticket_id INT REFERENCES tickets (id),
                    text TEXT NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )  ENGINE=INNODB;
            """
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()
