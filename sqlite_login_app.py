
import streamlit as st
import sqlite3

# ---------- Database Setup ----------
def create_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_user_table()

# ---------- Signup ----------
def signup():
    st.title("📝 Signup")
    new_user = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")

    if st.button("Create Account"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (new_user,))
        if c.fetchone():
            st.warning("🚫 Username already exists.")
        else:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_password))
            conn.commit()
            st.success("✅ Account created! Please login.")
        conn.close()

# ---------- Login ----------
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()
        conn.close()

        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ---------- Logout ----------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ---------- Main App ----------
def main_app():
    st.title("🎉 Welcome to BillBuster!")
    st.write("This is your main app. Customize here.")

# ---------- Session State ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- Auth Logic ----------
if st.session_state.logged_in:
    st.sidebar.success(f"👋 Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
    main_app()
else:
    auth_page = st.sidebar.radio("Choose", ["Login", "Signup"])
    if auth_page == "Login":
        login()
    else:
        signup()
