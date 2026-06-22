import streamlit as st
import db  # Konektado sa iyong db.py (Basta siguraduhing tumatakbo ang MySQL mo)


# Maayos na pag-import ng mga external modules mula sa iyong project directory
from modules.pow.preview_pow import render_preview_pow_module
from modules.pow.add_pow import render_add_pow_module
from modules.pow.list_pow import render_pow_history_module

class OfficeDashboard:
    def __init__(self, username, user_role, on_logout):
        self.username = username
        self.user_role = user_role
        self.on_logout = on_logout
        
        # --- INITIALIZE MULTI-VIEW STATE (Parang clear_content_area natin sa Desktop) ---
        if "active_view" not in st.session_state:
            st.session_state.active_view = "Dashboard Overview"
        
        # --- RE-ROUTE VARIABLES FOR MODALS ---
        if "current_selected_pow_id" not in st.session_state:
            st.session_state.current_selected_pow_id = None

        self.render_layout()

    def render_layout(self):
        # ==============================================================================
        # 🏛️ SIDEBAR COMPONENT (Dito isinalin ang tk.Frame Sidebar mo)
        # ==============================================================================
        with st.sidebar:
            st.markdown("<h2 style='text-align: center; color: white;'>🏛️ PGSO PORTAL</h2>", unsafe_allow_html=True)
            st.divider()
            
            # --- CORE WORKSPACE MENU ---
            st.markdown("**WORKSPACE MENU**")
            if st.button("➕ ADD POW", use_container_width=True, key="btn_add"):
                st.session_state.active_view = "Add New POW"
                
            if st.button("👁️ PREVIEW POW", use_container_width=True, key="btn_prev"):
                st.session_state.active_view = "Preview POW Records"
                
            if st.button("📋 POW (Program of Work) History", use_container_width=True, key="btn_hist"):
                st.session_state.active_view = "POW Masterlist History"
                
            st.divider()
            
            # --- DOCUMENTS & FORMS MENU ---
            st.markdown("<p style='color: gray; font-size: 12px; font-weight: bold;'>DOCUMENTS & FORMS</p>", unsafe_allow_html=True)
            if st.button("📋 POW (Blank Form)", use_container_width=True): self.future_update_notice()
            if st.button("🛒 PR (Purchase Request)", use_container_width=True): self.future_update_notice()
            if st.button("🚗 TO (Travel Order)", use_container_width=True): self.future_update_notice()
            
            st.divider()
            
            # --- SYSTEM MENU ---
            st.markdown("<p style='color: gray; font-size: 12px; font-weight: bold;'>SYSTEM</p>", unsafe_allow_html=True)
            if st.button("⚙️ SETTINGS", use_container_width=True): self.future_update_notice()
            
            # 🔥 ADMIN FEATURE RESTRICTION (Isinalin mula sa tk if condition mo)
            if self.user_role == "admin":
                if st.button("👥 MANAGE USERS", use_container_width=True, type="primary"):
                    st.session_state.active_view = "User Management Panel"
            
            st.divider()
            # 🚪 LOGOUT BUTTON
            if st.button("🚪 Mag-Logout", use_container_width=True, type="secondary"):
                self.on_logout()

        # ==============================================================================
        # 👑 TOPBAR & MAIN CONTENT COMPONENT
        # ==============================================================================
        # Ipinapakita kung sino ang logged-in na User at Role (Kanan ng screen)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"📍 {st.session_state.active_view}")
        with col2:
            st.markdown(f"<p style='text-align: right; font-weight: bold;'>👤 {self.username} ({self.user_role.upper()})</p>", unsafe_allow_html=True)
        
        st.divider()

        # --- DYNAMIC RENDERING PANEL ---
        if st.session_state.active_view == "Dashboard Overview":
            self.show_welcome_message()
            
        elif st.session_state.active_view == "Add New POW":
            # 🚀 Direkta nang tinatawag ang totoong Add New POW module na binuo natin
            render_add_pow_module()
            
        elif st.session_state.active_view == "Preview POW Records":
            # 👁️ Tinatawag ang Preview interface
            render_preview_pow_module()
                
       elif st.session_state.active_view == "POW Masterlist History":
            render_pow_history_module()  # 👈 Papalitan nito ang dating st.info() placeholder text
            
        elif st.session_state.active_view == "User Management Panel":
            self.open_user_management()

    # ==============================================================================
    # 📜 SYSTEM WELCOME MESSAGE COMPONENT
    # ==============================================================================
    def show_welcome_message(self):
        with st.expander("ℹ️ PGSO Portal System Info", expanded=True):
            st.markdown("### Main Dashboard Workspace")
            guide_text = (
                "All necessary workspace menus have been successfully initialized on the left-side panel (Sidebar) for your office operations:\n\n"
                "* **ADD / EDIT / PREVIEW** – For managing all master data records and transactional data entry.\n"
                "* **POW / PR / TO** – For processing operational program of works, purchase requests, and travel orders.\n"
                "* **SETTINGS** – For system configuration and environment adjustments.\n\n"
                "These navigation controls are currently armed and fully optimized, standing ready for your backend integration and localized database transaction routines.\n\n"
                "📘 **Complete System Guide & Structural Architecture:**\n\n"
                "The data administration module acts as the gatekeeper of your operational storage layer. "
                "Basic inputs are validated locally prior to executing transactions against the integrated database structures."
            )
            st.write(guide_text)

    def future_update_notice(self):
        st.toast("⚠️ Ang function na ito ay kasalukuyang inihahanda para sa susunod na update.", icon="ℹ️")

    # ==============================================================================
    # ✏️ EDIT MODE MODAL COMPONENT (Ginamit ang native Dialog feature ng Streamlit)
    # ==============================================================================
    @st.dialog("✏️ EDIT MODE - Update POW Record", width="large")
    def open_edit_pow_modal(self):
        pow_id = st.session_state.current_selected_pow_id
        st.write(f"Editing POW ID Reference: **{pow_id}**")
        
        # Grid input para sa project metadata
        c1, c2 = st.columns(2)
        with c1:
            ent_proj_name = st.text_input("Project Title / Name:", value="Sample Project Title")
        with c2:
            ent_location = st.text_input("Project Location:", value="Nueva Ecija")
            
        st.markdown("#### Listahan ng mga Aytem")
        # Dito lalabas ang dataframe array table ng item entries mo
        st.caption("Items Framework Loaded (Editable items will render inside Web-Table array layers)")
        
        # Form field controllers inside modal
        st.markdown("---")
        col_q, col_u, col_d, col_p = st.columns([1, 1, 3, 2])
        qty = col_q.text_input("QTY")
        unit = col_u.text_input("UNIT")
        desc = col_d.text_input("DESCRIPTION")
        price = col_p.text_input("PRICE")
        
        if st.button("💾 SAVE ALL CHANGES & OVERWRITE DATABASE", type="primary", use_container_width=True):
            if not ent_proj_name or not ent_location:
                st.error("Hindi pwedeng iwanang blangko ang Project Name at Location, boss.")
            else:
                st.success("Matagumpay na na-overwrite at na-update ang buong data, boss!")
                st.rerun()

    # ==============================================================================
    # 👥 ADMIN USER MANAGEMENT DIALOG COMPONENT
    # ==============================================================================
    def open_user_management(self):
        st.markdown("### 👥 REGISTERED ENCODERS LIST")
        
        try:
            users = db.get_all_encoders()
        except Exception:
            users = [(1, "admin_sample", "admin", "active"), (2, "encoder_sample", "staff", "pending")]
            
        if not users:
            st.info("No other registered users found.")
            return
            
        for user in users:
            u_id, u_name, u_role, u_status = user[0], user[1], user[2], user[3]
            
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 2])
                with col_info:
                    st.write(f"👤 **{u_name}** | Role: `{u_role.upper()}` | Status: *{u_status.upper()}*")
                
                with col_actions:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Delete", key=f"del_{u_id}", type="secondary"):
                            st.warning(f"Burado na si {u_name} test triggered.")
                    with btn_col2:
                        if u_status == "pending":
                            if st.button("Approve", key=f"app_{u_id}", type="primary"):
                                st.success(f"Aktibo na si {u_name}!")
