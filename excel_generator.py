import streamlit as st
import db  # Gumagana sa iyong database layer
import os  # Para sa paggawa ng folders
from datetime import datetime  # Para sa real-time date
import io  # Gagamitin para sa in-memory browser download capability

def render_preview_pow_module():
    """
    Ito ang Main Entry Point para sa Web Preview at Excel Export Module.
    Papalit sa open_excel_preview_modal ng Tkinter.
    """
    st.markdown("### 👁️ POW - Print & Office Excel Layout Preview")
    
    # ==========================================================================
    # DETALYE 1: PROYEKTO SELECTOR (Katapat ng Treeview Selection sa Desktop)
    # ==========================================================================
    # Hihilahin natin ang lahat ng active projects para maging dropdown selection
    try:
        # TANDAAN: Siguraduhing may function ka sa db.py na nagbabalik ng listahan ng projects
        # Kung wala pa, maaari mong i-adapt ang query na ito sa db.py mo
        all_projects = db.get_all_projects() # Nagbabalik ng list ng (id, project_name, location)
    except Exception:
        # Fallback sample data para hindi mag-crash habang dine-debelop
        all_projects = [(1, "SAMPLE OFFICE BUILDING REPAIR", "PALAYAN CITY"), (2, "CONCRETE ROAD MAINTENANCE", "CABANATUAN CITY")]

    if not all_projects:
        st.info("📭 Walang nahanap na proyekto sa database. Mag-encode muna sa 'ADD POW' section, boss.")
        return

    # Gagawa ng magandang format para sa dropdown selection box
    project_options = {f"ID: {proj[0]} | {proj[1]}": proj[0] for proj in all_projects}
    selected_option = st.selectbox("🎯 Pumili ng Proyekto na Nais I-preview at I-export:", list(project_options.keys()))
    
    pow_id = project_options[selected_option]

    # Hihilahin ang records ng napiling POW ID
    proj_info = db.get_project_details(pow_id)
    pow_items = db.get_items_by_project(pow_id)

    if not proj_info:
        st.error("❌ Hindi mahanap ang detalye ng proyektong ito sa database.")
        return

    project_name, location = proj_info[0], proj_info[1]

    # ==========================================================================
    # DETALYE 2: ACTIONS BAR (Mga Pindutan sa Itaas)
    # ==========================================================================
    col_btn1, col_btn2 = st.columns([1, 3])
    
    # Tagatago ng bytes para sa web direct download link
    excel_buffer = io.BytesIO()

    # ==========================================================================
    # DETALYE 3: LOHIKA NG AUTOMATED EXCEL GENERATOR ( openpyxl Engine )
    # ==========================================================================
    def generate_excel_data():
        """Binuo ang openpyxl routine base sa layout ng iyong desktop application"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, Border, Side
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Program of Work"
        ws.views.sheetView[0].showGridLines = True

        # 📑 PRINT & PAGE SETUP FOR LEGAL SIZE (Eksaktong kopya ng deskop specification mo)
        ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
        ws.page_setup.paperSize = ws.PAPERSIZE_LEGAL
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1   
        ws.page_setup.fitToHeight = 0  

        ws.page_margins.left = 0.5
        ws.page_margins.right = 0.5
        ws.page_margins.top = 0.75
        ws.page_margins.bottom = 0.75

        font_title = Font(name="Arial", size=10, bold=True)
        font_regular = Font(name="Arial", size=10)
        font_bold_body = Font(name="Arial", size=10, bold=True)
        
        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        ws['A1'] = "Republic of the Philippines"
        ws['A2'] = "PROVINCE   OF   NUEVA   ECIJA"
        ws['A3'] = "Palayan City"
        ws['A4'] = "PROVINCIAL GENERAL SERVICES OFFICE"
        ws['A6'] = "PROGRAM OF WORKS"
        
        for r in range(1, 7):
            if ws.cell(row=r, column=1).value:
                ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
                header_cell = ws.cell(row=r, column=1)
                header_cell.alignment = align_center
                header_cell.font = font_title

        ws['A7'] = f"Project: {project_name}"
        ws['A8'] = f"Location: {location}"
        ws['A7'].font = font_bold_body
        ws['A8'].font = font_bold_body

        headers_list = ["ITEM", "QTY", "UNIT", "DESCRIPTION", "UNIT PRICE", "AMOUNT"]
        for col_num, header_text in enumerate(headers_list, start=1):
            c_cell = ws.cell(row=9, column=col_num, value=header_text)
            c_cell.font = font_bold_body
            c_cell.alignment = align_center
            
        row_tracker = 10
        computed_total = 0.0
        
        for idx, item in enumerate(pow_items, start=1):
            qty = float(item[0])
            unit = item[1]
            raw_name = item[2]
            raw_price = item[3]
            
            name = str(raw_name).replace("\n", " ").replace("\r", " ").strip()
            try:
                price = float(raw_price) if raw_price is not None else 0.0
            except ValueError:
                price = 0.0

            amount = qty * price
            computed_total += amount

            ws.cell(row=row_tracker, column=1, value=idx).alignment = align_center
            ws.cell(row=row_tracker, column=2, value=qty).alignment = align_center
            ws.cell(row=row_tracker, column=3, value=unit).alignment = align_center
            ws.cell(row=row_tracker, column=4, value=name).alignment = align_left
            
            p_cell = ws.cell(row=row_tracker, column=5, value=price)
            p_cell.number_format = '#,##0.00'
            p_cell.alignment = align_right
            
            a_cell = ws.cell(row=row_tracker, column=6, value=amount)
            a_cell.number_format = '#,##0.00'
            a_cell.alignment = align_right

            for column_pos in range(1, 7):
                ws.cell(row=row_tracker, column=column_pos).font = font_regular
                
            row_tracker += 1

        row_tracker += 1 
        ws.cell(row=row_tracker, column=5, value="Total  P").font = font_bold_body
        ws.cell(row=row_tracker, column=5).alignment = Alignment(horizontal="right", vertical="center")
        
        f_total_cell = ws.cell(row=row_tracker, column=6, value=computed_total)
        f_total_cell.font = font_bold_body
        f_total_cell.number_format = '"P" #,##0.00'
        f_total_cell.alignment = align_right

        double_bottom_border = Border(bottom=Side(style='double'))
        last_item_amount_cell = ws.cell(row=row_tracker - 2, column=6)
        last_item_amount_cell.border = double_bottom_border

        row_tracker += 2
        ws.cell(row=row_tracker, column=1, value="Prepared by:                                                                                                               Checked by:").font = font_regular
        
        row_tracker += 2
        ws.cell(row=row_tracker, column=1, value="        JONATHAN G. LADIGNON                                                                                               BENJAMIN N. RAMOS JR.").font = font_bold_body
        
        row_tracker += 1
        ws.cell(row=row_tracker, column=1, value="             Admin. Officer III                                                                                                                 Engineer II").font = font_regular

        row_tracker += 2
        ws.cell(row=row_tracker, column=1, value="Noted by:                                                                                                                     Recommending Approval:").font = font_regular

        row_tracker += 2
        ws.cell(row=row_tracker, column=1, value="        MARIO T. MARIANO                                                                                                     ENGR. FLORECIO M. VALINO").font = font_bold_body
        
        row_tracker += 1
        ws.cell(row=row_tracker, column=1, value="             Engineer IV                                                                                                                          PGS-Officer").font = font_regular

        row_tracker += 2
        ws.cell(row=row_tracker, column=4, value="                             Approved:").font = font_regular

        row_tracker += 2
        ws.cell(row=row_tracker, column=4, value="                     HON. AURELIO M. UMALI").font = font_bold_body
        row_tracker += 1
        ws.cell(row=row_tracker, column=4, value="                                   Governor").font = font_regular

        column_widths = {'A': 4.57, 'B': 4.86, 'C': 7.00, 'D': 47.14, 'E': 11.57, 'F': 14.57}
        for col_letter, width_size in column_widths.items():
            ws.column_dimensions[col_letter].width = width_size

        ws.row_dimensions[9].height = 20
        for r_idx in range(10, row_tracker + 15):
            ws.row_dimensions[r_idx].height = 16

        if len(pow_items) > 35:
            from openpyxl.worksheet.pagebreak import Break
            ws.row_breaks.append(Break(id=45))

        # --- LOCAL DRIVE AUTO-SAVE (Kapag tumatakbo sa PC mo, boss) ---
        date_folder_name = datetime.now().strftime("%m-%Y")
        usb_base_path = r"G:\jrm"
        clean_project_name = project_name.replace(' ', '_').replace('/', '-').replace('\\', '-')
        filename = f"POW_{clean_project_name}.xlsx"

        if os.path.exists("G:\\"):
            final_export_dir = os.path.join(usb_base_path, date_folder_name)
            os.makedirs(final_export_dir, exist_ok=True)
            full_save_path = os.path.join(final_export_dir, filename)
            wb.save(full_save_path)
            st.toast(f"💾 Auto-saved sa USB: {full_save_path}", icon="✅")
        else:
            # Kung nasa Streamlit Cloud Server, isasave lang muna sa memory buffer para ma-download sa browser
            wb.save(os.path.join(os.getcwd(), filename))
            
        # I-save sa buffer para makuha ng Download Button ng browser
        wb.save(excel_buffer)
        return excel_buffer.getvalue(), filename

    # Patakbuhin ang excel compilation background assembly
    excel_bytes, download_filename = generate_excel_data()

    with col_btn1:
        # Modernong Web Download Button para pwedeng ma-download kahit sa CP o browser gamit ang openpyxl generation
        st.download_button(
            label="📥 EXPORT TO EXCEL",
            data=excel_bytes,
            file_name=download_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    # ==========================================================================
    # DETALYE 4: TEXT PRINT PREVIEW WINDOW (Consolas Style Emulation)
    # ==========================================================================
    st.markdown("#### 📄 Print Preview Display (Legal Format Layout)")
    
    lines = []
    lines.append(f"{'':<25}Republic of the Philippines")
    lines.append(f"{'':<22}PROVINCE   OF   NUEVA   ECIJA")
    lines.append(f"{'':<26}Palayan City")
    lines.append(f"{'':<15}PROVINCIAL GENERAL SERVICES OFFICE")
    lines.append("")
    lines.append(f"{'':<27}PROGRAM OF WORKS")
    lines.append("")
    lines.append(f"Project:  {project_name}")
    lines.append(f"Location: {location}")
    lines.append("")
    
    lines.append("=" * 95)
    lines.append(f"{'ITEM':<8}{'QTY':<8}{'UNIT':<10}{'DESCRIPTION':<35}{'UNIT PRICE':<16}{'AMOUNT':<15}")
    lines.append("=" * 95)

    grand_total = 0.0
    for idx, item in enumerate(pow_items, start=1):
        qty = float(item[0]) 
        unit = item[1]
        raw_name = item[2]
        raw_price = item[3]
        
        name = str(raw_name).replace("\n", " ").replace("\r", " ").strip()
        try:
            price = float(raw_price) if raw_price is not None else 0.0
        except ValueError:
            price = 0.0

        amount = qty * price
        grand_total += amount
        
        short_name = name[:32] + "..." if len(name) > 32 else name
        lines.append(f"{idx:<8}{qty:<8.2f}{unit:<10}{short_name:<35}{price:>12,.2f}      {amount:>12,.2f}")

    lines.append("-" * 95)
    lines.append(f"{'TOTAL':<61}P     {grand_total:>22,.2f}")
    lines.append("=" * 95)
    lines.append("")

    lines.append(f"Prepared by:{'':<45}Checked by:")
    lines.append("")
    lines.append(f"       JONATHAN G. LADIGNON{'':<37}BENJAMIN N. RAMOS JR")
    lines.append(f"       Admin. Officer III  {'':<37}Engineer II")
    lines.append("")
    lines.append(f"Noted by:{'':<48}Recommending Approval:")
    lines.append("")
    lines.append(f"MARIO T. MARIANO{'':<41}ENGR. FLORECIO M. VALINO")
    lines.append("")
    lines.append(f"{'':<50}Approved:")
    lines.append("")
    lines.append(f"{'':<45}HON. AURELIO M. UMALI")
    lines.append(f"{'':<50}Governor")

    # Pagsasama-sama ng text lines array
    full_preview_text = "\n".join(lines)
    
    # Ginamit ang st.code upang mapanatili ang fixed-width monospaced (Consolas/Courier) font alignment ng layout mo
    st.code(full_preview_text, language="text")
