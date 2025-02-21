# 🎓 EduConnect-LMS

> 🌟 Empowering collaborative learning through technology and innovation

<div align="center">

[![Live Demo](https://img.shields.io/badge/✨_Live_Demo-Click_Here-2ea44f?style=for-the-badge)](https://educonnect-lms.onrender.com/)

</div>

EduConnect-LMS is a collaborative learning management system designed to facilitate interaction between students, demonstrators, lecturers, and study groups. The platform integrates AI-powered tools to enhance the learning experience while providing a robust environment for academic collaboration.

## ✨ Features

### 👥 User Management
- Account creation and management by administrators
- User account request system
- Secure login system for all users
- Role-based access control (Students, Demonstrators, Lecturers)

### 👥 Study Groups
- Create and join subject/topic-specific study groups
- Group creation by Demonstrators/Lecturers
- Student-initiated group requests with approval system
- Share and access study materials within groups
- Collaborative note-sharing platform

### 👨‍🏫 Demonstrator Support
- Group management by subject/topic and year
- Task assignment capabilities
- Study material distribution
- Performance feedback system
- Direct interaction with student groups

### ⚡ AI-Enhanced Learning
- AI-powered content summarization
- Upload and process study materials
- Automated summary generation for efficient learning

### 💬 Discussion Forums
- Topic-specific discussion boards
- Peer-to-peer interaction
- Demonstrator/Lecturer participation
- Question and answer system

### ⏰ Study Session Management
- Schedule individual or group study sessions
- Built-in study timer
- Session tracking and management
- Time management tools

## 💻 Technology Stack

### 🎨 Frontend
- HTML
- CSS
- JavaScript

### ⚙️ Backend
- Flask (Python web framework)

### 🔌 API Services
- OpenAI API for AI-powered content summarization
- RESTful API architecture for service integration
- API endpoints for user management, study groups, and content delivery
- Secure API authentication and authorization

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step-by-Step Installation

1. Clone the repository:
```bash
git clone https://github.com/sandunMadhushan/EduConnect-LMS.git
```

2. Navigate to the project directory:
```bash
cd EduConnect-LMS
```

3. Create and activate a virtual environment:
**For Windows:**
```bash
# Create virtual environment
python -m venv virt
# Activate virtual environment
source virt/Scripts/activate
```

**For macOS/Linux:**
```bash
# Create virtual environment
python -m venv virt
# Activate virtual environment
source virt/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
# Create .env file
touch .env
```

Add the following required environment variables to your `.env` file:
```bash
# Database Configuration
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
DB_HOST=your_database_host

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
UPLOAD_FOLDER=path_to_upload_folder
SECRET_KEY=your_secret_key
```

Environment Variables Description:
- `DB_USER`: Database username for authentication
- `DB_PASSWORD`: Database password for authentication
- `DB_NAME`: Name of the database to be used
- `DB_HOST`: Database host address
- `OPENAI_API_KEY`: API key for OpenAI services
- `UPLOAD_FOLDER`: Path where uploaded files will be stored
- `SECRET_KEY`: Secret key for Flask application security

6. Run the application:
```bash
flask run
```

The application should now be running at `http://localhost:5000`

### Deactivating the Virtual Environment
When you're done working on the project, you can deactivate the virtual environment:
```bash
deactivate
```

### Troubleshooting
If you encounter any issues during installation:
1. Make sure you have the correct Python version installed
2. Ensure all prerequisites are met
3. Check if the virtual environment is activated (you should see `(virt)` in your terminal)
4. Verify that all environment variables are properly set in the `.env` file
5. Try removing the virtual environment and starting fresh:
   ```bash
   # Windows
   rmdir /s /q virt
   
   # macOS/Linux
   rm -rf virt
   ```

### Troubleshooting

If you encounter any issues during installation:

1. Make sure you have the correct Python version installed
2. Ensure all prerequisites are met
3. Check if the virtual environment is activated (you should see `(virt)` in your terminal)
4. Try removing the virtual environment and starting fresh:
   ```bash
   # Windows
   rmdir /s /q virt
   
   # macOS/Linux
   rm -rf virt
   ```

## 🔄 Development Status

This project is currently under active development. New features and improvements are being added regularly.

## 📩 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
