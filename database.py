from sqlalchemy import create_engine, text
import pymysql

# engine = create_engine('mysql+pymysql://admineduconnectlms:password.2109@educonnectlms.mysql.database.azure.com/educonnect')

# def get_studygroups():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM studygroups"))
#         studygroups = []
#         for row in result.all():
#             studygroups.append(dict(row))
#         return studygroups


# with engine.connect() as conn:
#       result = conn.execute(text("SELECT * FROM studygroups"))
#       print(result.all())


conn = pymysql.connect(user='admineduconnectlms',
   password='password.2109',
   database='educonnect',
   host='educonnectlms.mysql.database.azure.com',
   ssl={'ssl': True})

def get_studygroups():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM studygroups")
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def create_studygroup(name, description, members):
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO studygroups (name, description, members) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, description, members))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return None

def close_connection():
    if conn:
        conn.close()