import openpyxl
import mysql.connector
import db  # Ginagamit ang connection details mula sa iyong db.py

def refresh_master_items(file_name="master_items.xlsx", use_streamlit=False):
    """
    Nag-a-update ng master items table mula sa Excel.
    Gumagana sa local terminal at ligtas ding tawagin sa Streamlit Web UI.
    """
    
    # Dynamic logger para sa Console o Web UI Screen
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

    # 🛑 HAKBANG 1: BASAHIN MUNA ANG EXCEL (Safety Check)
    # Proteksyon para kung walang file, hindi muna mabubura ang nasa database!
    log_msg(f"Hakbang 1: Binabasa at sinusuri ang file na '{file_name}'...")
    try:
        wb = openpyxl.load_workbook(file_name, data_only=True) # data_only=True para formula values ang makuha kung may computation
        ws = wb.active
    except FileNotFoundError:
        log_msg(f"Error: Hindi nahanap ang file na '{file_name}'. Siguraduhing upload ito sa tamang folder, boss.", "error")
        return
    except Exception as e:
        log_msg(f"Error sa pagbasa ng Excel file: {e}", "error")
        return

    # 🔌 HAKBANG 2: KUMONEKTA SA DATABASE
    log_msg("Hakbang 2: Kumokonekta sa database pipeline...")
    try:
        conn = db.get_connection() 
        cursor = conn.cursor()
    except Exception as e:
        log_msg(f"Error sa koneksyon ng database: {e}", "error")
        return

    # 🗑️ HAKBANG 3: NILILINIS ANG LUMANG DATA (Dahil sigurado nang may pamalit)
    log_msg("Hakbang 3: Ligtas na nililinis ang lumang laman ng master_items table...")
    try:
        cursor.execute("TRUNCATE TABLE master_items;")
        conn.commit()
    except Exception as e:
        log_msg(f"Hindi ma-clear ang talahanayan: {e}", "error")
        cursor.close()
        conn.close()
        return

    # 📥 HAKBANG 4: MIGRATION AT PAG-INSERT NG BAGONG AYTEM
    log_msg("Hakbang 4: Isinusubo na ang mga bagong materyales sa database...")
    
    insert_query = """
        INSERT INTO master_items (description, unit, unit_price) 
        VALUES (%s, %s, %s)
    """
    
    success_count = 0
    skipped_count = 0
    
    # Magsisimula sa Row 2 para lampasan ang table headers ng Excel
    for r_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        name = row[0]   # Column A: Item Description
        unit = row[1]   # Column B: Unit (e.g., pcs, bags, cu.m)
        price = row[2]  # Column C: Presyo
        
        # Laktawan ang mga blangkong hilera sa Excel
        if not name or str(name).strip() == "":
            continue
            
        # 🧼 PRICE CLEANER: Tanggalin ang mga sagabal na simbolo tulad ng ₱, commas, o spaces
        actual_price = 0.00
        if price is not None:
            try:
                clean_price = str(price).replace("₱", "").replace("P", "").replace(",", "").strip()
                actual_price = float(clean_price)
            except ValueError:
                log_msg(f"Row {r_idx}: Invalid price format para sa '{name}' ({price}). Ginawang 0.00 muna.", "warning")
                actual_price = 0.00

        actual_unit = str(unit).strip() if unit is not None else "pcs"
        
        try:
            cursor.execute(insert_query, (str(name).strip(), actual_unit, actual_price))
            success_count += 1
        except Exception as e:
            skipped_count += 1
            log_msg(f"Laktaw sa Row {r_idx} [{name}]: {e}", "warning")

    # Pinal na pag-save sa MySQL Engine
    conn.commit()
    cursor.close()
    conn.close()
    
    # Pinal na ulat
    log_msg(f"MIGRATION DONE! {success_count} items inserted successfully. {skipped_count} items skipped/warned.", "success")

if __name__ == "__main__":
    # Isulat dito ang saktong filename ng excel mo na kasama sa GitHub folder
    refresh_master_items("mga_materyales.xlsx", use_streamlit=False)
