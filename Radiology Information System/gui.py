import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import (
    create_database_db,
    migrate_add_phone_column_db,
    login_db,
    create_user_db,
    get_all_users_db,
    delete_user_db,
    add_patient_db,
    view_patients_db,
    search_patient_db,
    update_patient_information_db,
    delete_patient_db,
    add_scan_db,
    view_scans_db,
    add_report_db,
    view_reports_db,
    view_pending_reports_db,
    view_completed_reports_db,
    update_report_status_db,
    dashboard_db,
)

# ============================================================
# DESIGN TOKENS
# ============================================================
COLORS = {
    "navy":        "#1A2B4A",
    "navy_light":  "#243660",
    "teal":        "#0E8A8A",
    "teal_light":  "#12ABAD",
    "white":       "#FFFFFF",
    "off_white":   "#F4F7FB",
    "slate":       "#E2E8F0",
    "text_dark":   "#1E293B",
    "text_mid":    "#475569",
    "text_light":  "#94A3B8",
    "success":     "#16A34A",
    "error":       "#DC2626",
    "warning":     "#D97706",
    "row_even":    "#F8FAFC",
    "row_odd":     "#FFFFFF",
}

FONTS = {
    "heading":    ("Segoe UI", 20, "bold"),
    "subheading": ("Segoe UI", 13, "bold"),
    "label":      ("Segoe UI", 10),
    "label_bold": ("Segoe UI", 10, "bold"),
    "entry":      ("Segoe UI", 11),
    "button":     ("Segoe UI", 10, "bold"),
    "status":     ("Segoe UI", 10),
    "nav":        ("Segoe UI", 11),
    "stat_value": ("Segoe UI", 32, "bold"),
    "stat_label": ("Segoe UI", 10),
    "small":      ("Segoe UI", 9),
}

BODY_REGIONS = [
    "Head", "Brain", "Neck", "Chest", "Abdomen", "Pelvis",
    "Spine - Cervical", "Spine - Thoracic", "Spine - Lumbar",
    "Shoulder", "Elbow", "Wrist", "Hand",
    "Hip", "Knee", "Ankle", "Foot",
    "Whole Body",
]

# ============================================================
# ROLE PERMISSIONS
# Which nav keys each role is allowed to see.
# Admin sees everything.  Change this table to adjust access.
# ============================================================
ROLE_PERMISSIONS = {
    "Admin": [
        "dashboard", "add_patient", "view", "search",
        "scan", "view_scans", "report", "view_reports", "manage_users",
    ],
    "Radiologist": [
        "dashboard", "view", "search",
        "view_scans", "report", "view_reports",
    ],
    "Technician": [
        "dashboard", "view", "search",
        "scan", "view_scans",
    ],
    "Receptionist": [
        "dashboard", "add_patient", "view", "search",
        "view_reports",
    ],
}

# ============================================================
# ROLE BADGE COLOURS — shown in the sidebar footer
# ============================================================
ROLE_COLORS = {
    "Admin":        "#7C3AED",   # purple
    "Radiologist":  COLORS["teal"],
    "Technician":   "#EA580C",   # orange
    "Receptionist": "#1D4ED8",   # blue
}

create_database_db()
migrate_add_phone_column_db()


# ============================================================
# SMALL REUSABLE WIDGET HELPERS
# ============================================================
def styled_entry(parent, **kw):
    return tk.Entry(parent, font=FONTS["entry"], relief="flat",
                    bg=COLORS["off_white"], fg=COLORS["text_dark"],
                    insertbackground=COLORS["teal"], bd=0, **kw)

def underline(parent):
    return tk.Frame(parent, bg=COLORS["slate"], height=2)

def bind_focus_line(widget, line):
    widget.bind("<FocusIn>",  lambda e: line.config(bg=COLORS["teal"]))
    widget.bind("<FocusOut>", lambda e: line.config(bg=COLORS["slate"]))

def make_tree(parent, columns, col_cfg, height=None):
    kw = dict(columns=columns, show="headings",
              style="Custom.Treeview", selectmode="browse")
    if height:
        kw["height"] = height
    tree = ttk.Treeview(parent, **kw)
    for col in columns:
        w, anc = col_cfg[col]
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor=anc, minwidth=40)
    tree.tag_configure("even", background=COLORS["row_even"])
    tree.tag_configure("odd",  background=COLORS["row_odd"])
    return tree

def populate_tree(tree, data):
    tree.delete(*tree.get_children())
    for i, row in enumerate(data):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=row, tags=(tag,))


# ============================================================
# LOGIN WINDOW
# ============================================================
def show_login(on_success):
    """
    Builds and shows the login window.
    on_success(user_dict) is called when credentials are correct.
    The login window destroys itself before calling on_success.
    """
    win = tk.Tk()
    win.title("RIS — Login")
    win.geometry("420x520")
    win.resizable(False, False)
    win.configure(bg=COLORS["navy"])

    # ---- header panel ----
    header = tk.Frame(win, bg=COLORS["navy"])
    header.pack(fill="x", pady=(40, 20))

    tk.Label(header, text="☢", font=("Segoe UI", 40),
             fg=COLORS["teal"], bg=COLORS["navy"]).pack()
    tk.Label(header, text="Radiology Information System",
             font=("Segoe UI", 13, "bold"),
             fg=COLORS["white"], bg=COLORS["navy"]).pack()
    tk.Label(header, text="Sign in to continue",
             font=FONTS["small"],
             fg=COLORS["text_light"], bg=COLORS["navy"]).pack(pady=(4, 0))

    # ---- form card ----
    card_outer = tk.Frame(win, bg=COLORS["slate"])
    card_outer.pack(fill="x", padx=32)
    card = tk.Frame(card_outer, bg=COLORS["white"])
    card.pack(fill="x", padx=1, pady=1)

    form = tk.Frame(card, bg=COLORS["white"])
    form.pack(fill="x", padx=28, pady=28)

    # username
    tk.Label(form, text="Username", font=FONTS["label_bold"],
             fg=COLORS["text_mid"], bg=COLORS["white"],
             anchor="w").pack(fill="x", pady=(0, 4))
    username_entry = styled_entry(form)
    username_entry.pack(fill="x", ipady=8)
    u_line = underline(form); u_line.pack(fill="x")
    bind_focus_line(username_entry, u_line)

    # password
    tk.Label(form, text="Password", font=FONTS["label_bold"],
             fg=COLORS["text_mid"], bg=COLORS["white"],
             anchor="w").pack(fill="x", pady=(18, 4))
    password_entry = styled_entry(form, show="•")
    password_entry.pack(fill="x", ipady=8)
    p_line = underline(form); p_line.pack(fill="x")
    bind_focus_line(password_entry, p_line)

    # error label — hidden until needed
    error_lbl = tk.Label(form, text="", font=FONTS["small"],
                         fg=COLORS["error"], bg=COLORS["white"])
    error_lbl.pack(pady=(10, 0))

    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:
            error_lbl.config(text="Please enter both username and password")
            return

        user = login_db(username, password)

        if not user:
            error_lbl.config(text="Incorrect username or password")
            password_entry.delete(0, tk.END)
            password_entry.focus_set()
            return

        # success — close login window and hand off to main app
        win.destroy()
        on_success(user)

    # login button
    login_btn = tk.Label(form, text="Sign In", font=FONTS["button"],
                         bg=COLORS["teal"], fg=COLORS["white"],
                         cursor="hand2", pady=11, anchor="center")
    login_btn.pack(fill="x", pady=(20, 0))
    login_btn.bind("<Button-1>", lambda e: attempt_login())
    login_btn.bind("<Enter>",    lambda e: login_btn.config(bg=COLORS["teal_light"]))
    login_btn.bind("<Leave>",    lambda e: login_btn.config(bg=COLORS["teal"]))

    username_entry.bind("<Return>", lambda e: password_entry.focus_set())
    password_entry.bind("<Return>", lambda e: attempt_login())

    # version footer
    tk.Label(win, text="v1.1  •  RIS",
             font=FONTS["small"],
             fg=COLORS["text_light"],
             bg=COLORS["navy"]).pack(side="bottom", pady=16)

    username_entry.focus_set()
    win.mainloop()


# ============================================================
# MAIN APPLICATION
# ============================================================
def start_main_app(current_user):
    """
    Builds the main RIS window for the logged-in user.
    current_user is the dict returned by login_db():
        {"user_id", "username", "role", "full_name"}
    """
    role        = current_user["role"]
    full_name   = current_user["full_name"] or current_user["username"]
    allowed     = ROLE_PERMISSIONS.get(role, [])

    root = tk.Tk()
    root.title(f"RIS — {full_name}  [{role}]")
    root.geometry("1100x680")
    root.minsize(900, 580)
    root.configure(bg=COLORS["navy"])

    # ---------- ttk styles ----------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Custom.Treeview",
                    background=COLORS["white"],
                    foreground=COLORS["text_dark"],
                    rowheight=32,
                    fieldbackground=COLORS["white"],
                    borderwidth=0,
                    font=FONTS["label"])
    style.configure("Custom.Treeview.Heading",
                    background=COLORS["navy"],
                    foreground=COLORS["white"],
                    font=FONTS["label_bold"],
                    relief="flat", padding=8)
    style.map("Custom.Treeview",
              background=[("selected", COLORS["teal"])],
              foreground=[("selected", COLORS["white"])])
    style.map("Custom.Treeview.Heading",
              background=[("active", COLORS["navy_light"])])
    style.configure("Thin.Vertical.TScrollbar",
                    troughcolor=COLORS["off_white"],
                    background=COLORS["teal"],
                    borderwidth=0, arrowsize=12)
    style.configure("TCombobox", padding=4)

    # =====================================================
    # LAYOUT
    # =====================================================
    sidebar = tk.Frame(root, bg=COLORS["navy"], width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    content_area = tk.Frame(root, bg=COLORS["off_white"])
    content_area.pack(side="right", fill="both", expand=True)

    # ---- sidebar logo ----
    logo_frame = tk.Frame(sidebar, bg=COLORS["navy"], height=90)
    logo_frame.pack(fill="x")
    logo_frame.pack_propagate(False)

    tk.Label(logo_frame, text="☢", font=("Segoe UI", 28),
             fg=COLORS["teal"], bg=COLORS["navy"]).pack(pady=(18, 0))
    tk.Label(logo_frame, text="RIS", font=("Segoe UI", 11, "bold"),
             fg=COLORS["white"], bg=COLORS["navy"]).pack()

    tk.Frame(sidebar, bg=COLORS["navy_light"], height=1).pack(fill="x", pady=8)

    # ---- toast bar ----
    toast_bar = tk.Frame(content_area, bg=COLORS["off_white"], height=36)
    toast_bar.pack(side="bottom", fill="x")
    toast_bar.pack_propagate(False)

    toast_label = tk.Label(toast_bar, text="", font=FONTS["status"],
                           bg=COLORS["off_white"], fg=COLORS["text_mid"],
                           anchor="w", padx=16)
    toast_label.pack(fill="both", expand=True)

    _toast_job = [None]

    def show_message(msg, color="success", duration=3000):
        if _toast_job[0]:
            root.after_cancel(_toast_job[0])
        bg_map = {
            "success": ("#DCFCE7", COLORS["success"]),
            "error":   ("#FEE2E2", COLORS["error"]),
            "info":    ("#DBEAFE", "#1D4ED8"),
        }
        bg, fg = bg_map.get(color, ("#DBEAFE", "#1D4ED8"))
        icons  = {"success": "✔  ", "error": "✖  ", "info": "ℹ  "}
        toast_bar.config(bg=bg)
        toast_label.config(text=icons.get(color, "") + msg,
                           bg=bg, fg=fg, font=FONTS["label_bold"])
        def clear():
            toast_bar.config(bg=COLORS["off_white"])
            toast_label.config(text="", bg=COLORS["off_white"],
                               fg=COLORS["text_mid"], font=FONTS["status"])
        _toast_job[0] = root.after(duration, clear)

    # ---- content host ----
    content_host = tk.Frame(content_area, bg=COLORS["off_white"])
    content_host.pack(fill="both", expand=True)

    def clear_content():
        for w in content_host.winfo_children():
            w.destroy()

    # =====================================================
    # NAV BUTTON FACTORY
    # =====================================================
    nav_buttons  = {}
    _active_nav  = [None]

    def make_nav_btn(text, icon, command, key):
        btn_frame = tk.Frame(sidebar, bg=COLORS["navy"], cursor="hand2")
        btn_frame.pack(fill="x", pady=1)

        indicator = tk.Frame(btn_frame, bg=COLORS["navy"], width=4)
        indicator.pack(side="left", fill="y")

        inner = tk.Frame(btn_frame, bg=COLORS["navy"], cursor="hand2")
        inner.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 13),
                            fg=COLORS["text_light"], bg=COLORS["navy"],
                            width=3, anchor="center")
        icon_lbl.pack(side="left", pady=10, padx=(10, 4))

        text_lbl = tk.Label(inner, text=text, font=FONTS["nav"],
                            fg=COLORS["text_light"], bg=COLORS["navy"],
                            anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        def activate():
            for k, parts in nav_buttons.items():
                parts["indicator"].config(bg=COLORS["navy"])
                parts["icon"].config(fg=COLORS["text_light"], bg=COLORS["navy"])
                parts["text"].config(fg=COLORS["text_light"], bg=COLORS["navy"])
                parts["frame"].config(bg=COLORS["navy"])
                parts["inner"].config(bg=COLORS["navy"])
            indicator.config(bg=COLORS["teal"])
            icon_lbl.config(fg=COLORS["white"], bg=COLORS["navy_light"])
            text_lbl.config(fg=COLORS["white"], bg=COLORS["navy_light"])
            btn_frame.config(bg=COLORS["navy_light"])
            inner.config(bg=COLORS["navy_light"])
            _active_nav[0] = key
            command()

        for w in (btn_frame, inner, icon_lbl, text_lbl):
            w.bind("<Button-1>", lambda e, a=activate: a())

        def on_enter(e):
            if _active_nav[0] != key:
                for w in (btn_frame, inner, icon_lbl, text_lbl):
                    w.config(bg=COLORS["navy_light"])
        def on_leave(e):
            if _active_nav[0] != key:
                for w in (btn_frame, inner, icon_lbl, text_lbl):
                    w.config(bg=COLORS["navy"])

        for w in (btn_frame, inner, icon_lbl, text_lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        nav_buttons[key] = {
            "frame": btn_frame, "inner": inner, "indicator": indicator,
            "icon":  icon_lbl,  "text":  text_lbl, "activate": activate,
        }

    # =====================================================
    # PAGE HEADER
    # =====================================================
    def page_header(title, subtitle=""):
        hdr = tk.Frame(content_host, bg=COLORS["white"], height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Frame(hdr, bg=COLORS["teal"], width=4).pack(side="left", fill="y")
        txt = tk.Frame(hdr, bg=COLORS["white"])
        txt.pack(side="left", fill="both", expand=True, padx=20)
        tk.Label(txt, text=title, font=FONTS["heading"],
                 fg=COLORS["text_dark"], bg=COLORS["white"],
                 anchor="w").pack(anchor="w", pady=(12, 0))
        if subtitle:
            tk.Label(txt, text=subtitle, font=FONTS["small"],
                     fg=COLORS["text_mid"], bg=COLORS["white"],
                     anchor="w").pack(anchor="w")

        tk.Frame(content_host, bg=COLORS["slate"], height=1).pack(fill="x")

    # =====================================================
    # 1. DASHBOARD
    # =====================================================
    def show_dashboard():
        clear_content()
        page_header("Dashboard", f"Welcome back, {full_name}")

        body = tk.Frame(content_host, bg=COLORS["off_white"])
        body.pack(fill="both", expand=True, padx=24, pady=20)

        try:
            data = dashboard_db()
            show_message("Dashboard loaded", "success")
        except Exception as e:
            data = {"patients": "—", "scans": "—", "reports": "—", "pending": "—"}
            show_message(f"Could not load data: {e}", "error")

        cards_row = tk.Frame(body, bg=COLORS["off_white"])
        cards_row.pack(fill="x", pady=(0, 20))

        stats = [
            ("Total Patients",  str(data["patients"]), "👤", COLORS["teal"]),
            ("Total Scans",     str(data["scans"]),    "🩻", "#7C3AED"),
            ("Total Reports",   str(data["reports"]),  "📄", "#EA580C"),
            ("Pending Reports", str(data["pending"]),  "⏳", COLORS["warning"]),
        ]

        for label, value, icon, accent in stats:
            card = tk.Frame(cards_row, bg=COLORS["white"], relief="flat", bd=0)
            card.pack(side="left", fill="both", expand=True, padx=8, pady=4)
            tk.Frame(card, bg=accent, height=5).pack(fill="x")
            bi = tk.Frame(card, bg=COLORS["white"])
            bi.pack(fill="both", expand=True, padx=20, pady=16)
            tk.Label(bi, text=icon, font=("Segoe UI", 26),
                     bg=COLORS["white"], fg=accent).pack(anchor="w")
            tk.Label(bi, text=value, font=FONTS["stat_value"],
                     bg=COLORS["white"], fg=COLORS["text_dark"]).pack(anchor="w")
            tk.Label(bi, text=label, font=FONTS["stat_label"],
                     bg=COLORS["white"], fg=COLORS["text_mid"]).pack(anchor="w")

        # role badge
        badge_frame = tk.Frame(body, bg=COLORS["off_white"])
        badge_frame.pack(anchor="w", pady=(0, 12))

        role_color = ROLE_COLORS.get(role, COLORS["teal"])
        tk.Label(badge_frame, text=f"  {role}  ",
                 font=FONTS["label_bold"],
                 bg=role_color, fg=COLORS["white"],
                 padx=6, pady=4).pack(side="left")
        tk.Label(badge_frame,
                 text=f"  You have access to {len(allowed)} section(s)",
                 font=FONTS["small"],
                 bg=COLORS["off_white"],
                 fg=COLORS["text_mid"]).pack(side="left", padx=8)

        # quick actions — only show what this role can access
        tk.Label(body, text="Quick Actions", font=FONTS["subheading"],
                 fg=COLORS["text_dark"],
                 bg=COLORS["off_white"]).pack(anchor="w", pady=(8, 6))

        qa_row = tk.Frame(body, bg=COLORS["off_white"])
        qa_row.pack(fill="x")

        all_quick = [
            ("➕  Register Patient", "add_patient"),
            ("🔍  Search Patient",   "search"),
            ("🩻  Add Scan",         "scan"),
            ("📄  Add Report",       "report"),
        ]

        for text, key in all_quick:
            if key not in allowed:
                continue
            btn = tk.Label(qa_row, text=text, font=FONTS["nav"],
                           bg=COLORS["white"], fg=COLORS["teal"],
                           cursor="hand2", padx=16, pady=12,
                           relief="flat", bd=0)
            btn.pack(side="left", padx=(0, 10))
            btn.bind("<Button-1>", lambda e, k=key: nav_buttons[k]["activate"]())
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["off_white"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["white"]))

    # =====================================================
    # 2. ADD PATIENT
    # =====================================================
    def show_add_patient():
        clear_content()
        page_header("Register Patient",
                    "Fill in the details below to create a new patient record")

        body = tk.Frame(content_host, bg=COLORS["off_white"])
        body.pack(fill="both", expand=True, padx=32, pady=20)

        card_outer = tk.Frame(body, bg=COLORS["slate"])
        card_outer.pack(fill="x", pady=4)
        card = tk.Frame(card_outer, bg=COLORS["white"])
        card.pack(fill="x", padx=1, pady=1)

        form_inner = tk.Frame(card, bg=COLORS["white"])
        form_inner.pack(fill="x", padx=30, pady=24)
        form_inner.columnconfigure(0, weight=1)
        form_inner.columnconfigure(1, weight=1)

        left = tk.Frame(form_inner, bg=COLORS["white"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        tk.Label(left, text="Patient Name *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        name_entry = styled_entry(left)
        name_entry.pack(fill="x", ipady=7)
        nl = underline(left); nl.pack(fill="x"); bind_focus_line(name_entry, nl)

        tk.Label(left, text="Age *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(18, 4))
        age_entry = styled_entry(left)
        age_entry.pack(fill="x", ipady=7)
        al = underline(left); al.pack(fill="x"); bind_focus_line(age_entry, al)

        tk.Label(left, text="Phone Number *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(18, 4))
        phone_entry = styled_entry(left)
        phone_entry.pack(fill="x", ipady=7)
        pl = underline(left); pl.pack(fill="x"); bind_focus_line(phone_entry, pl)
        tk.Label(left, text="For contacting patient when report is ready",
                 font=FONTS["small"], fg=COLORS["text_light"],
                 bg=COLORS["white"], anchor="w").pack(fill="x")

        right = tk.Frame(form_inner, bg=COLORS["white"])
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        tk.Label(right, text="Sex *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        sex_var = tk.StringVar()
        sex_combo = ttk.Combobox(right, textvariable=sex_var,
                                 values=["Male", "Female", "Other"],
                                 font=FONTS["entry"], state="readonly")
        sex_combo.pack(fill="x", ipady=4)

        tk.Label(right, text="Address / Notes", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(18, 4))
        addr_entry = styled_entry(right)
        addr_entry.pack(fill="x", ipady=7)
        addr_l = underline(right); addr_l.pack(fill="x")
        bind_focus_line(addr_entry, addr_l)

        btn_row = tk.Frame(card, bg=COLORS["white"])
        btn_row.pack(fill="x", padx=30, pady=(20, 24))

        def save_patient():
            name  = name_entry.get().strip()
            age   = age_entry.get().strip()
            sex   = sex_var.get().strip()
            phone = phone_entry.get().strip()

            errors = []
            if not name:
                errors.append("Patient name is required")
            if not age:
                errors.append("Age is required")
            elif not age.isdigit():
                errors.append("Age must be a number")
            elif not (0 < int(age) < 130):
                errors.append("Enter a realistic age (1–129)")
            if not sex:
                errors.append("Sex is required")
            if not phone:
                errors.append("Phone number is required")
            elif not phone.replace("+", "").replace(" ", "").isdigit():
                errors.append("Phone number must contain only digits")

            if errors:
                show_message(errors[0], "error")
                return

            try:
                if not add_patient_db(name, int(age), sex, phone):
                    show_message("A patient with this name, age and sex already exists",
                                 "error")
                    return
                show_message(f"Patient '{name}' registered successfully", "success")
                for e in (name_entry, age_entry, phone_entry, addr_entry):
                    e.delete(0, tk.END)
                sex_combo.set("")
                name_entry.focus_set()
            except Exception as ex:
                show_message(f"Database error: {ex}", "error")

        save_btn = tk.Label(btn_row, text="Save Patient Record",
                            font=FONTS["button"], bg=COLORS["teal"],
                            fg=COLORS["white"], cursor="hand2",
                            padx=24, pady=10)
        save_btn.pack(side="left")
        save_btn.bind("<Button-1>", lambda e: save_patient())
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=COLORS["teal_light"]))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=COLORS["teal"]))

        def clear_form():
            for e in (name_entry, age_entry, phone_entry, addr_entry):
                e.delete(0, tk.END)
            sex_combo.set("")
            name_entry.focus_set()
            show_message("Form cleared", "info")

        clr_btn = tk.Label(btn_row, text="Clear Form", font=FONTS["button"],
                           bg=COLORS["slate"], fg=COLORS["text_mid"],
                           cursor="hand2", padx=24, pady=10)
        clr_btn.pack(side="left", padx=(12, 0))
        clr_btn.bind("<Button-1>", lambda e: clear_form())
        clr_btn.bind("<Enter>", lambda e: clr_btn.config(bg=COLORS["text_light"]))
        clr_btn.bind("<Leave>", lambda e: clr_btn.config(bg=COLORS["slate"]))

        name_entry.bind("<Return>", lambda e: age_entry.focus_set())
        age_entry.bind("<Return>",  lambda e: phone_entry.focus_set())
        phone_entry.bind("<Return>",lambda e: sex_combo.focus_set())
        sex_combo.bind("<Return>",  lambda e: save_patient())
        name_entry.focus_set()

    # =====================================================
    # 3. VIEW PATIENTS
    # =====================================================
    def show_view_patients():
        clear_content()
        page_header("Patient Records",
                    "Browse, edit, or remove registered patients")

        toolbar = tk.Frame(content_host, bg=COLORS["off_white"])
        toolbar.pack(fill="x", padx=24, pady=(12, 4))

        tk.Label(toolbar, text="🔍", font=("Segoe UI", 12),
                 bg=COLORS["off_white"],
                 fg=COLORS["text_mid"]).pack(side="left")
        filter_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=filter_var, font=FONTS["entry"],
                 relief="flat", bg=COLORS["white"], fg=COLORS["text_dark"],
                 insertbackground=COLORS["teal"],
                 bd=0, width=28).pack(side="left", ipady=6, padx=(6, 0))
        tk.Frame(toolbar, bg=COLORS["teal"], height=2,
                 width=230).pack(side="left", anchor="s")

        count_label = tk.Label(toolbar, text="", font=FONTS["small"],
                               fg=COLORS["text_mid"],
                               bg=COLORS["off_white"])
        count_label.pack(side="right", padx=8)

        # Edit / Delete only for Admin
        if "manage_users" in allowed:
            action_row = tk.Frame(content_host, bg=COLORS["off_white"])
            action_row.pack(fill="x", padx=24, pady=(0, 8))
            selected_id = tk.IntVar(value=0)

            def edit_selected():
                pid = selected_id.get()
                if not pid:
                    show_message("Select a patient row first", "error"); return
                _open_edit_patient(pid, load_data)

            def delete_selected():
                pid = selected_id.get()
                if not pid:
                    show_message("Select a patient row first", "error"); return
                if messagebox.askyesno("Confirm Delete",
                        f"Delete patient ID {pid}?\nThis also deletes their "
                        "scans and reports and cannot be undone."):
                    if delete_patient_db(pid):
                        show_message(f"Patient {pid} deleted", "success")
                        load_data()
                    else:
                        show_message("Patient not found", "error")

            for lbl, cmd, bg in [
                ("✏ Edit Selected",   edit_selected,   COLORS["teal"]),
                ("🗑 Delete Selected", delete_selected, COLORS["error"]),
            ]:
                b = tk.Label(action_row, text=lbl, font=FONTS["button"],
                            bg=bg, fg=COLORS["white"], cursor="hand2",
                            padx=16, pady=8)
                b.pack(side="left", padx=(0, 8))
                b.bind("<Button-1>", lambda e, c=cmd: c())
        else:
            selected_id = tk.IntVar(value=0)

        tree_frame = tk.Frame(content_host, bg=COLORS["white"])
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        columns  = ("ID", "Name", "Age", "Sex", "Phone")
        col_cfg  = {"ID": (60,"center"), "Name": (240,"w"),
                    "Age": (70,"center"), "Sex": (90,"center"),
                    "Phone": (140,"center")}
        tree = make_tree(tree_frame, columns, col_cfg)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=tree.yview,
                            style="Thin.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.bind("<<TreeviewSelect>>",
                  lambda e: selected_id.set(
                      int(tree.item(tree.selection()[0], "values")[0])
                      if tree.selection() else 0))

        all_data = []

        def load_data():
            nonlocal all_data
            try:
                all_data = list(view_patients_db())
                apply_filter()
                show_message(f"{len(all_data)} patient records loaded", "success")
            except Exception as ex:
                show_message(f"Error: {ex}", "error")

        def apply_filter(*_):
            q = filter_var.get().strip().lower()
            filtered = [r for r in all_data
                        if q in " ".join(map(str, r)).lower()] if q else all_data
            populate_tree(tree, filtered)
            count_label.config(
                text=f"{len(filtered)} record{'s' if len(filtered)!=1 else ''}")

        filter_var.trace_add("write", apply_filter)
        load_data()

    def _open_edit_patient(patient_id, refresh_callback):
        records = search_patient_db(patient_id=patient_id)
        if not records:
            show_message("Patient not found", "error"); return
        pid, name, age, sex, phone = records[0]

        win = tk.Toplevel()
        win.title("Edit Patient")
        win.geometry("400x420")
        win.configure(bg=COLORS["white"])
        win.grab_set()

        tk.Label(win, text="Edit Patient", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["text_dark"]).pack(pady=(20, 10))

        form = tk.Frame(win, bg=COLORS["white"])
        form.pack(fill="x", padx=24)

        def field(label_text, value):
            tk.Label(form, text=label_text, font=FONTS["label_bold"],
                     fg=COLORS["text_mid"], bg=COLORS["white"],
                     anchor="w").pack(fill="x", pady=(10, 2))
            e = styled_entry(form)
            e.insert(0, str(value))
            e.pack(fill="x", ipady=6)
            return e

        name_e  = field("Name", name)
        age_e   = field("Age",  age)

        tk.Label(form, text="Sex", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(10, 2))
        sv = tk.StringVar(value=sex)
        ttk.Combobox(form, textvariable=sv,
                     values=["Male","Female","Other"],
                     font=FONTS["entry"],
                     state="readonly").pack(fill="x", ipady=4)

        phone_e = field("Phone", phone or "")

        def save():
            nn, na, ns, np_ = (name_e.get().strip(), age_e.get().strip(),
                               sv.get().strip(), phone_e.get().strip())
            if not nn or not na.isdigit() or not ns:
                show_message("All fields must be valid", "error"); return
            if update_patient_information_db(patient_id, nn, int(na), ns, np_):
                show_message("Patient updated", "success")
                win.destroy(); refresh_callback()
            else:
                show_message("Update failed", "error")

        sb = tk.Label(win, text="Save Changes", font=FONTS["button"],
                      bg=COLORS["teal"], fg=COLORS["white"],
                      cursor="hand2", padx=24, pady=10)
        sb.pack(pady=20)
        sb.bind("<Button-1>", lambda e: save())

    # =====================================================
    # 4. SEARCH PATIENT
    # =====================================================
    def show_search_patient():
        clear_content()
        page_header("Search Patient",
                    "Find a patient by name or ID")

        body = tk.Frame(content_host, bg=COLORS["off_white"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        sco = tk.Frame(body, bg=COLORS["slate"])
        sco.pack(fill="x", pady=(0, 16))
        sc = tk.Frame(sco, bg=COLORS["white"])
        sc.pack(fill="x", padx=1, pady=1)

        inner = tk.Frame(sc, bg=COLORS["white"])
        inner.pack(fill="x", padx=24, pady=18)

        tk.Label(inner, text="Patient Name or ID", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"],
                 bg=COLORS["white"]).pack(anchor="w", pady=(0, 6))

        srow = tk.Frame(inner, bg=COLORS["white"])
        srow.pack(fill="x")

        search_entry = styled_entry(srow)
        search_entry.pack(side="left", fill="x", expand=True, ipady=8)

        sl = underline(inner); sl.pack(fill="x", pady=(0, 4))
        bind_focus_line(search_entry, sl)

        columns = ("ID", "Name", "Age", "Sex", "Phone")
        col_cfg = {"ID": (60,"center"), "Name": (240,"w"),
                   "Age": (70,"center"), "Sex": (90,"center"),
                   "Phone": (140,"center")}
        tree = make_tree(body, columns, col_cfg, height=10)

        vsb = ttk.Scrollbar(body, orient="vertical",
                            command=tree.yview,
                            style="Thin.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)

        result_label = tk.Label(body, text="", font=FONTS["small"],
                                fg=COLORS["text_mid"],
                                bg=COLORS["off_white"])

        def do_search():
            kw = search_entry.get().strip()
            if not kw:
                show_message("Enter a name or ID", "error"); return
            try:
                data = (search_patient_db(patient_id=int(kw))
                        if kw.isdigit()
                        else search_patient_db(name=kw))
                if not data:
                    tree.delete(*tree.get_children())
                    result_label.config(text="No matching records found",
                                        fg=COLORS["error"])
                    show_message("No patient found", "error"); return
                populate_tree(tree, data)
                result_label.config(
                    text=f"{len(data)} result{'s' if len(data)!=1 else ''} found",
                    fg=COLORS["success"])
                show_message(f"{len(data)} result(s) found", "success")
            except Exception as ex:
                show_message(f"Search error: {ex}", "error")

        sb = tk.Label(srow, text="Search", font=FONTS["button"],
                      bg=COLORS["teal"], fg=COLORS["white"],
                      cursor="hand2", padx=20, pady=8)
        sb.pack(side="right", padx=(12, 0))
        sb.bind("<Button-1>", lambda e: do_search())
        sb.bind("<Enter>", lambda e: sb.config(bg=COLORS["teal_light"]))
        sb.bind("<Leave>", lambda e: sb.config(bg=COLORS["teal"]))
        search_entry.bind("<Return>", lambda e: do_search())

        result_label.pack(anchor="w", pady=(0, 6))
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        search_entry.focus_set()

    # =====================================================
    # 5. ADD SCAN
    # =====================================================
    def show_add_scan():
        clear_content()
        page_header("Add Scan", "Record a new imaging scan for a patient")

        body = tk.Frame(content_host, bg=COLORS["off_white"])
        body.pack(fill="both", expand=True, padx=32, pady=20)

        co = tk.Frame(body, bg=COLORS["slate"])
        co.pack(fill="x", pady=4)
        card = tk.Frame(co, bg=COLORS["white"])
        card.pack(fill="x", padx=1, pady=1)

        form = tk.Frame(card, bg=COLORS["white"])
        form.pack(fill="x", padx=30, pady=24)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        left = tk.Frame(form, bg=COLORS["white"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        tk.Label(left, text="Patient ID *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        pid_entry = styled_entry(left)
        pid_entry.pack(fill="x", ipady=7)
        pidl = underline(left); pidl.pack(fill="x")
        bind_focus_line(pid_entry, pidl)

        tk.Label(left, text="Scan Type *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(16, 4))
        st_var = tk.StringVar()
        st_combo = ttk.Combobox(left, textvariable=st_var,
                                values=["X-Ray","CT Scan","MRI","Ultrasound",
                                        "PET Scan","Mammography","Fluoroscopy"],
                                font=FONTS["entry"], state="readonly")
        st_combo.pack(fill="x", ipady=4)

        tk.Label(left, text="Body Region *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(16, 4))
        br_var = tk.StringVar()
        br_combo = ttk.Combobox(left, textvariable=br_var,
                                values=BODY_REGIONS,
                                font=FONTS["entry"], state="readonly")
        br_combo.pack(fill="x", ipady=4)

        right = tk.Frame(form, bg=COLORS["white"])
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        tk.Label(right, text="Scan Date * (YYYY-MM-DD)", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        date_entry = styled_entry(right)
        date_entry.pack(fill="x", ipady=7)
        dl = underline(right); dl.pack(fill="x")
        bind_focus_line(date_entry, dl)

        tk.Label(right, text="Image Path *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(16, 4))
        img_frame = tk.Frame(right, bg=COLORS["white"])
        img_frame.pack(fill="x")
        img_entry = styled_entry(img_frame)
        img_entry.pack(side="left", fill="x", expand=True, ipady=7)

        def browse():
            f = filedialog.askopenfilename(
                title="Select Scan Image",
                filetypes=[("Image Files","*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.dcm"),
                           ("All Files","*.*")])
            if f:
                img_entry.delete(0, tk.END)
                img_entry.insert(0, f)

        tk.Button(img_frame, text="Browse", command=browse).pack(side="left", padx=8)
        il = underline(right); il.pack(fill="x")
        bind_focus_line(img_entry, il)

        nf = tk.Frame(card, bg=COLORS["white"])
        nf.pack(fill="x", padx=30, pady=(0, 8))
        tk.Label(nf, text="Clinical Notes", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        notes = tk.Text(nf, font=FONTS["entry"], relief="flat",
                        bg=COLORS["off_white"], fg=COLORS["text_dark"],
                        insertbackground=COLORS["teal"], bd=0,
                        height=4, wrap="word")
        notes.pack(fill="x")
        nl2 = underline(nf); nl2.pack(fill="x")
        notes.bind("<FocusIn>",  lambda e: nl2.config(bg=COLORS["teal"]))
        notes.bind("<FocusOut>", lambda e: nl2.config(bg=COLORS["slate"]))

        def save_scan():
            pid = pid_entry.get().strip()
            stype = st_var.get().strip()
            region = br_var.get().strip()
            sdate = date_entry.get().strip()
            history = notes.get("1.0", tk.END).strip()
            img = img_entry.get().strip()

            errors = []
            if not pid:           errors.append("Patient ID is required")
            elif not pid.isdigit():errors.append("Patient ID must be a number")
            if not stype:         errors.append("Scan type is required")
            if not region:        errors.append("Body region is required")
            if not sdate:         errors.append("Scan date is required")
            if not img:           errors.append("Image path is required")
            if errors:
                show_message(errors[0], "error"); return

            try:
                result = add_scan_db(int(pid), stype, region, sdate, history, img)
                if not result:
                    show_message("Invalid date, patient not found, or duplicate scan",
                                 "error"); return
                show_message("Scan saved successfully", "success")
                for e in (pid_entry, date_entry): e.delete(0, tk.END)
                st_combo.set(""); br_combo.set("")
                notes.delete("1.0", tk.END)
                img_entry.delete(0, tk.END)
                pid_entry.focus_set()
            except Exception as ex:
                show_message(f"Database error: {ex}", "error")

        br = tk.Frame(card, bg=COLORS["white"])
        br.pack(fill="x", padx=30, pady=(8, 24))
        sb = tk.Label(br, text="Save Scan Record", font=FONTS["button"],
                      bg=COLORS["teal"], fg=COLORS["white"],
                      cursor="hand2", padx=24, pady=10)
        sb.pack(side="left")
        sb.bind("<Button-1>", lambda e: save_scan())
        sb.bind("<Enter>", lambda e: sb.config(bg=COLORS["teal_light"]))
        sb.bind("<Leave>", lambda e: sb.config(bg=COLORS["teal"]))
        pid_entry.focus_set()

    # =====================================================
    # 6. VIEW SCANS
    # =====================================================
    def show_view_scans():
        clear_content()
        page_header("Scan Records", "All imaging scans in the system")

        toolbar = tk.Frame(content_host, bg=COLORS["off_white"])
        toolbar.pack(fill="x", padx=24, pady=(12, 4))
        count_lbl = tk.Label(toolbar, text="", font=FONTS["small"],
                             fg=COLORS["text_mid"], bg=COLORS["off_white"])
        count_lbl.pack(side="right", padx=8)

        tf = tk.Frame(content_host, bg=COLORS["white"])
        tf.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        columns = ("ScanID","PatientID","Type","Region","Date","History","ImagePath")
        col_cfg = {
            "ScanID":(60,"center"),"PatientID":(80,"center"),
            "Type":(90,"center"),"Region":(120,"w"),
            "Date":(100,"center"),"History":(180,"w"),"ImagePath":(160,"w")}
        tree = make_tree(tf, columns, col_cfg)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview,
                            style="Thin.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        try:
            data = list(view_scans_db())
            populate_tree(tree, data)
            count_lbl.config(text=f"{len(data)} scan(s)")
            show_message(f"{len(data)} scan records loaded", "success")
        except Exception as ex:
            show_message(f"Error loading scans: {ex}", "error")

    # =====================================================
    # 7. ADD REPORT
    # =====================================================
    def show_add_report():
        clear_content()
        page_header("Add Radiology Report",
                    "Compose and save a diagnostic report for a scan")

        body = tk.Frame(content_host, bg=COLORS["off_white"])
        body.pack(fill="both", expand=True, padx=32, pady=20)

        co = tk.Frame(body, bg=COLORS["slate"])
        co.pack(fill="both", expand=True, pady=4)
        card = tk.Frame(co, bg=COLORS["white"])
        card.pack(fill="both", expand=True, padx=1, pady=1)

        mf = tk.Frame(card, bg=COLORS["white"])
        mf.pack(fill="x", padx=30, pady=24)
        mf.columnconfigure(0, weight=1)
        mf.columnconfigure(1, weight=1)
        mf.columnconfigure(2, weight=1)

        c0 = tk.Frame(mf, bg=COLORS["white"])
        c0.grid(row=0, column=0, sticky="ew")
        tk.Label(c0, text="Scan ID *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        scan_id_entry = styled_entry(c0)
        scan_id_entry.pack(fill="x", ipady=7)
        l0 = underline(c0); l0.pack(fill="x")
        bind_focus_line(scan_id_entry, l0)

        c1 = tk.Frame(mf, bg=COLORS["white"])
        c1.grid(row=0, column=1, sticky="ew", padx=(16, 0))
        tk.Label(c1, text="Radiologist *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        # pre-fill with the logged-in user's full name
        radio_entry = styled_entry(c1)
        radio_entry.insert(0, full_name)
        radio_entry.pack(fill="x", ipady=7)
        l1 = underline(c1); l1.pack(fill="x")
        bind_focus_line(radio_entry, l1)

        c2 = tk.Frame(mf, bg=COLORS["white"])
        c2.grid(row=0, column=2, sticky="ew", padx=(16, 0))
        tk.Label(c2, text="Status *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        status_var = tk.StringVar(value="Pending")
        ttk.Combobox(c2, textvariable=status_var,
                     values=["Pending", "Completed"],
                     font=FONTS["entry"],
                     state="readonly").pack(fill="x", ipady=4)

        rf = tk.Frame(card, bg=COLORS["white"])
        rf.pack(fill="x", padx=30, pady=(0, 8))
        tk.Label(rf, text="Report Text *", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        rtbox = tk.Text(rf, font=FONTS["entry"], relief="flat",
                        bg=COLORS["off_white"], fg=COLORS["text_dark"],
                        insertbackground=COLORS["teal"], bd=0,
                        height=8, wrap="word")
        rtbox.pack(fill="x")
        rl = underline(rf); rl.pack(fill="x")
        rtbox.bind("<FocusIn>",  lambda e: rl.config(bg=COLORS["teal"]))
        rtbox.bind("<FocusOut>", lambda e: rl.config(bg=COLORS["slate"]))

        def save_report():
            sid = scan_id_entry.get().strip()
            radio = radio_entry.get().strip()
            status = status_var.get().strip()
            rtext = rtbox.get("1.0", tk.END).strip()

            errors = []
            if not sid or not sid.isdigit(): errors.append("Valid Scan ID is required")
            if not radio:                    errors.append("Radiologist name is required")
            if not rtext:                    errors.append("Report text cannot be empty")
            if errors:
                show_message(errors[0], "error"); return

            try:
                if not add_report_db(int(sid), radio, status, rtext):
                    show_message("Scan not found or report already exists",
                                 "error"); return
                show_message("Report saved successfully", "success")
                scan_id_entry.delete(0, tk.END)
                rtbox.delete("1.0", tk.END)
                status_var.set("Pending")
                scan_id_entry.focus_set()
            except Exception as ex:
                show_message(f"Database error: {ex}", "error")

        br2 = tk.Frame(card, bg=COLORS["white"])
        br2.pack(fill="x", padx=30, pady=(8, 24))
        sb = tk.Label(br2, text="Save Report", font=FONTS["button"],
                      bg=COLORS["teal"], fg=COLORS["white"],
                      cursor="hand2", padx=24, pady=10)
        sb.pack(side="left")
        sb.bind("<Button-1>", lambda e: save_report())
        sb.bind("<Enter>", lambda e: sb.config(bg=COLORS["teal_light"]))
        sb.bind("<Leave>", lambda e: sb.config(bg=COLORS["teal"]))
        scan_id_entry.focus_set()

    # =====================================================
    # 8. VIEW REPORTS
    # =====================================================
    def show_view_reports():
        clear_content()
        page_header("Radiology Reports",
                    "Review pending and completed reports")

        tabs_row = tk.Frame(content_host, bg=COLORS["off_white"])
        tabs_row.pack(fill="x", padx=24, pady=(12, 0))

        action_row = tk.Frame(content_host, bg=COLORS["off_white"])
        action_row.pack(fill="x", padx=24, pady=(4, 4))

        tf = tk.Frame(content_host, bg=COLORS["white"])
        tf.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        columns = ("ReportID","ScanID","Radiologist","Status","ReportText")
        col_cfg = {
            "ReportID":(80,"center"),"ScanID":(80,"center"),
            "Radiologist":(150,"w"),"Status":(100,"center"),"ReportText":(300,"w")}
        tree = make_tree(tf, columns, col_cfg)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview,
                            style="Thin.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        current_tab = tk.StringVar(value="pending")
        tab_buttons = {}

        def load(tab_key):
            current_tab.set(tab_key)
            try:
                if tab_key == "pending":
                    data = list(view_pending_reports_db())
                elif tab_key == "completed":
                    data = list(view_completed_reports_db())
                else:
                    data = list(view_reports_db())
                populate_tree(tree, data)
                show_message(f"{len(data)} report(s) loaded", "success")
            except Exception as ex:
                show_message(f"Error: {ex}", "error")
            for k, b in tab_buttons.items():
                b.config(bg=COLORS["teal"] if k==tab_key else COLORS["slate"],
                         fg=COLORS["white"] if k==tab_key else COLORS["text_mid"])

        for lbl, key in [("Pending","pending"),("Completed","completed"),("All","all")]:
            b = tk.Label(tabs_row, text=lbl, font=FONTS["button"],
                        cursor="hand2", padx=18, pady=8)
            b.pack(side="left", padx=(0, 8))
            b.bind("<Button-1>", lambda e, k=key: load(k))
            tab_buttons[key] = b

        # only radiologists and admins can mark as completed
        if role in ("Radiologist", "Admin"):
            def mark_completed():
                sel = tree.selection()
                if not sel:
                    show_message("Select a report row first", "error"); return
                rid = tree.item(sel[0], "values")[0]
                if update_report_status_db(int(rid), "Completed"):
                    show_message(f"Report {rid} marked as Completed", "success")
                    load(current_tab.get())
                else:
                    show_message("Report not found", "error")

            mb = tk.Label(action_row, text="✔ Mark as Completed",
                          font=FONTS["button"], bg=COLORS["success"],
                          fg=COLORS["white"], cursor="hand2", padx=16, pady=8)
            mb.pack(side="left")
            mb.bind("<Button-1>", lambda e: mark_completed())

        load("pending")

    # =====================================================
    # 9. MANAGE USERS  (Admin only)
    # =====================================================
    def show_manage_users():
        clear_content()
        page_header("Manage Users",
                    "Create, view, and remove staff accounts")

        # ---- create user form ----
        co = tk.Frame(content_host, bg=COLORS["slate"])
        co.pack(fill="x", padx=24, pady=(12, 0))
        card = tk.Frame(co, bg=COLORS["white"])
        card.pack(fill="x", padx=1, pady=1)

        form = tk.Frame(card, bg=COLORS["white"])
        form.pack(fill="x", padx=24, pady=20)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=1)

        def col_field(col_idx, label_text):
            cf = tk.Frame(form, bg=COLORS["white"])
            cf.grid(row=0, column=col_idx, sticky="ew",
                    padx=(0 if col_idx==0 else 10, 0))
            tk.Label(cf, text=label_text, font=FONTS["label_bold"],
                     fg=COLORS["text_mid"], bg=COLORS["white"],
                     anchor="w").pack(fill="x", pady=(0, 4))
            e = styled_entry(cf)
            e.pack(fill="x", ipady=6)
            l = underline(cf); l.pack(fill="x")
            bind_focus_line(e, l)
            return e

        uname_e  = col_field(0, "Username")
        pw_e     = col_field(1, "Password")
        pw_e.config(show="•")
        fname_e  = col_field(2, "Full Name")

        role_cf = tk.Frame(form, bg=COLORS["white"])
        role_cf.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        tk.Label(role_cf, text="Role", font=FONTS["label_bold"],
                 fg=COLORS["text_mid"], bg=COLORS["white"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        role_var2 = tk.StringVar()
        ttk.Combobox(role_cf, textvariable=role_var2,
                     values=["Admin","Radiologist","Technician","Receptionist"],
                     font=FONTS["entry"],
                     state="readonly").pack(fill="x", ipady=4)

        def create_user():
            un = uname_e.get().strip()
            pw = pw_e.get()
            fn = fname_e.get().strip()
            rl = role_var2.get().strip()

            if not un or not pw or not rl:
                show_message("Username, password and role are required", "error")
                return
            if len(pw) < 6:
                show_message("Password must be at least 6 characters", "error")
                return

            if create_user_db(un, pw, rl, fn):
                show_message(f"User '{un}' created as {rl}", "success")
                for e in (uname_e, pw_e, fname_e): e.delete(0, tk.END)
                role_var2.set("")
                load_users()
            else:
                show_message(f"Username '{un}' is already taken", "error")

        btn_row = tk.Frame(card, bg=COLORS["white"])
        btn_row.pack(fill="x", padx=24, pady=(0, 16))
        cb = tk.Label(btn_row, text="Create User", font=FONTS["button"],
                      bg=COLORS["teal"], fg=COLORS["white"],
                      cursor="hand2", padx=20, pady=8)
        cb.pack(side="left")
        cb.bind("<Button-1>", lambda e: create_user())
        cb.bind("<Enter>", lambda e: cb.config(bg=COLORS["teal_light"]))
        cb.bind("<Leave>", lambda e: cb.config(bg=COLORS["teal"]))

        # ---- users table ----
        tf = tk.Frame(content_host, bg=COLORS["white"])
        tf.pack(fill="both", expand=True, padx=24, pady=(8, 16))

        columns = ("ID", "Username", "Role", "Full Name")
        col_cfg = {"ID":(60,"center"),"Username":(160,"w"),
                   "Role":(120,"center"),"Full Name":(200,"w")}
        tree = make_tree(tf, columns, col_cfg)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview,
                            style="Thin.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        # delete user button (below table)
        del_row = tk.Frame(content_host, bg=COLORS["off_white"])
        del_row.pack(fill="x", padx=24, pady=(0, 8))

        def delete_selected_user():
            sel = tree.selection()
            if not sel:
                show_message("Select a user row first", "error"); return
            uid, uname = (tree.item(sel[0], "values")[0],
                          tree.item(sel[0], "values")[1])

            if uname == current_user["username"]:
                show_message("You cannot delete your own account", "error"); return

            if messagebox.askyesno("Confirm Delete",
                    f"Delete user '{uname}'? They will no longer be able to log in."):
                if delete_user_db(int(uid)):
                    show_message(f"User '{uname}' deleted", "success")
                    load_users()
                else:
                    show_message("Delete failed", "error")

        db2 = tk.Label(del_row, text="🗑 Delete Selected User",
                       font=FONTS["button"], bg=COLORS["error"],
                       fg=COLORS["white"], cursor="hand2", padx=16, pady=8)
        db2.pack(side="left")
        db2.bind("<Button-1>", lambda e: delete_selected_user())

        def load_users():
            try:
                data = get_all_users_db()
                populate_tree(tree, data)
            except Exception as ex:
                show_message(f"Error loading users: {ex}", "error")

        load_users()

    # =====================================================
    # LOGOUT
    # =====================================================
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            root.destroy()
            # re-launch the login window
            show_login(lambda user: start_main_app(user))

    # =====================================================
    # REGISTER NAV BUTTONS  (only show allowed pages)
    # =====================================================
    all_nav_items = [
        ("Dashboard",    "⊞",  show_dashboard,      "dashboard"),
        ("Add Patient",  "➕", show_add_patient,    "add_patient"),
        ("View Patients","👥", show_view_patients,  "view"),
        ("Search",       "🔍", show_search_patient, "search"),
        ("Add Scan",     "🩻", show_add_scan,       "scan"),
        ("View Scans",   "📷", show_view_scans,     "view_scans"),
        ("Add Report",   "📄", show_add_report,     "report"),
        ("View Reports", "📋", show_view_reports,   "view_reports"),
        ("Manage Users", "👤", show_manage_users,   "manage_users"),
    ]

    for label, icon, cmd, key in all_nav_items:
        if key in allowed:
            make_nav_btn(label, icon, cmd, key)

    # ---- sidebar footer: role badge + logout ----
    tk.Frame(sidebar, bg=COLORS["navy_light"],
             height=1).pack(fill="x", side="bottom")

    logout_btn = tk.Label(sidebar, text="⏻  Logout", font=FONTS["small"],
                          fg=COLORS["text_light"], bg=COLORS["navy"],
                          cursor="hand2", pady=8)
    logout_btn.pack(side="bottom", fill="x", padx=16)
    logout_btn.bind("<Button-1>", lambda e: logout())
    logout_btn.bind("<Enter>",
                    lambda e: logout_btn.config(fg=COLORS["white"]))
    logout_btn.bind("<Leave>",
                    lambda e: logout_btn.config(fg=COLORS["text_light"]))

    role_color = ROLE_COLORS.get(role, COLORS["teal"])
    tk.Label(sidebar,
             text=f"  {role}  ",
             font=FONTS["small"],
             bg=role_color,
             fg=COLORS["white"],
             pady=4).pack(side="bottom", fill="x")

    tk.Label(sidebar, text=full_name, font=FONTS["small"],
             fg=COLORS["text_light"],
             bg=COLORS["navy"]).pack(side="bottom", pady=(8, 2))

    # ---- boot into dashboard ----
    nav_buttons["dashboard"]["activate"]()
    root.mainloop()


# ============================================================
# ENTRY POINT
# ============================================================
def start_gui():
    """
    Entry point. Shows the login screen first.
    On successful login, opens the main app window.
    """
    show_login(lambda user: start_main_app(user))


if __name__ == "__main__":
    start_gui()