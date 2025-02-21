from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text
import os
import bcrypt  # for password hashing
from datetime import datetime

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
        
def register_user(name, email, password):
    """
    Register a new user with hashed password
    Returns: User ID if successful, None if failed
    """
    if not conn:
        return None
    try:
        # Check if email already exists
        with conn.cursor() as cursor:
            check_sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(check_sql, (email,))
            if cursor.fetchone():
                print("Email already exists")  # Debug line
                return None  # If the email exists, return None

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        with conn.cursor() as cursor:
            sql = """
                INSERT INTO users (name, email, password, joined_date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                name,
                email,
                hashed_password,
                datetime.now().date()
            ))
            conn.commit()
            return cursor.lastrowid  # Return the user ID
    except Exception as e:
        print(f"Registration error: {e}")  # More detailed error logging
        return None

def login_user(email, password):
    """
    Verify user credentials
    Returns: User data if successful, None if failed
    """
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user:
                # Verify password
                stored_password = user[3] 
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')

                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    return {
                        'id': user[0],
                        'name': user[1],
                        'email': user[2],
                        'joined_date': user[4],
                        'bio': user[5],           
                    'profile_pic': user[6]  
                    }
                else:
                    print("Password verification failed")  # Debugging password mismatch
            else:
                print("User not found")  # User not found in the database
    except Exception as e:
        print(f"Login error: {e}")
    return None


def get_user_by_id(user_id):
    """
    Retrieve user information by ID
    Returns: User data if found, None if not found
    """
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, email, password, joined_date, bio, profile_pic FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'password': user[3],
                    'joined_date': user[4],
                    'bio': user[5],           
                    'profile_pic': user[6]    
                }
            else:
                print("No user found with that ID.")
    except Exception as e:
        print(f"Error: {e}")
    return None

def update_user(user_id, name=None, email=None):
    """
    Update user information
    Returns: True if successful, False if failed
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            updates = []
            values = []
            if name:
                updates.append("name = %s")
                values.append(name)
            if email:
                updates.append("email = %s")
                values.append(email)
                
            if not updates:
                return False
                
            values.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(sql, tuple(values))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_user_profile_pic(user_id, profile_pic_path):
    """
    Update user's profile picture path in database
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET profile_pic = %s WHERE id = %s"
            cursor.execute(sql, (profile_pic_path, user_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_user_profile(user_id, name=None, email=None, bio=None):
    """
    Update user information
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            updates = []
            values = []
            if name:
                updates.append("name = %s")
                values.append(name)
            if email:
                updates.append("email = %s")
                values.append(email)
            if bio:
                updates.append("bio = %s")
                values.append(bio)
                
            if not updates:
                return False
                
            values.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(sql, tuple(values))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def close_connection():
    if conn:
        conn.close()