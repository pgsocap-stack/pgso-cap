import streamlit as st
from datetime import datetime
import db  # Konektado sa iyong db.py layer

def render_pow_history_module():
    """
    Main module component para sa pag-render ng POW History Records.
    100% Web-ready gamit ang Native Streamlit Expanders at Dataframes.
    """
    st.markdown("## 📜 PROGRAM OF WORKS (POW) MASTERLIST HISTORY")
    st.write("Dito makikita ang kasaysayan ng lahat ng nagawang Program of Works na naka-grupo kada buwan.")

    # --- DATABASE DATA FETCHING ---
    try:
        records = db.get_all_pow_history()
    except Exception as e:
        st.error(f"❌ Database connection error: Hindi mahila ang kasaysayan ng POW. Detalye: {e}")
        return

    if not records:
        st.info("📭 Walang nahanap na kasaysayan ng POW sa database.")
        return

    # ==============================================================================
    # MONTH GROUPING ENGINE (Pagsasama-samahin ang records kada Buwan at Taon)
    # ==============================================================================
    monthly_groups = {}

    for row in records:
        pow_id = row[0]
        proj_name = row[1]
        location = row[2]
        grand_total = float(row[3])
        created_at = row[4]

        # DateTime Parsing (String o Object validation)
        if isinstance(created_at, str):
            dt_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        else:
            dt_obj = created_at

        month_bracket = dt_obj.strftime("%B %Y").upper()
        time_str = dt_obj.strftime("%H:%M:%S")
        date_str = dt_obj.strftime("%m/%d/%Y")
        
        project_combined_info = f"{proj_name}, {location}"

        if month_bracket not in monthly_groups:
            monthly_groups[month_bracket] = []

        # Pag-imbak sa array ng partikular na buwan
        monthly_groups[month_bracket].append({
            "POW ID": pow_id,
            "Project Name & Geolocation": project_combined_info,
            "Grand Total Amount": grand_total,
            "Time (HH:MM:SS)": time_str,
            "Date (MM/DD/YYYY)": date_str
        })

    # ==============================================================================
    # DYNAMIC WEB RENDERING (Looping sa bawat na-isave na buwan)
    # ==============================================================================
    for month_title, items in monthly_groups.items():
        
        # Gumawa ng isang magandang collapsible container kada buwan
        # (Katumbas ng Month Header Node natin sa Tkinter Treeview)
        with st.expander(f"📅 {month_title} — ({len(items)} Records Found)", expanded=True):
            
            # Konpigurasyon ng Column para sa magandang currency format at tamang lapad
            column_configuration = {
                "POW ID": st.column_config.NumberColumn("POW ID", format="%d", width="small"),
                "Project Name & Geolocation": st.column_config.TextColumn("Project Name & Geolocation", width="large"),
                "Grand Total Amount": st.column_config.NumberColumn("Grand Total Amount", format="₱%,.2f", width="medium"),
                "Time (HH:MM:SS)": st.column_config.TextColumn("Time (HH:MM:SS)", width="small"),
                "Date (MM/DD/YYYY)": st.column_config.TextColumn("Date (MM/DD/YYYY)", width="small")
            }
            
            # I-render ang data array sa isang ganap na interactive at responsive na Web Table
            st.dataframe(
                items,
                use_container_width=True,
                hide_index=False,  # Ipakita ang auto-number row grouping index
                column_config=column_configuration
            )
