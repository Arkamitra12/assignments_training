import psycopg2
def get_connection():
    conn=psycopg2.connect(
        host="localhost",
        database="library_store",
        user="postgres",
        password="Admin@123"
    )
    print("Connected to postgre successfully")
    return conn
if __name__ == "__main__":
    conn=get_connection()
    connection.close()