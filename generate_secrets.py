#!/usr/bin/env python3
"""
Generate secure secrets for the CTF Platform
Run this script to generate random secrets for your .env file
"""

import secrets
import string

def generate_secret(length=32):
    """Generate a random secret string"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_admin_password(length=12):
    """Generate a secure admin password with mixed case, numbers, and symbols"""
    # Ensure at least one of each type
    lowercase = secrets.choice(string.ascii_lowercase)
    uppercase = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice("!@#$%^&*")
    
    # Generate remaining characters
    remaining_length = length - 4
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    remaining = ''.join(secrets.choice(alphabet) for _ in range(remaining_length))
    
    # Combine and shuffle
    password_chars = list(lowercase + uppercase + digit + symbol + remaining)
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)

def main():
    print("🔐 CTF Platform Secret Generator")
    print("=" * 40)
    print()
    
    # Generate all secrets
    secret_key = generate_secret(32)
    jwt_secret = generate_secret(32)
    admin_password = generate_admin_password(12)
    
    print("Add these to your .env file:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"ADMIN_PASSWORD={admin_password}")
    print()
    print("⚠️  Keep these secrets secure and never commit them to version control!")
    print()
    
    # Print admin password to console for easy copying
    print("🔑 Generated Admin Password:")
    print(f"   {admin_password}")
    print()
    
    # Generate additional secrets for production
    print("For production, also consider generating:")
    print(f"# Database password: {generate_secret(16)}")
    print(f"# Redis password: {generate_secret(16)}")
    print(f"# Custom admin username: admin_{generate_secret(8)}")

if __name__ == "__main__":
    main()
