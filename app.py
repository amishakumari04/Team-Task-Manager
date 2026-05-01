import streamlit as st
import bcrypt
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models import SessionLocal, User, Project, Task  # Ensure models.py is in the same folder

# --- Configuration ---
st.set_page_config(page_title="Team Task Manager", layout="wide")
db = SessionLocal()

# --- Auth Helpers ---
def hash_pw(pw): 
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_pw(pw, hashed): 
    return bcrypt.checkpw(pw.encode(), hashed.encode())

# Initialize session state for user login
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

# --- AUTHENTICATION UI (Centered) ---
if st.session_state.user_id is None:
    st.title("🛡️ Team Task Manager")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Login", use_container_width=True):
                user = db.query(User).filter(User.username == u).first()
                if user and check_pw(p, user.password):
                    st.session_state.user_id = user.id
                    st.session_state.user_role = user.role
                    st.session_state.username = user.username
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            new_u = st.text_input("New Username", key="reg_u")
            new_p = st.text_input("New Password", type="password", key="reg_p")
            new_role = st.selectbox("Role", ["Member", "Admin"], key="reg_role")
            if st.button("Create Account", use_container_width=True):
                exists = db.query(User).filter(User.username == new_u).first()
                if exists:
                    st.warning("User already exists!")
                else:
                    user = User(username=new_u, password=hash_pw(new_p), role=new_role)
                    db.add(user)
                    db.commit()
                    st.success("Account created! Please log in.")

# --- MAIN APP UI ---
else:
    # Sidebar Navigation
    st.sidebar.title(f"👋 Hello, {st.session_state.username}")
    st.sidebar.info(f"Role: {st.session_state.user_role}")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.rerun()

    # 1. Dashboard Metrics
    st.title("🚀 Project Dashboard")
    all_tasks = db.query(Task).all()
    
    if all_tasks:
        df = pd.DataFrame([{
            'Status': t.status, 
            'Due': t.due_date
        } for t in all_tasks])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Tasks", len(df))
        m2.metric("Completed", len(df[df['Status'] == 'Done']))
        overdue = len(df[(df['Status'] != 'Done') & (df['Due'] < datetime.now())])
        m3.metric("Overdue", overdue, delta_color="inverse")
    
    st.divider()

    # 2. Admin Controls (Role-Based Access)
    if st.session_state.user_role == "Admin":
        with st.expander("🛠️ Admin Controls - Create & Assign"):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Create Project")
                p_name = st.text_input("Project Name")
                if st.button("Add Project"):
                    db.add(Project(name=p_name))
                    db.commit()
                    st.success(f"Project '{p_name}' added!")
                    st.rerun()
            
            with c2:
                st.subheader("Assign Task")
                projs = db.query(Project).all()
                users = db.query(User).all()
                
                t_name = st.text_input("Task Title")
                t_proj = st.selectbox("Select Project", [p.name for p in projs])
                t_user = st.selectbox("Assign To", [u.username for u in users])
                t_date = st.date_input("Due Date", min_value=datetime.now())
                
                if st.button("Assign"):
                    p_obj = db.query(Project).filter(Project.name == t_proj).first()
                    u_obj = db.query(User).filter(User.username == t_user).first()
                    new_task = Task(
                        title=t_name, 
                        project_id=p_obj.id, 
                        assigned_to=u_obj.id,
                        due_date=datetime.combine(t_date, datetime.min.time())
                    )
                    db.add(new_task)
                    db.commit()
                    st.success("Task assigned!")
                    st.rerun()

    # 3. Task Board (Interactive Status Tracking)
    st.header("📋 My Task Board")
    my_tasks = db.query(Task).filter(Task.assigned_to == st.session_state.user_id).all()
    
    if not my_tasks:
        st.info("You have no tasks assigned.")
    else:
        for t in my_tasks:
            with st.container():
                col_info, col_date, col_status = st.columns([3, 2, 2])
                
                # Highlight red if overdue
                display_title = f"**{t.title}**"
                if t.due_date < datetime.now() and t.status != "Done":
                    display_title += " ⚠️ OVERDUE"
                
                col_info.write(display_title)
                col_date.write(f"📅 {t.due_date.strftime('%Y-%m-%d')}")
                
                current_idx = ["Todo", "Doing", "Done"].index(t.status)
                new_status = col_status.selectbox(
                    "Update Status", 
                    ["Todo", "Doing", "Done"], 
                    index=current_idx, 
                    key=f"task_{t.id}"
                )
                
                if new_status != t.status:
                    t.status = new_status
                    db.commit()
                    st.rerun()
                st.divider()