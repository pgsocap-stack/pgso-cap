import openpyxl
import mysql.connector
import db  # Ginagamit ang connection details mula sa iyong db.py

def refresh_master_items(file_name="master_items.xlsx", use_streamlit=False):
    """
    Nag-a-update ng master items table mula sa Excel.
    use_streamlit=True kung gagamitin sa loob ng web dashboard.
    """
    
    # Pang-log ng mensahe (Console o Web UI)
    def log_msg(text, status="info"):
        if use_streamlit:
            import streamlit as st
            if status == "success": st.success(text)
            elif status == "error": st.error(text)
            elif status == "warning": st.warning(text)
            else: st.info(text)
        else:
            prefix = "🔄" if status == "info" else "✅" if status == "success" else "❌" if status == "error" else "⚠️"
            print(f"{prefix} {text}")

    log_msg("Hakbang 1: Kumokonekta sa database...")
    try:
        conn = db.get_connection() # Gumagamit ng standard configuration mo sa db.py
        cursor = conn.cursor()
    except Exception as e:
        log_msg(f"Error sa koneksyon ng database: {e}", "error")
        return

    log_msg("Hakbang 2: Nililinis ang lumang laman ng master_items...")
    try:
        # Siguraduhing tugma ang table name sa database mo
        cursor.execute("TRUNCATE TABLE master_items;")
        conn.commit()
    except Exception as e:
        log_msg(f"Hindi ma-clear ang table: {e}", "error")
        cursor.close()
        conn.close()
        return

    log_msg(f"Hakbang 3: Binabasa ang file na '{file_name}'...")
    try:
        wb = openpyxl.load_workbook(file_name)
        ws = wb.active
    except FileNotFoundError:
        log_msg(f"Error: Hindi nahanap ang file na '{file_name}'.", "error")
        cursor.close()
        conn.close()
        return

    log_msg("Hakbang 4: Isinusubo na ang mga bagong materyales sa database...")
    
    # 🔥 ITINUGMA ANG MGA COLUMNS: description, unit, unit_price para tugma sa dashboard suggestions natin!
    insert_query = """
        INSERT INTO master_items (description, unit, unit_price) 
        VALUES (%s, %s, %s)
    """
    
    success_count = 0
    # Babasahin mula Row 2 para lagpasan ang Header ng Excel
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = row[0]   # Column A: Item Name / Description
        unit = row[1]   # Column B: Unit (e.g., pcs, bags, cu.m)
        price = row[2]  # Column C: Presyo
        
        if name:
            actual_price = float(price) if price is not None else 0.00
            actual_unit = str(unit).strip() if unit is not None else "pcs"
            
            try:
                cursor.execute(insert_query, (str(name).strip(), actual_unit, actual_price))
                success_count += 1
            except Exception as e:
                # Huwag i-crash ang buong loop kung may isang depektibong row
                print(f"⚠️ Laktaw: {name} ({e})")

    # I-commit ang mga bagong pasok na data
    conn.commit()
    cursor.close()
    conn.close()
    
    log_msg(f"TAGUMPAY, BOSS! {success_count} na materyales ang pumasok sa database master list!", "success")

if __name__ == "__main__":
    # 👈 Siguraduhing EKSOPTO ang pangalan ng excel file mo rito (kung master_items.xlsx o mga_materyales.xlsx)
    refresh_master_items("master_items.xlsx", use_streamlit=False)
