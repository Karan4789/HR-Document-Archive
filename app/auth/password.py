# app/auth/password.py

import bcrypt
MAX_PASSWORD_LENGTH = 72

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt, truncating it to 72 bytes if necessary."""

    truncated_password = password[:MAX_PASSWORD_LENGTH].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(truncated_password, salt)
    
    # Decode the hashed password back to a string for storing in the database
    return hashed_password_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed version."""
    # Truncate the plain password and encode it to bytes
    truncated_password = plain_password[:MAX_PASSWORD_LENGTH].encode('utf-8')
    
    # Encode the stored hashed password back to bytes for comparison
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # Use bcrypt's checkpw function to securely compare the two
    return bcrypt.checkpw(truncated_password, hashed_password_bytes)
