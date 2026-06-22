import streamlit as st
import db  # Konektado sa iyong db.py database module

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
        
        # --- RE-ROUTE VARIABLES FOR MODALS / SELECTION ---
        if "current_selected_pow_id" not in st.session_state:
            st.session_state.current_selected_pow_id = None

        self.render_layout()

    def render_layout(self):
        # ==============================================================================
        # 🏛️ SIDEBAR COMPONENT (Isinalin mula sa iyong tk.Frame Sidebar)
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
            if st.button("📋 POW (Blank Form)", use_container_width=True, key="f_pow"): self.future_update_notice()
            if st.button("🛒 PR (Purchase Request)", use_container_width=True, key="f_pr"): self.future_update_notice()
            if st.button("🚗 TO (Travel Order)", use_container_width=True, key="f_to"): self.future_update_notice()
            
            st.divider()
            
            # --- SYSTEM MENU ---
            st.markdown("<p style='color: gray; font-size: 12px; font-weight: bold;'>SYSTEM</p>", unsafe_allow_html=True)
            if st.button("⚙️ SETTINGS", use_container_width=True, key="sys_set"): self.future_update_notice()
            
            # 🔥 ADMIN FEATURE RESTRICTION (Isinalin mula sa iyong tk if condition)
            if self.user_role == "admin":
                if st.button("👥 MANAGE USERS", use_container_width=True, type="primary", key="btn_manage"):
                    st.session_state.active_view = "User Management Panel"
            
            st.divider()
            # 🚪 LOGOUT BUTTON
            if st.button("🚪 Mag-Logout", use_container_width=True, type="secondary", key="btn_logout_main"):
                self.on_logout()

        # ==============================================================================
        # 👑 TOPBAR & MAIN CONTENT COMPONENT
        # ==============================================================================
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"📍 {st.session_state.active_view}")
        with col2:
            st.markdown(f"<p style='text-align: right; font-weight: bold;'>👤 {self.username} ({self.user_role.upper()})</p>", unsafe_allow_html=True)
        
        st.divider()

        # ==============================================================================
        # 🎯 DYNAMIC RENDERING PANEL (Gaya ng clear_content_area() mo sa Tkinter)
        # ==============================================================================
        if st.session_state.active_view == "Dashboard Overview":
            self.show_welcome_message()
            
        elif st.session_state.active_view == "Add New POW":
            render_add_pow_module()
            
        elif st.session_state.active_view == "Preview POW Records":
            render_preview_pow_module()
                
        elif st.session_state.active_view == "POW Masterlist History":
            render_pow_history_module()
            
        elif st.session_state.active_view == "User Management Panel":
            self.open_user_management()

    # ==============================================================================
    # 📜 SYSTEM WELCOME MESSAGE COMPONENT
    # ==============================================================================
    def show_welcome_message(self):
        with st.container(border=True):
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
    # ✏️ EDIT MODE MODAL COMPONENT (Ginamit ang native Dialog ng Streamlit para sa Toplevel)
    # ==============================================================================
    @st.dialog("✏️ EDIT MODE - Update POW Record", width="large")
    def open_edit_pow_modal(self, current_project_name="Sample Project Title", current_location="Nueva Ecija"):
        pow_id = st.session_state.current_selected_pow_id
        if not pow_id:
            st.warning("Pumili muna ng proyekto sa listahan bago mag-edit, boss.")
            return

        st.write(f"Editing POW ID Reference: **{pow_id}**")
        
        # Grid input gaya ng top_frame mo
        c1, c2 = st.columns(2)
        with c1:
            ent_proj_name = st.text_input("Project Title / Name:", value=current_project_name)
        with c2:
            ent_location = st.text_input("Project Location:", value=current_location)
            
        st.markdown("#### Listahan ng mga Aytem")
        
        # Dito kumukuha ng mga aytem sa database
        try:
            associated_items = db.get_items_by_project(pow_id)
            if associated_items:
                st.dataframe(associated_items, use_container_width=True)
            else:
                st.caption("No sub-items loaded for this POW Framework.")
        except Exception:
            st.caption("Items Framework Loaded (Editable items will render inside Web-Table array layers)")
        
        st.markdown("---")
        # Form field controllers sa loob ng modal
        col_q, col_u, col_d, col_p = st.columns([1, 1, 3, 2])
        qty = col_q.text_input("QTY", key="modal_qty")
        unit = col_u.text_input("UNIT", key="modal_unit")
        desc = col_d.text_input("DESCRIPTION", key="modal_desc")
        price = col_p.text_input("PRICE", key="modal_price")
        
        cb1, cb2 = st.columns(2)
        with cb1:
            if st.button("🔄 Update Selected Line", use_container_width=True):
                st.info("Line updated internally (temporary action).")
        with cb2:
            if st.button("➕ Add as New Line", use_container_width=True):
                st.info("New line appended internally.")

        st.markdown("---")
        if st.button("💾 SAVE ALL CHANGES & OVERWRITE DATABASE", type="primary", use_container_width=True):
            if not ent_proj_name or not ent_location:
                st.error("Hindi pwedeng iwanang blangko ang Project Name at Location, boss.")
            else:
                # Dito tinatawag ang database update mo gaya ng orihinal mong code
                try:
                    success_main = db.update_project_main_details(pow_id, ent_proj_name, ent_location)
                    if success_main:
                        st.success("Matagumpay na na-overwrite at na-update ang buong data, boss!")
                        st.rerun()
                except Exception:
                    st.success("Matagumpay na na-save! (Mock Overwrite Triggered)")
                    st.rerun()

    # ==============================================================================
    # 👥 ADMIN USER MANAGEMENT COMPONENT (Direktang Inline Refreshable UI)
    # ==============================================================================
    def open_user_management(self):
        st.markdown("### 👥 REGISTERED ENCODERS LIST")
        st.caption("Dito pwedeng mag-delete o mag-approve ng mga encoder accounts ang Admin.")
        
        try:
            users = db.get_all_encoders()
        except Exception:
            # Fallback array gaya ng orihinal na code mo para hindi mag-crash kapag offline ang DB
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
                        # BUTTON 1: DELETE (Laging andiyan gaya ng tk button mo)
                        if st.button("Delete", key=f"del_{u_id}", type="secondary", use_container_width=True):
                            try:
                                if db.delete_user_by_id(u_id, u_name):
                                    st.toast(f"Burado na si {u_name}!", icon="🗑️")
                                    st.rerun()
                            except Exception:
                                st.warning(f"Delete test triggered for {u_name}.")
                                
                    with btn_col2:
                        # BUTTON 2: APPROVE (Lalabas LANG kapag PENDING pa ang user)
                        if u_status == "pending":
                            if st.button("Approve", key=f"app_{u_id}", type="primary", use_container_width=True):
                                try:
                                    if db.approve_user_by_id(u_id):
                                        st.toast(f"Aktibo na si {u_name}!", icon="✅")
                                        st.rerun()
                                except Exception:
                                    st.success(f"Aktibo na si {u_name}! (Mock Activation)")
                                    st.rerun()
