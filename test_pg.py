import psycopg2, os
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME','pixup_db'),
        user=os.getenv('DB_USER','pixup_user'),
        password=os.getenv('DB_PASSWORD','123'),
        host=os.getenv('DB_HOST','localhost'),
        port=os.getenv('DB_PORT','5432'),
    )
    print('Conexão OK')
    conn.close()
except Exception as e:
    print('ERRO', repr(e))