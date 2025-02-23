from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text
import os
import bcrypt  # for password hashing
from datetime import datetime
from azure.communication.email import EmailClient

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
        
# Azure Email
connection_string = os.getenv('CONNECTION_STRING')
sender_address = os.getenv('SENDER_ADDRESS')

def check_email_exists(email):
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def send_welcome_email_sync(user_email, name):
    """Synchronous version of send_welcome_email"""
    connection_string = os.getenv('CONNECTION_STRING')
    sender_address = os.getenv('SENDER_ADDRESS')
    
    try:
        email_client = EmailClient.from_connection_string(connection_string)
        
        message = {
            "senderAddress": sender_address,
            "content": {
                "subject": "Welcome to EduConnect!",
                "plainText": f"Hi {name},\n\nWelcome to EduConnect! Thank you for registering.\n\nBest regards,\nThe Team",
                "html": f"""
                    <html>
                        <body>
                            <h1>Welcome to EduConnect!</h1>
                            <p>Hi {name},</p>
                            <p>Welcome to EduConnect! Thank you for registering.</p>
                            <br>
                            <a href="https://educonnect-lms.onrender.com/" style="color: #ffffff; background: #1d3557; background-image: linear-gradient(145deg, #1d3557, #457b9d); padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; text-align: center;">
                            Visit EduConnect
                            </a>
                            <br>
                            <br>
                            <p>Best regards,</p>
                            <p>The Team</p>
                            <hr>
                            <p><img src="https://i.imgur.com/8yUWDDq.png" alt="EduConnect Logo" style="width:200px"></p>
                            <p style="font-size: 12px; color: #777;">This is an automated email. Please do not reply.</p>
                        </body>
                    </html>
                """
            },
            "recipients": {
                "to": [{"address": user_email, "displayName": name}]
            }
        }
        
        # Use sync version of send
        poller = email_client.begin_send(message)
        result = poller.result()
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def save_reset_token(email, token, expiry):
    """
    Save password reset token to database
    Returns: True if successful, False if failed
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            # First verify user exists
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            
            if not user:
                return False
                
            # Save token
            sql = """INSERT INTO password_resets (user_id, token, expiry)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE token = %s, expiry = %s"""
            cursor.execute(sql, (user[0], token, expiry, token, expiry))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving reset token: {e}")
        return False

def verify_reset_token(token):
    """
    Verify if reset token is valid and not expired
    Returns: True if valid, False if invalid or expired
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = """SELECT user_id, expiry FROM password_resets 
                    WHERE token = %s AND expiry > NOW()"""
            cursor.execute(sql, (token,))
            result = cursor.fetchone()
            return bool(result)
    except Exception as e:
        print(f"Error verifying reset token: {e}")
        return False

def update_password_with_token(token, new_password):
    """
    Update user password using reset token
    Returns: True if successful, False if failed
    """
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            # Get user_id from valid token
            sql = """SELECT user_id FROM password_resets 
                    WHERE token = %s AND expiry > NOW()"""
            cursor.execute(sql, (token,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            user_id = result[0]
            
            # Hash new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update password
            sql = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(sql, (hashed_password, user_id))
            
            # Delete used token
            sql = "DELETE FROM password_resets WHERE token = %s"
            cursor.execute(sql, (token,))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    
def get_user_by_email(email):
    """Get user data by email"""
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, email FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2]
                }
    except Exception as e:
        print(f"Error getting user by email: {e}")
    return None

def update_user_password(user_id, current_password, new_password):
    """
    Update user's password after verifying current password
    Returns: (bool, str) - (Success status, Message)
    """
    if not conn:
        return False, "Database connection error"
    try:
        with conn.cursor() as cursor:
            # First verify current password
            sql = "SELECT password FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "User not found"
            
            stored_password = result[0]
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
                
            # Verify current password
            if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password):
                return False, "Current password is incorrect"
            
            # Hash and update new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            sql = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(sql, (hashed_password, user_id))
            conn.commit()
            
            return True, "Password updated successfully"
    except Exception as e:
        print(f"Error updating password: {e}")
        return False, "An error occurred while updating password"