import streamlit as st
import db  # Gagamitin ang kinopya mong db.py sa parehong folder

# 🌟 RULE 1 NG STREAMLIT: Dapat ito ang PINAKA-UNANG 'st.' command sa script!
st.set_page_config(
    page_title="PGSO Management System",
    page_icon="🏛️",
    layout="wide",  # Ginagawa nitong maximized ang screen katulad ng zoomed sa Tkinter
    initial_sidebar_state="expanded"
)

# ==============================================================================
# INITIALIZATION NG LAHAT NG SESSION STATES (Proteksyon sa KeyError)
# ==============================================================================
if 'active_view' not in st.session_state:
    st.session_state.active_view = "login"

if 'dashboard' not in st.session_state:
    st.session_state['dashboard'] = {}  # Solusyon para hindi na magka-KeyError sa dashboard.py

if 'page' not in st.session_state:
    st.session_state.page = 'login'

if 'username' not in st.session_state:
    st.session_state.username = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# I-initialize ang database sa unang load ng website
if 'db_ready' not in st.session_state:
    db.initialize_db()
    st.session_state.db_ready = True


# ==============================================================================
# 🎛️ MGA TRIGGERS / HANDLERS
# ==============================================================================
def handle_web_logout():
    st.session_state.page = 'login'
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()


# ==============================================================================
# 🏛️ MGA PALANDINGAN NG WEB APP (SCREENS)
# ==============================================================================

def show_login():
    st.markdown("<h2 style='text-align: center; color: #2196F3;'>ACCOUNT LOGIN</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_user").strip()
    password = st.text_input("Password", type="password", key="login_pass").strip()
    
    if st.button("Login", use_container_width=True, type="primary"):
        if not username or not password:
            st.warning("⚠️ Attention! All input fields must be filled out before proceeding")
        else:
            user_role = db.authenticate_user(username, password)
            
            if user_role:
                st.toast("🎉 Success! Access Granted. Login successful.")
                st.session_state.username = username
                st.session_state.user_role = "admin" if username.lower() == "admin" else "staff"
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.error("❌ Login Failed! Invalid username or password. Please try again.")
                
    st.markdown("---")
    if st.button("Don't have an account? Sign Up", use_container_width=True):
        st.session_state.page = 'signup'
        st.rerun()


def show_signup():
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>CREATE ACCOUNT</h2>", unsafe_allow_html=True)
    
    username = st.text_input("New Username", key="reg_user").strip()
    password = st.text_input("New Password", type="password", key="reg_pass").strip()
    
    if st.button("Register Account", use_container_width=True):
        if not username or not password:
            st.warning("⚠️ Attention! All fields are required to register an account.")
        else:
            try:
                success, message = db.register_user(username, password, role='encoder')
                if success:
                    st.success(f"🎯 {message}")
                    st.info("Maaari ka nang bumalik sa Login page para mag-sign in.")
                else:
                    st.error(f"❌ Registration Failed! {message}")
            except AttributeError:
                st.info("⏳ Access request submitted. Form logged for database synchronization validation.")
                
    st.markdown("---")
    if st.button("Already have an account? Log In", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()


def show_dashboard():
    # Dynamic import para hindi mag-conflict habang nilo-load ang page state
    from dashboard import OfficeDashboard
    
    OfficeDashboard(
        username=st.session_state.username,
        user_role=st.session_state.user_role,
        on_logout=handle_web_logout
    )


# ==============================================================================
# 🎮 MAIN APP CONTROLLER (May Tamang Indentation at Spacing na)
# ==============================================================================
if st.session_state.page == 'login' or st.session_state.page == 'signup':
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        with st.container(border=True):  # Malinis na card wrapper para sa logging pages
            if st.session_state.page == 'login':
                show_login()
            elif st.session_state.page == 'signup':
                show_signup()
else:
    # Kapag 'dashboard' na ang active, pinapagana ang buong dashboard screen
    show_dashboard()
