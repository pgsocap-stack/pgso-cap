import streamlit as st
import os
import subprocess
from openpyxl import load_workbook
import db  # Koneksyon sa iyong database layer

def render_preview_pow_module():
    """
    Main component para sa pag-preview, pag-delete, at pag-edit ng Program of Works.
    Kasalukuyang pumapalit sa PreviewPowModule Tkinter class.
    """
    st.markdown("## 🏛️ PREVIEW SAVED PROGRAM OF WORK (POW)")

    # ==========================================================================
    # INITIALIZATION NG SESSION STATES (Para sa Edit at Selection tracking)
    # ==========================================================================
    if 'selected_pow_id' not in st.session_state:
        st.session_state.selected_pow_id = None
    if 'in_edit_mode' not in st.session_state:
        st.session_state.in_edit_mode = False
    if 'edit_items_list' not in st.session_state:
        st.session_state.edit_items_list = []

    # Kung pinindot ang 'Cancel Edit', ibalik sa normal view
    if st.session_state.in_edit_mode:
        render_edit_mode_interface()
        return

    # ==========================================================================
    # MAIN SPLIT VIEW LAYOUT (Kaliwa: Project List | Kanan: Item list on POW)
    # ==========================================================================
    left_col, right_col = st.columns([1, 2])

    # --------------------------------------------------------------------------
    # 👈 KALIWANG KOLUM: List of Projects
    # --------------------------------------------------------------------------
    with left_col:
        st.markdown("#### 📋 List of Projects")
        
        try:
            # Hinihila ang mga projects gamit ang db logic mo sa desktop
            projects = db.get_project_list()
        except Exception:
            projects = []

        if not projects:
            st.info("📭 Walang nahanap na proyekto sa database.")
            return

        # I-format ang listahan para sa web dropdown/list selector
        project_options = {f"ID {proj[0]} - {proj[1]}": proj for proj in projects}
        selected_project_key = st.radio(
            "Pumili ng Proyekto sa Listahan:",
            options=list(project_options.keys()),
            label_visibility="collapsed"
        )
        
        # Pagkuha ng mga detalye ng napiling proyekto
        selected_proj_data = project_options[selected_project_key]
        pow_id = selected_proj_data[0]
        project_name = selected_proj_data[1]
        location = selected_proj_data[2]
        
        st.session_state.selected_pow_id = pow_id

        st.markdown("---")
        
        # 🗑️ PINDUTAN: Delete Entire POW
        if st.button("❌ Delete Selected POW", type="secondary", use_container_width=True):
            # Two-step validation para sa web safety (imbes na biglang pop-up)
            st.session_state.show_delete_confirmation = True
            
        if st.session_state.get('show_delete_confirmation', False):
            st.warning(f"⚠️ Sigurado ka bang buburahin ang buong proyekto: **{project_name}**? Hindi na ito mababawi.")
            conf_col1, conf_col2 = st.columns(2)
            with conf_col1:
                if st.button("👍 Oo, Burahin", type="primary", use_container_width=True):
                    success = db.delete_pow_from_sql(pow_id)
                    if success:
                        st.toast("🗑️ Matagumpay na nabura ang buong POW record.", icon="✅")
                        st.session_state.selected_pow_id = None
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
            with conf_col2:
                if st.button("🔕 Kanselahin", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()

    # --------------------------------------------------------------------------
    # 👉 KANAN KOLUM: Item list on POW & Summary Bar
    # --------------------------------------------------------------------------
    with right_col:
        st.markdown(f"#### 📍 Location: `{location}`")
        
        # Hilaan ng mga aytem mula sa SQL base sa napiling ID
        associated_items = db.get_items_by_project(pow_id)
        
        # Pag-aayos ng itsura ng Table Grid (parang Treeview sa computer)
        table_data = []
        grand_total = 0.0
        
        for idx, item in enumerate(associated_items, start=1):
            qty = float(item[0])
            unit = item[1]
            name = item[2]
            price = float(item[3])
            total = qty * price
            grand_total += total
            
            table_data.append({
                "#": idx,
                "Qty": qty,
                "Unit": unit,
                "Item Description": name,
                "Unit Price": f"P {price:,.2f}",
                "Total Price": f"P {total:,.2f}"
            })
            
        st.dataframe(table_data, use_container_width=True, hide_index=True)
        
        # 💰 SUMMARY BAR SA ILALIM NG TABLE
        st.info(f"### **PROJECT TOTAL COST:** `P {grand_total:,.2f}`")
        
        # --- LOWER CONTAINER BUTTONS ---
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            # Pindutan papunta sa layout engine na ginawa natin kanina
            if st.button("👁️ Preview Data Layout", type="primary", use_container_width=True):
                # Ini-inject ang view variable para lumipat sa generator tab
                st.session_state.active_view = "Preview POW Records"
                st.rerun()
                
        with btn_col2:
            if st.button("✏️ Edit POW Record", use_container_width=True):
                # I-setup ang session state bago lumipat sa Edit Screen
                st.session_state.edit_project_name = project_name
                st.session_state.edit_location = location
                # FORMAT: [qty, unit, description, price, orig_desc]
                st.session_state.edit_items_list = [
                    [item[0], item[1], item[2], float(item[3]), item[2]] for item in associated_items
                ]
                st.session_state.in_edit_mode = True
                st.rerun()


# ==============================================================================
# ✏️ INTERNAL MODULE: THE EDIT MODE INTERFACE (Immersed Modal Emulation)
# ==============================================================================
def render_edit_mode_interface():
   
def render_edit_mode_interface():
    st.markdown("### ✏️ EDIT MODE - Update POW Record")
    
    # 🌟 KULANG 1: HAKBANG PAPUNTANG MASTER LIST IMPORT (Dito mo isaksak sa pinakataas)
    try:
        from master_list import ITEM_MASTER_LIST
    except ImportError:
        try:
            from master_items import ITEM_MASTER_LIST
        except ImportError:
            try:
                from modules.pow.master_list import ITEM_MASTER_LIST
            except Exception as e:
                st.error(f"⚠️ Hindi mahanap ang master_list.py sa GitHub: {e}")
                ITEM_MASTER_LIST = []

    # I-convert para maging dictionary finder
    master_pool = {item[0]: {"unit": item[1], "price": float(item[2])} for item in ITEM_MASTER_LIST}

    # --- UPPER FRAME: DETAILS ---
    with st.container(border=True):
        st.markdown("**Details of POW**")
        edit_proj_name = st.text_input("Project Title / Name:", value=st.session_state.edit_project_name)
        edit_location = st.text_input("Project Location:", value=st.session_state.edit_location)

    # --- MIDDLE FRAME: TABLE PREVIEW ---
    st.markdown("**List of Items (Current Session)**")
    display_edit_rows = []
    for idx, row in enumerate(st.session_state.edit_items_list):
        display_edit_rows.append({
            "Line": idx + 1,
            "QTY": row[0],
            "UNIT": row[1],
            "ITEM DESCRIPTION": row[2],
            "UNIT PRICE": f"{row[3]:.2f}",
            "ORIGINAL NAME (TRACER)": row[4]
        })
    st.dataframe(display_edit_rows, use_container_width=True, hide_index=True)


    # ==============================================================================
    # 🏛️ HAKBANG 2: ANG SMART DROPDOWN TEXT BOX INTERFACE (Yung Form sa Baba)
    # ==============================================================================
    dropdown_options = list(master_pool.keys())
    dropdown_options.insert(0, "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...")

    st.markdown("### ➕ Magdagdag ng Bagong Aytem sa POW")

    with st.container(border=True):
        # 🔍 ANG SMART SEARCH TEXT BOX/DROPDOWN
        selected_item = st.selectbox(
            "Mag-search o Pumili ng Materyales (Item Description):",
            options=dropdown_options,
            index=0
        )
        
        default_unit = ""
        default_price = 0.00
        chosen_desc = ""
        
        if selected_item != "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...":
            chosen_desc = selected_item
            default_unit = master_pool[selected_item]["unit"]
            default_price = master_pool[selected_item]["price"]

        # Grid layout para magkakatabi ang mga input fields
        col1, col2, col3 = st.columns([1, 1, 1.5])
        
        with col1:
            input_qty = st.number_input("QTY (Dami):", min_value=0.0, step=1.0, value=0.0, key="enc_qty")
        with col2:
            input_unit = st.text_input("UNIT:", value=default_unit, key="enc_unit")
        with col3:
            input_price = st.number_input("UNIT PRICE (Presyo):", min_value=0.0, step=0.01, value=default_price, key="enc_price")

        if selected_item == "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...":
            final_description = st.text_input("Isulat ang Pangalan ng Custom Material dito, boss:", key="enc_custom_desc")
        else:
            final_description = chosen_desc

        # --- BUTTON PARA SA PAGPAPASOK SA KASALUKUYANG SESSION LIST ---
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Isama sa Listahan ng Materyales", use_container_width=True, type="primary"):
            if not final_description.strip():
                st.error("⚠️ Error: Hindi pwedeng iwanang blangko ang Description ng materyales, boss!")
            elif input_qty <= 0:
                st.warning("⚠️ Paalala: Siguraduhing ang QTY ay higit sa 0 para ma-compute ang amount.")
            else:
                if 'edit_items_list' not in st.session_state:
                    st.session_state.edit_items_list = []
                    
                st.session_state.edit_items_list.append([
                    float(input_qty), 
                    input_unit.strip(), 
                    final_description.strip(), 
                    float(input_price), 
                    final_description.strip()
                ])
                st.toast(f"🎉 Naidagdag na sa listahan: {final_description.strip()}", icon="✅")
                st.rerun()
