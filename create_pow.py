import streamlit as st
import db

# 1. Hilahin ang buong masterlist mula sa Database
master_items_data = db.get_all_master_items()

# 2. I-convert ang data sa isang Dictionary para sa mabilisang auto-fill
# Format: {"Pangalan ng Materyales": {"unit": "pcs", "price": 150.00}}
master_pool = {row[0]: {"unit": row[1], "price": float(row[2])} for row in master_items_data}

st.markdown("### ➕ Magdagdag ng Bagong Aytem sa POW")

# Gagawa ng container para sa iyong Form sa ibaba
with st.container(border=True):
    
    # 🔍 PRE-PREPARE NG MGA OPTIONS PARA SA DROPDOWN
    dropdown_options = list(master_pool.keys())
    # Maglagay ng default option para kung wala sa listahan ang materyales, pwede i-type manu-mano
    dropdown_options.insert(0, "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...")

    # DITO NA MAGSISIMULA ANG INPUTS
    selected_item = st.selectbox(
        "🔍 Mag-search o Pumili ng Materyales (Item Description):",
        options=dropdown_options
    )
    
    # Kusa nating hihilahin ang default Unit at Price base sa napili sa Dropdown
    default_unit = ""
    default_price = 0.00
    
    if selected_item != "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...":
        chosen_desc = selected_item
        default_unit = master_pool[selected_item]["unit"]
        default_price = master_pool[selected_item]["price"]
    else:
        chosen_desc = ""

    # Gagawa ng 3 columns para sa QTY, UNIT, at PRICE para magkakatabi sila sa screen
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        input_qty = st.number_input("QTY (Dami):", min_value=0.0, step=1.0, value=0.0)
        
    with col2:
        # Kung may napili sa dropdown, lalabas dito automatic ang unit (e.g. bags, pcs)
        input_unit = st.text_input("UNIT:", value=default_unit)
        
    with col3:
        # Kung may napili sa dropdown, lalabas dito automatic ang presyo mula sa Excel mo
        input_price = st.number_input("UNIT PRICE (Presyo):", min_value=0.0, step=0.01, value=default_price)

    # Kung "Custom Entry" ang pinili, magpapakita ng extra text box para maitype ang bagong pangalan
    if selected_item == "✨ Manu-manong Isusulat (Custom Entry) / Pumili sa ibaba...":
        final_description = st.text_input("Isulat ang Pangalan ng Custom Material:")
    else:
        final_description = chosen_desc

    # --- BUTTON PARA SA PAGSOUND-IN O PAGSABIT SA LALAGYAN ---
    if st.button("➕ Isama sa Listahan", use_container_width=True, type="primary"):
        if not final_description.strip():
            st.error("⚠️ Error: Hindi pwedeng blangko ang Item Description, boss!")
        elif input_qty <= 0:
            st.warning("⚠️ Paalala: Siguraduhing may laman o higit sa 0 ang QTY.")
        else:
            # Dito mo na isasabit sa iyong st.session_state ang bagong row ng aytem!
            # Halimbawa:
            if 'init_data' not in st.session_state:
                st.session_state.init_data = []
                
            st.session_state.init_data.append({
                "ITEM": len(st.session_state.init_data) + 1,
                "QTY": input_qty,
                "UNIT": input_unit,
                "DESCRIPTION": final_description.strip(),
                "UNIT PRICE": input_price,
                "AMOUNT": input_qty * input_price
            })
            st.toast(f"🎉 Naidagdag na si: {final_description}", icon="✅")
            st.rerun()
