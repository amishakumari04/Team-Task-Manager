import streamlit as st
import bcrypt
import pandas as pd
from models import SessionLocal, User, Project, Task
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Team Task Manager", layout="wide", initial_sidebar_state="expanded")
db = SessionLocal()

# --- CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTH HELPERS ---
def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_pw(pw, hashed): return bcrypt.checkpw(pw.encode(), hashed.encode())

if 'user' not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION FLOW ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🚀 Team Task Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Secure Collaboration & Task Tracking</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Login"):
                user = db.query(User).filter(User.username == u).first()
                if user and check_pw(p, user.password):
                    st.session_state.user = user
                    st.success("Login Successful!")
                    st.rerun()
                else: st.error("Invalid Credentials")
        
        with tab2:
            nu = st.text_input("Choose Username")
            np = st.text_input("Choose Password", type="password")
            role = st.selectbox("Assign Role", ["Member", "Admin"])
            if st.button("Create Account"):
                if not db.query(User).filter(User.username == nu).first():
                    db.add(User(username=nu, password=hash_pw(np), role=role))
                    db.commit()
                    st.success("Account created! Please switch to Login tab.")
                else: st.error("Username already taken.")

# --- DASHBOARD FLOW ---
else:
    curr_user = st.session_state.user
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    st.sidebar.info(f"User: **{curr_user.username}** \n\n Role: **{curr_user.role}**")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("🚀 Project Dashboard")

    # --- METRICS (Filtered for logged-in user) ---
    my_tasks = db.query(Task).filter(Task.assigned_to == curr_user.id).all()
    
    col1, col2, col3 = st.columns(3)
    total = len(my_tasks)
    completed = len([t for t in my_tasks if t.status == 'Done'])
    overdue = len([t for t in my_tasks if t.status != 'Done' and t.due_date < datetime.now()])
    
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Overdue", overdue, delta_color="inverse")
    
    st.divider()

    # --- ADMIN CONTROLS ---
    if curr_user.role == "Admin":
        with st.expander("🛠️ Admin Controls - Create & Assign"):
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Create Project")
                p_name = st.text_input("Project Name")
                if st.button("Add Project"):
                    if p_name:
                        db.add(Project(name=p_name))
                        db.commit()
                        st.success(f"Project '{p_name}' Added!")
                        st.rerun()

            with c2:
                st.subheader("Assign Task")
                t_title = st.text_input("Task Title")
                
                # Fetch fresh data for dropdowns
                projs = db.query(Project).all()
                users = db.query(User).all()
                
                p_map = {p.name: p.id for p in projs}
                u_map = {u.username: u.id for u in users}
                
                sel_p = st.selectbox("Select Project", list(p_map.keys()))
                sel_u = st.selectbox("Assign To", list(u_map.keys()))
                
                if st.button("Assign Task"):
                    if t_title:
                        new_t = Task(title=t_title, project_id=p_map[sel_p], assigned_to=u_map[sel_u])
                        db.add(new_t)
                        db.commit()
                        st.success("Task Successfully Assigned!")
                        st.rerun()

    # --- TASK BOARD ---
    st.subheader("📋 My Task Board")
    if not my_tasks:
        st.info("No tasks assigned to you yet.")
    else:
        for t in my_tasks:
            with st.container():
                tc1, tc2, tc3 = st.columns([3, 2, 1])
                tc1.write(f"**{t.title}**")
                tc2.write(f"📁 {t.project.name if t.project else 'N/A'}")
                
                # Dynamic Status Update
                status_options = ["Todo", "Doing", "Done"]
                new_status = tc3.selectbox(
                    "Change Status", 
                    status_options, 
                    index=status_options.index(t.status), 
                    key=f"task_{t.id}"
                )
                
                if new_status != t.status:
                    t.status = new_status
                    db.commit()
                    st.rerun()
                st.divider()
