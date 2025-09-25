#!/usr/bin/env python3
"""
Script to reset challenge submissions for testing purposes
"""

import requests
import json

def login_as_admin():
    """Login as admin and get token"""
    response = requests.post('http://localhost:5000/api/auth/login', 
                           json={'username': 'admin', 'password': 'admin123!'})
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Login failed: {response.text}")
        return None

def reset_challenge_submissions(challenge_id, user_id=None):
    """Reset submissions for a challenge"""
    token = login_as_admin()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    data = {}
    
    if user_id:
        data['user_id'] = user_id
    
    response = requests.post(f'http://localhost:5000/api/admin/challenges/{challenge_id}/reset',
                           headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        if 'deleted_submissions' in result:
            print(f"   Deleted {result['deleted_submissions']} submissions")
        if 'user_score' in result:
            print(f"   User score: {result['user_score']}")
        return True
    else:
        print(f"❌ Reset failed: {response.text}")
        return False

def reset_user_score(user_id):
    """Reset all submissions and score for a user"""
    token = login_as_admin()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(f'http://localhost:5000/api/admin/users/{user_id}/reset-score',
                           headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Deleted {result['deleted_submissions']} submissions")
        print(f"   New score: {result['new_score']}")
        return True
    else:
        print(f"❌ Reset failed: {response.text}")
        return False

if __name__ == "__main__":
    print("🔧 CTF Challenge Reset Tool")
    print("=" * 40)
    
    # Get user input
    choice = input("Choose option:\n1. Reset challenge for all users\n2. Reset challenge for specific user\n3. Reset user's entire score\nChoice (1-3): ")
    
    if choice == "1":
        challenge_id = int(input("Enter challenge ID: "))
        reset_challenge_submissions(challenge_id)
    elif choice == "2":
        challenge_id = int(input("Enter challenge ID: "))
        user_id = int(input("Enter user ID: "))
        reset_challenge_submissions(challenge_id, user_id)
    elif choice == "3":
        user_id = int(input("Enter user ID: "))
        reset_user_score(user_id)
    else:
        print("Invalid choice")
