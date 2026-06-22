import streamlit as st
import os
import subprocess
from openpyxl import load_workbook
import db  # Koneksyon sa iyong database layer

def render_add_pow_module():
    """
    Main component para sa paglikha at pag-save ng bagong Program of Works (POW).
    100% Web-ready, walang Tkinter dependencies, at compatible sa cloud.
    """
    st.markdown("## 🏗️ CREATE NEW PROGRAM OF WORK (POW)")

    # ==========================================================================
    # INITIALIZATION NG SESSION STATES PARA SA BAGONG PROYEKTO
    # ==========================================================================
    if 'new_items_list' not in st.session_state:
        st.session_state.new_items_list = []  # Listahan ng mga aytem para sa kasalukuyang session

    # --- UPPER FRAME: PROYEKTO DETAILS ---
    with st.container(border=True):
        st.markdown("#### 📝 General Project Details")
        proj_col1, proj_col2 = st.columns(2)
        with proj_col1:
            project_name = st.text_input("Project Title / Name:", placeholder="Hal: Concreting of Barangay Road...")
        with proj_col2:
            location = st.text_input("Project Location:", placeholder="Hal: Zone 4, San Fernando...")

    # --- MIDDLE FRAME: LIVE TABLE PREVIEW ---
    st.markdown("#### 📋 Current Items in POW")
    display_new_rows = []
    grand_total = 0.0

    for idx, row in enumerate(st.session_state.new_items_list):
        qty = float(row[0])
        price = float(row[3])
        total = qty * price
        grand_total += total
        
        display_new_rows.append({
            "Line": idx + 1,
            "QTY": qty,
            "UNIT": row[1],
            "ITEM DESCRIPTION": row[2],
            "UNIT PRICE": f"P {price:,.2f}",
            "TOTAL PRICE": f"P {total:,.2f}"
        })

    if display_new_rows:
        st.dataframe(display_new_rows, use_container_width=True, hide_index=True)
        # 💰 SUMMARY BAR
        st.info(f"### **ESTIMATED TOTAL COST:** `P {grand_total:,.2f}`")
    else:
        st.info("📭 Blangko pa ang listahan ng mga aytem. Gumamit ng form sa ibaba para magdagdag.")

    # --- LOWER FRAME: FORM INPUTS PARA SA PAGDAGDAG NG ROW ---
    with st.container(border=True):
        st.markdown("#### ➕ Add Item to List")
        
        f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 3, 1.5])
        with f_col1:
            form_qty = st.text_input("QTY:", value="", placeholder="0", key="add_qty")
        with f_col2:
            form_unit = st.text_input("UNIT:", value="", placeholder="pcs/bags", key="add_unit")
        with f_col3:
            form_desc = st.text_input("ITEM DESCRIPTION:", value="", placeholder="Pangalan o detalye ng materyales...", key="add_desc")
        with f_col4:
            form_price = st.text_input("UNIT PRICE:", value="", placeholder="0.00", key="add_price")

        # Row Control Buttons
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("➕ Add Line into Session", type="secondary", use_container_width=True):
                if not form_desc.strip():
                    st.error("⚠️ Paki-sulat ang Description ng aytem, boss.")
                else:
                    try:
                        q_val = float(form_qty) if form_qty else 0.0
                        p_val = float(form_price) if form_price else 0.0
                        
                        # I-save sa listahan: [qty, unit, description, price, orig_desc]
                        # Dahil bagong gawa ito, ang orig_desc ay kapareho lang ng description
                        st.session_state.new_items_list.append([
                            q_val, form_unit.strip(), form_desc.strip(), p_val, form_desc.strip()
                        ])
                        st.toast("Item added successfully!", icon="➕")
                        st.rerun()
                    except ValueError:
                        st.error("❌ Dapat valid na numero ang ilalagay sa QTY at PRICE, boss.")
                        
        with action_col2:
            if st.button("🧹 Clear Current Session List", use_container_width=True):
                st.session_state.new_items_list = []
                st.toast("List cleared!", icon="🗑️")
                st.rerun()

    # --- FINAL SUBMIT & SAVE PIPELINE ---
    st.markdown("---")
    save_col1, save_col2 = st.columns([2, 1])
    
    with save_col1:
        if st.button("💾 SAVE NEW POW RECORD & SYNC TO DATABASE", type="primary", use_container_width=True):
            excel_path = r"G:\jrm\master_items.xlsx"
            
            # Validations bago mag-save
            if not project_name.strip() or not location.strip():
                st.error("❌ Huwag iwanang blangko ang Project Title at Location, boss.")
                return
            if not st.session_state.new_items_list:
                st.error("❌ Hindi pwedeng mag-save ng walang lamang mga aytem ang POW.")
                return

            # 1. EXCEL SYNC ENGINE (Gagana kung local, ligtas laktawan kung cloud)
            if os.path.exists(excel_path):
                try:
                    wb = load_workbook(excel_path)
                    ws = wb.active
                    
                    for row in st.session_state.new_items_list:
                        q, u, d, p, orig_d = row[0], row[1], row[2], row[3], row[4]
                        
                        # Maghanap kung may kaparehong aytem sa Excel para maiwasan ang duplicate entries sa Master List
                        target_row = None
                        for ex_row in range(2, ws.max_row + 1):
                            cell_val = ws.cell(row=ex_row, column=1).value
                            if cell_val and str(cell_val).strip().lower() == str(orig_d).strip().lower():
                                target_row = ex_row
                                break
                        
                        if target_row:
                            # Kung nagbago ang presyo o unit habang binubuo, i-overwrite sa Excel
                            ws.cell(row=target_row, column=2, value=u)
                            ws.cell(row=target_row, column=3, value=p)
                        else:
                            # Kung sariwang item, isingit sa pinakailalim ng Excel rows
                            new_row = ws.max_row + 1
                            ws.cell(row=new_row, column=1, value=d)
                            ws.cell(row=new_row, column=2, value=u)
                            ws.cell(row=new_row, column=3, value=p)
                            
                    wb.save(excel_path)
                    wb.close()
                except Exception as e:
                    st.error(f"❌ Excel Sync Error: Nabigong isulat ang data sa {excel_path}. Detalye: {e}")
                    return
            else:
                st.warning("⚠️ Paalala: Walang nahanap na lokal na Excel drive (`G:\\`). Nilaktawan ang Excel sync process.")

            # 2. SUBPROCESS AUTOMATION AUTOMATIC RUN
            if os.path.exists(r"G:\jrm"):
                try:
                    subprocess.run(["py", "import_master.py"], cwd=r"G:\jrm", check=True, capture_output=True, text=True)
                except Exception as err:
                    st.error(f"⚠️ Na-save sa Excel pero may babala sa 'import_master.py'. Detalye: {err}")
                    return

            # 3. SQL DATABASE INSERTION PIPELINE
            try:
                # Gagawa muna ng panibagong Project Main Entry sa database at kukunin ang bagong POW ID
                new_pow_id = db.insert_new_project_main(project_name.strip(), location.strip())
                
                if new_pow_id:
                    # I-extract ang tuple parameters: (qty, unit, description, price)
                    final_items_to_insert = [(r[0], r[1], r[2], r[3]) for r in st.session_state.new_items_list]
                    success_items = db.insert_project_items_batch(new_pow_id, final_items_to_insert)
                    
                    if success_items:
                        st.success(f"🎉 Tagumpay! Ang proyektong idinagdag ay rehistrado na sa SQL Database (POW ID: {new_pow_id}).")
                        # Linisin ang session upang handa sa susunod na transaksyon
                        st.session_state.new_items_list = []
                        st.rerun()
                    else:
                        st.error("❌ SQL Error: Hindi maipasok ang listahan ng mga aytem sa database.")
                else:
                    st.error("❌ SQL Error: Nabigong likhain ang pangunahing record ng proyekto.")
            except Exception as sql_err:
                st.error(f"❌ Database Transaction Error: {sql_err}")

    with save_col2:
        if st.button("🔄 Reset Form", use_container_width=True):
            st.session_state.new_items_list = []
            st.rerun()
