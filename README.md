# Web CTF Platform

A modern web-based Capture The Flag platform inspired by overthewire.org, designed to provide cybersecurity education through interactive challenges without requiring VM installations.

## Features

- 🎯 **Web-based Challenges**: Solve CTF challenges directly in your browser
- 🔐 **User Authentication**: Secure login and user management
- 🏆 **Scoring System**: Track progress with points and leaderboards
- 📊 **Progress Tracking**: Monitor solved challenges and statistics
- 🎨 **Modern UI**: Clean, responsive interface built with React
- 🚀 **Easy Deployment**: Simple setup with PowerShell scripts
- 🔧 **Admin Panel**: Manage challenges and users through web interface
- 🎲 **Multi-part Challenges**: Complex challenges with multiple flag submissions
- 📈 **Difficulty Levels**: Easy, Medium, and Hard challenges with appropriate point values

## Challenge Categories

- **Cryptography**: Encryption, decryption, and crypto analysis
- **Web Security**: XSS, SQL injection, and web vulnerabilities
- **Forensics**: File analysis, steganography, and data recovery
- **Reverse Engineering**: Binary analysis and code understanding
- **Network Security**: Packet analysis and network protocols
- **Miscellaneous**: General security concepts and puzzles

## Scoring System

Challenges are categorized by difficulty with corresponding point values:

- **Easy**: 50-100 points
- **Medium**: 100-150 points  
- **Hard**: 150+ points

### Multi-part Challenges

Some challenges require multiple flag submissions to complete:

- **Primary Flag**: The main challenge answer (e.g., `flag{attack_type}`)
- **Secondary Flags**: Additional information (e.g., `flag2{attacker_ip}`)
- **Completion**: All parts must be submitted to receive full points
- **Partial Credit**: Individual parts can be submitted independently

Example: A DNS Cache Poisoning challenge might require:
1. `flag{dns_cache_poisoning}` - The attack type
2. `flag2{10.0.0.50}` - The attacker's IP address

## Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd ctf-platform
   ```

2. **Install Dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   cd client
   npm install
   cd ..
   ```

3. **Configure Environment Variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file with your preferred settings
   # Use  Generate_Secrets.py to generate secret key, jwt secret key, and admin password.
   # At minimum, change the SECRET_KEY and JWT_SECRET_KEY
   ```

4. **Start the Platform**
   ```powershell
   # Windows PowerShell - Database will be automatically initialized if needed
   .\start_ctf.ps1
   
   # Or use the simple version
   .\start_ctf_simple.ps1
   ```

5. **Access the Platform**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Admin Login: username: `admin`, password: `.env[ADMIN_PASSWORD]`

## Project Structure

```
web-ctf-platform/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── contexts/       # React contexts
│   └── public/             # Static assets
├── server/                 # Python Flask backend
│   ├── routes/             # API routes
│   ├── models.py           # Database models
│   ├── utils/              # Server utilities
│   │   └── sample_data.py  # Sample challenges
│   └── instance/           # Database files
├── start_ctf.ps1           # PowerShell startup script
├── start_ctf_simple.ps1    # Simple PowerShell startup script
└── requirements.txt        # Python dependencies
```

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python Flask, SQLAlchemy
- **Database**: SQLite
- **Authentication**: JWT tokens
- **Multi-part Challenges**: Support for complex flag submissions with multiple answers
- **Deployment**: PowerShell scripts for easy startup
- **Real-time Updates**: React Query for efficient data fetching
- **Responsive Design**: Mobile-friendly interface

## Security Best Practices

### Environment Variables
- **Never commit `.env` files** - They contain sensitive information
- **Use strong secrets** - Generate random strings for `SECRET_KEY` and `JWT_SECRET_KEY`
- **Change default credentials** - Update admin username/password in production

### Production Deployment
- Use environment-specific configuration files
- Enable HTTPS in production
- Use a proper database (PostgreSQL) instead of SQLite
- Set up proper logging and monitoring
- Use a reverse proxy (nginx) for the frontend
- Implement rate limiting and DDoS protection

### Development Security
- Keep dependencies updated
- Use virtual environments for Python
- Don't expose admin credentials in logs
- Use different secrets for development and production

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
