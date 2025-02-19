from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text
import os

# Load environment variables
load_dotenv()

try:
    conn = pymysql.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        ssl={'ssl': True}
    )
except Exception as e:
    print(f"Database connection error: {e}")
    conn = None

def get_studygroups():
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM studygroups")
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def create_studygroup(name, description, members):
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO studygroups (name, description, members) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, description, members))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def db_post_a_question(title, category, description):
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO questions (title, category, description) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, category, description))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_questions_by_category(category):
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM questions WHERE category = %s"
            cursor.execute(sql, (category))
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error: {e}")
        return []
    
def get_all_questions():
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM questions")
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def close_connection():
    if conn:
        conn.close()