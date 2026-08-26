from database.connection import db
from utils.security import verify_password, hash_password

class AuthService:
    @staticmethod
    def login(username, password):
        user = db.one("SELECT * FROM users WHERE username=? AND is_active=1", (username.strip(),))
        return user if user and verify_password(password, user["password_hash"]) else None
    @staticmethod
    def change_password(user_id, old, new):
        user = db.one("SELECT * FROM users WHERE id=?", (user_id,))
        if not user or not verify_password(old, user["password_hash"]): return False
        db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new), user_id)); return True
    @staticmethod
    def users(): return db.query("SELECT id,username,full_name,role,is_active,created_at FROM users ORDER BY id DESC")
    @staticmethod
    def add_user(username,password,full_name,role):
        return db.execute("INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)",
                          (username,hash_password(password),full_name,role))

