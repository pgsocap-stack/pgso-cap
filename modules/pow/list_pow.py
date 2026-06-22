import streamlit as st
import db  # Ikonekta sa iyong db.py para sa history records

def render_pow_history_module():
    st.markdown("### 📋 POW (Program of Work) Masterlist History")
    st.caption("Dito makikita ang kasaysayan at buwanang talaan ng mga nagawang Program of Works (POW).")

    # 1. SEARCH & FILTERS CONTROLLERS
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Maghanap ng Proyekto (Project Name o Location):", placeholder="I-type dito...")
    with col_filter:
        status_filter = st.selectbox("📌 Filter sa Status:", ["All", "Active", "Pending", "Archived"])

    st.divider()

    # 2. PULL RECORDS FROM DATABASE
    try:
        # Hihingi ng data sa db.py (gaya ng ginagawa ng Tkinter treeview mo dati)
        if search_query:
            pow_records = db.search_pow_records(search_query)  # Bagong feature if ready na sa db
        else:
            pow_records = db.get_all_pow_history()  # Or kung anong tawag sa list function mo sa db.py
    except Exception:
        # Fallback Mock Data para hindi mag-crash ang UI kung inaayos pa ang db.py
        pow_records = [
            (101, "Proposed Concrete Pathway", "Zone 1, San Jose", "2026-06-15", "₱ 150,000.00"),
            (102, "Asphalt Overseeding & Repair", "Poblacion Road", "2026-06-18", "₱ 420,000.00")
        ]

    # 3. RENDER AS WEB DATA TABLE
    if not pow_records:
        st.info("Walang nahanap na Program of Work records sa kasalukuyan.")
        return

    # Isasalin natin ang dating Tkinter Treeview patungong interactive Streamlit Dataframe Table
    formatted_data = []
    for row in pow_records:
        formatted_data.append({
            "POW ID Reference": row[0],
            "Project Title / Name": row[1],
            "Project Location": row[2],
            "Date Encoded": row[3],
            "Estimated Budget": row[4]
        })

    # I-display ang table nang malinis sa web window
    st.dataframe(formatted_data, use_container_width=True, hide_index=True)

    # 4. ROW ACTION TRIGGERS (Katapat ng double-click o selection sa desktop)
    st.markdown("#### 🛠️ Record Actions")
    selected_pow_id = st.selectbox("Pumili ng POW ID na nais mong aksyunan:", [row[0] for row in pow_records])

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✏️ I-Edit ang Record", use_container_width=True, type="secondary"):
            st.session_state.current_selected_pow_id = selected_pow_id
            st.toast(f"Napili ang POW ID: {selected_pow_id}. Pwede mo na itong i-update, boss!", icon="ℹ️")
            # Dito mo pwede i-trigger ang open_edit_pow_modal() ng dashboard mo kung gusto mo
            
    with col_btn2:
        if st.button("🗑️ I-Delete ang Record", use_container_width=True):
            st.warning(f"Sigurado ka ba na nais mong burahin ang POW Reference: {selected_pow_id}?")
