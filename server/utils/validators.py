"""
Validation utilities for user input
"""

import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    # 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    # Check for uppercase, lowercase, number, and special character
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    return has_upper and has_lower and has_digit and has_special

def validate_flag_format(flag):
    """Validate flag format"""
    # Common flag formats: flag{...}, flag2{...}, CTF{...}, or custom formats
    if len(flag) < 5 or len(flag) > 500:
        return False
    
    # Basic validation - no dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    return not any(char in flag for char in dangerous_chars)

def validate_multi_flag(submitted_flag, expected_flags):
    """Validate multi-part flag submission"""
    if isinstance(expected_flags, str):
        # Single flag format
        return submitted_flag == expected_flags
    
    if isinstance(expected_flags, list):
        # Multiple possible flags
        return submitted_flag in expected_flags
    
    if isinstance(expected_flags, dict):
        # Multi-part flag with different formats
        for flag_format, expected_answer in expected_flags.items():
            if submitted_flag == f"{flag_format}{{{expected_answer}}}":
                return True
        return False
    
    return False

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    return text[:1000] if text else ""
