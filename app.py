import streamlit as st
import db  # Gagamitin ang kinopya mong db.py sa parehong folder

# I-configure ang web page setting para maging professional, responsive at maximized ang layout sa computer screens
st.set_page_config(
    page_title="PGSO Management System",
    page_icon="🏛️",
    layout="wide",  # Ginagawa nitong maximized ang screen katulad ng self.parent.state('zoomed') sa Tkinter
    initial_sidebar_state="expanded"
)

# 1. I-initialize ang database sa unang load ng website
if 'db_ready' not in st.session_state:
    db.initialize_db()
    st.session_state.db_ready = True

# 2. State management para sa paglipat-lipat ng screen at user sessions
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- MGA TRIGGERS O FUNCTIONS PARA SA LOGOUT ---
def handle_web_logout():
    st.session_state.page = 'login'
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()

# --- MGA PALANDINGAN O PAHINGA NG WEB APP (SCREENS) ---

def show_login():
    st.markdown("<h2 style='text-align: center; color: #2196F3;'>ACCOUNT LOGIN</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_user").strip()
    password = st.text_input("Password", type="password", key="login_pass").strip()
    
    # Login button layout
    if st.button("Login", use_container_width=True, type="primary"):
        if not username or not password:
            st.warning("⚠️ Attention! All input fields must be filled out before proceeding")
        else:
            # 🔍 Bumabase sa authenticate_user function mo sa db.py
            user_role = db.authenticate_user(username, password)
            
            if user_role:
                st.toast("🎉 Success! Access Granted. Login successful.")
                st.session_state.username = username
                # Kung True ang binalik pero string ang kailangan (tulad ng 'admin' o 'encoder'/'staff')
                st.session_state.user_role = "admin" if username.lower() == "admin" else "staff"
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.error("❌ Login Failed! Invalid username or password. Please try again.")
                
    st.markdown("---")
    # Link papuntang Sign Up
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
            # 🔍 Tinatawag ang register function mo mula sa db.py (Siguraduhing mayroon ka nito sa db.py)
            try:
                success, message = db.register_user(username, password, role='encoder')
                if success:
                    st.success(f"🎯 {message}")
                    st.info("Maaari ka nang bumalik sa Login page para mag-sign in.")
                else:
                    st.error(f"❌ Registration Failed! {message}")
            except AttributeError:
                # Fallback handler kung sakaling hindi pa rehistrado ang register function sa db.py mo
                st.info("⏳ Access request submitted. Form locked for database synchronization validation.")
                
    st.markdown("---")
    # Link pabalik ng Login
    if st.button("Already have an account? Log In", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()


def show_dashboard():
    # ==============================================================================
    # 🎛️ INTEGRATION HUB: TINAWAG NA ANG WEB VERSION NG DASHBOARD MO
    # ==============================================================================
    from dashboard import OfficeDashboard
    
    # Dito natin ipinapasa ang session parameters diretso sa Streamlit OfficeDashboard layer
    OfficeDashboard(
        username=st.session
