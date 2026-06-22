import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import db  # Konektado sa corrected db.py layer mo

class POWListModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f7fafc")
        self.parent = parent
        
        # Para sa tracking ng tooltip popup window
        self.tooltip_window = None
        self.current_hovered_item = None
        
        # --- TITLE BANNER ---
        title_frame = tk.Frame(self, bg="white", bd=1, relief="groove")
        title_frame.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(
            title_frame, 
            text="📜 PROGRAM OF WORKS (POW) MASTERLIST HISTORY", 
            font=("Segoe UI", 12, "bold"), 
            fg="#1a365d", 
            bg="white", 
            padx=15, 
            pady=15
        )
        lbl_title.pack(side="left")

        # --- MAIN CONTAINER ---
        main_frame = tk.Frame(self, bg="#f7fafc")
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # --- TREEVIEW TABLE SETUP ---
        columns = ("id", "project_info", "grand_total", "time", "date")
        
        self.tree = ttk.Treeview(main_frame, columns=columns, show="tree headings", height=20)
        
        self.tree.heading("#0", text="Month Group / No.", anchor="w")
        self.tree.heading("id", text="POW ID")
        self.tree.heading("project_info", text="Project Name & Geolocation")
        self.tree.heading("grand_total", text="Grand Total Amount")
        self.tree.heading("time", text="Time (HH:MM:SS)")
        self.tree.heading("date", text="Date (MM/DD/YYYY)")

        self.tree.column("#0", width=150, minwidth=120, anchor="w")
        self.tree.column("id", width=80, minwidth=60, anchor="center")
        self.tree.column("project_info", width=400, minwidth=300, anchor="w")
        self.tree.column("grand_total", width=150, minwidth=120, anchor="e")
        self.tree.column("time", width=120, minwidth=100, anchor="center")
        self.tree.column("date", width=120, minwidth=100, anchor="center")

        sb = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(fill="both", expand=True, side="left")
        sb.pack(fill="y", side="right")

       # --- STYLING PATTERNS FOR MAXIMIZED DATA FITTING ---
        style = ttk.Style()
        
        # Inayos ang Table Headings: Ginawang font size 9 para tipid sa espasyo
        style.configure(
            "Treeview.Heading", 
            font=("Segoe UI", 9, "bold"), 
            foreground="#2d3748"
        )
        
        # Inayos ang mismong Data Rows: Ginawang font size 9 at pinaliit ang rowheight mula 28 patungong 24
        style.configure(
            "Treeview", 
            font=("Segoe UI", 9), 
            rowheight=24
        )
        
        # Inayos ang Month Header at regular data background tags para sumunod sa liit ng font
        self.tree.tag_configure(
            "month_header", 
            background="#e2e8f0", 
            font=("Segoe UI", 9, "bold"), 
            foreground="#1a365d"
        )
        self.tree.tag_configure(
            "data_row", 
            background="white"
        )
        # ==============================================================================
        # MGA BAGONG EVENT BINDINGS PARA SA HOVER AT TOOLTIP
        # ==============================================================================
        self.tree.bind("<Motion>", self.on_mouse_move)
        self.tree.bind("<Leave>", self.hide_tooltip)

        # Kusang hihilahin ang data sa pagkabukas
        self.load_pow_history()

    def load_pow_history(self):
        """Hihilahin ang mga records mula sa db at iaayos kada buwan sa Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            records = db.get_all_pow_history()
            if not records: return

            current_month_bracket = ""
            parent_node = None
            list_counter = 1

            for row in records:
                pow_id = row[0]
                proj_name = row[1]
                location = row[2]
                grand_total = float(row[3])
                created_at = row[4]

                if isinstance(created_at, str):
                    dt_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                else:
                    dt_obj = created_at

                month_name = dt_obj.strftime("%B %Y").upper()
                time_str = dt_obj.strftime("%H:%M:%S")
                date_str = dt_obj.strftime("%m/%d/%Y")
                
                project_combined_info = f"{proj_name}, {location}"

                if month_name != current_month_bracket:
                    current_month_bracket = month_name
                    parent_node = self.tree.insert(
                        "", "end", text=current_month_bracket, open=True, tags=("month_header",)
                    )
                
                self.tree.insert(
                    parent_node, 
                    "end", 
                    text=f"   {list_counter}.", 
                    values=(pow_id, project_combined_info, f"₱ {grand_total:,.2f}", time_str, date_str),
                    tags=("data_row",)
                )
                list_counter += 1

        except Exception as e:
            messagebox.showerror("Error Loading POW History", f"An error occurred: {e}")

    # ==============================================================================
    # DYNAMIC TOOLTIP LOGIC ENGINE
    # ==============================================================================
    def on_mouse_move(self, event):
        """Tinitingnan kung saan nakatapat ang mouse at nagpapakita ng tooltip kung mahaba ang text."""
        # Alamin kung anong row at column ang tinatamaan ng mouse cursor coordinates
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        
        # Kung lumipat ng row o column ang mouse, burahin muna ang lumang tooltip
        if item_id != self.current_hovered_item:
            self.hide_tooltip()
            self.current_hovered_item = item_id

        if item_id:
            # Kunin ang values ng kasalukuyang row
            row_values = self.tree.item(item_id, 'values')
            
            # Siguraduhing data row ito (may laman ang values) at nakatapat sa Project Info column (`#2`)
            if row_values and column_id == "#2":
                full_text = row_values[1]  # Ito 'yung "Project Name, Location"
                
                # Lalabas lang ang tooltip kung ang pamagat ay mahaba (halimbawa, higit sa 35 characters)
                if len(full_text) > 35:
                    # Kunin ang eksaktong posisyon ng mouse pointer sa screen para doon ilitaw ang box
                    x = event.x_root + 15
                    y = event.y_root + 15
                    self.show_tooltip(full_text, x, y)
                else:
                    self.hide_tooltip()
            else:
                self.hide_tooltip()
        else:
            self.hide_tooltip()

    def show_tooltip(self, text, x, y):
        """Lilikha ng isang borderless, lumulutang na window sa tabi ng mouse pointer."""
        if self.tooltip_window:
            return  # Bukas na ang tooltip, huwag nang gumawa ng bago

        # Gumawa ng Toplevel frame na walang Windows title bar (override-redirect)
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.configure(bg="#2d3748")  # Charcoal Dark background para sa eleganteng UI Look

        # Ang label sa loob ng tooltip box
        lbl = tk.Label(
            self.tooltip_window, 
            text=text, 
            justify="left", 
            bg="#2d3748", 
            fg="white", 
            font=("Segoe UI", 9),
            padx=8, 
            pady=5,
            bd=1, 
            relief="solid"
        )
        lbl.pack()

    def hide_tooltip(self, event=None):
        """Ididestroy ang tooltip window kapag umalis na ang mouse sa hilera."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None