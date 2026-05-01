🚀 Team Task Manager (Full-Stack)
A robust web application designed for teams to create projects, assign tasks, and track real-time progress. Built with a focus on Role-Based Access Control (RBAC) and data relationships.

✨ Key Features
Authentication: Secure Login and Signup system using Bcrypt password hashing.

Role-Based Access:

Admins: Can create projects and assign tasks to any team member.

Members: Can view their assigned tasks and update their status.

Live Dashboard: Real-time metrics showing Total Tasks, Completed Tasks, and Overdue tracking.

Task Management: Interactive task board allowing status updates (Todo, Doing, Done).

🛠️ Tech Stack
Frontend: Streamlit (Python-based interactive UI)

Backend: Python

Database: SQLAlchemy with SQLite (Local) / PostgreSQL (Production)

Deployment: Railway

📋 Requirements Fulfilled
As per the assignment instructions in 1000255082.jpg:

[x] RESTful logic with a structured database.

[x] Proper Validations for user inputs and unique usernames.

[x] Relationships: Linked Users ↔ Tasks ↔ Projects.

[x] Deployment: Fully functional and live on Railway.

🚀 Installation & Local Setup
Clone the repository:

Bash
git clone <your-github-repo-url>
cd team-task-manager
Set up a Virtual Environment:

Bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
Install Dependencies:

Bash
pip install -r requirements.txt
Run the Application:

Bash
streamlit run app.py

🌐 Live Demo
The application is live at: [Insert Your Railway URL Here]