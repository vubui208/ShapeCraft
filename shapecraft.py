import os
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import turtle
import colorsys

USERS_FILE = "users.json"
PROJECTS_DIR = "projects"


def ensure_dirs():
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)


def load_users():
    ensure_dirs()
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_user_project_dir(username: str) -> str:
    path = os.path.join(PROJECTS_DIR, username)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


#canvas
class TurtleCanvasManager:
    def __init__(self, parent):
        self.canvas = tk.Canvas(
            parent, width=850, height=600, bg="white", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor("white")

        self.t = turtle.RawTurtle(self.screen)
        self.t.hideturtle()
        self.t.speed(0)
        self.screen.tracer(0)

    def reset(self):
        self.t.clear()
        self.t.penup()
        self.t.hideturtle()

    def clear(self):
        self.t.clear()
        self.screen.update()

    def draw_shape(self, cordinate):
        t = self.t
        t.penup()
        t.goto(cordinate["x"], cordinate["y"])
        t.setheading(cordinate.get("heading", 0))
        t.pendown()

        size = cordinate.get("size", 50)
        fill = cordinate.get("fill_color", "")
        pen = cordinate.get("pen_color", "black")
        thick = cordinate.get("pen_thickness", 2)

        t.color(pen, fill)
        t.pensize(thick)

        if fill:
            t.begin_fill()

        st = cordinate["type"]

        if st == "square":
            for i in range(4):
                t.forward(size)
                t.right(90)
        elif st == "rectangle":
            w = cordinate["width"]
            h = cordinate["height"]
            for i in range(2):
                t.forward(w)
                t.right(90)
                t.forward(h)
                t.right(90)

        elif st == "circle":
            t.circle(size)

        elif st == "triangle":
            for i in range(3):
                t.forward(size)
                t.left(120)

        elif st == "star":
            for i in range(5):
                t.forward(size)
                t.right(144)

        elif st == "polygon":
            sides = cordinate["sides"]
            ang = 360 / sides
            for i in range(sides):
                t.forward(size)
                t.right(ang)

        if fill:
            t.end_fill()

        t.penup()

    def draw_pattern(self, p):
        t = self.t
        t.penup()
        t.goto(p["x"], p["y"])
        t.setheading(p.get("heading", 0))
        t.pendown()

        t.color(p.get("color", "blue"))
        typ = p["type"]

        if typ == "spiral":
            L = p["start_length"]
            for _ in range(p["repeat"]):
                t.forward(L)
                t.right(p["turn_angle"])
                L += p["grow"]

        elif typ == "flower":
            for _ in range(p["petals"]):
                for _ in range(2):
                    t.circle(p["radius"], 60)
                    t.left(120)
                t.left(360 / p["petals"])

        elif typ == "mandala":
            for i in range(p["layers"]):
                r = (i + 1) * p["step"]
                for j in range(p["circles"]):
                    t.penup()
                    t.goto(0, 0)
                    t.setheading(360 * j / p["circles"])
                    t.forward(r)
                    t.pendown()
                    t.circle(5)

        elif typ == "grid":
            rows = p["rows"]
            cols = p["cols"]
            cell = p["cell_size"]
            x0, y0 = p["x"], p["y"]

            for r in range(rows + 1):
                t.penup()
                t.goto(x0, y0 - r * cell)
                t.pendown()
                t.forward(cols * cell)

            for c in range(cols + 1):
                t.penup()
                t.goto(x0 + c * cell, y0)
                t.pendown()
                t.setheading(-90)
                t.forward(rows * cell)

        elif typ == "random_walk":
            for _ in range(p["steps"]):
                t.setheading(random.choice([0, 90, 180, 270]))
                t.forward(p["step_len"])

        t.penup()


#shape config
class ShapeDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Shape")
        self.geometry("350x520")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text="Shape Type:", font=("Segoe UI", 11, "bold")).pack(pady=5)

        self.type_var = tk.StringVar(value="square")
        types = ["square", "rectangle", "circle", "triangle", "star", "polygon"]
        ttk.OptionMenu(
            self, self.type_var, "square", *types, command=self.update_fields
        ).pack()

        self.inputs = {}
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(pady=10)

        def add(label, key):
            ttk.Label(self.main_frame, text=label).pack()
            e = ttk.Entry(self.main_frame)
            e.pack(pady=3)
            self.inputs[key] = e

        add("X:", "x")
        add("Y:", "y")
        add("Size:", "size")
        add("Fill Color:", "fill_color")
        add("Pen Color:", "pen_color")
        add("Pen Thickness:", "pen_thickness")

        self.extra = ttk.Frame(self)
        self.extra.pack()
        self.update_fields("square")

        ttk.Button(self, text="Create", command=self.submit).pack(pady=15)

    def update_fields(self, st):
        for w in self.extra.winfo_children():
            w.destroy()

        if st == "rectangle":
            ttk.Label(self.extra, text="Width:").pack()
            self.w = ttk.Entry(self.extra)
            self.w.pack()

            ttk.Label(self.extra, text="Height:").pack()
            self.h = ttk.Entry(self.extra)
            self.h.pack()

        if st == "polygon":
            ttk.Label(self.extra, text="Sides:").pack()
            self.sides = ttk.Entry(self.extra)
            self.sides.pack()

    def submit(self):
        try:
            s = {
                "kind": "shape",
                "type": self.type_var.get(),
                "x": float(self.inputs["x"].get()),
                "y": float(self.inputs["y"].get()),
                "size": float(self.inputs["size"].get()),
                "fill_color": self.inputs["fill_color"].get(),
                "pen_color": self.inputs["pen_color"].get(),
                "pen_thickness": int(self.inputs["pen_thickness"].get()),
                "heading": 0,
            }
        except Exception:
            messagebox.showerror("Error", "Invalid input.")
            return

        if s["type"] == "rectangle":
            try:
                s["width"] = float(self.w.get())
                s["height"] = float(self.h.get())
            except Exception:
                messagebox.showerror("Error", "Invalid width/height.")
                return

        if s["type"] == "polygon":
            try:
                s["sides"] = int(self.sides.get())
            except Exception:
                messagebox.showerror("Error", "Invalid sides.")
                return

        self.result = s
        self.destroy()


#pattern config
class PatternDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Pattern")
        self.geometry("350x550")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text="Pattern Type:", font=("Segoe UI", 11, "bold")).pack(
            pady=5
        )

        self.type_var = tk.StringVar(value="spiral")
        types = ["spiral", "flower", "mandala", "grid", "random_walk"]
        ttk.OptionMenu(
            self, self.type_var, "spiral", *types, command=self.update_fields
        ).pack()

        self.inputs = {}
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(pady=10)

        def add(label, key):
            ttk.Label(self.main_frame, text=label).pack()
            e = ttk.Entry(self.main_frame)
            e.pack(pady=3)
            self.inputs[key] = e

        add("X:", "x")
        add("Y:", "y")
        add("Color:", "color")

        self.extra = ttk.Frame(self)
        self.extra.pack()
        self.update_fields("spiral")

        ttk.Button(self, text="Create", command=self.submit).pack(pady=15)

    def update_fields(self, ptype):
        for w in self.extra.winfo_children():
            w.destroy()

        def add(label):
            ttk.Label(self.extra, text=label).pack()
            e = ttk.Entry(self.extra)
            e.pack()
            return e

        if ptype == "spiral":
            self.r = add("Repeat:")
            self.turn = add("Turn Angle:")
            self.startl = add("Start Length:")
            self.grow = add("Grow Size:")

        elif ptype == "flower":
            self.petals = add("Petals:")
            self.radius = add("Radius:")

        elif ptype == "mandala":
            self.layers = add("Layers:")
            self.step = add("Step:")
            self.circles = add("Circle Count:")

        elif ptype == "grid":
            self.rows = add("Rows:")
            self.cols = add("Columns:")
            self.cell = add("Cell Size:")

        elif ptype == "random_walk":
            self.steps = add("Steps:")
            self.slen = add("Step Length:")

    def submit(self):
        try:
            p = {
                "kind": "pattern",
                "type": self.type_var.get(),
                "x": float(self.inputs["x"].get()),
                "y": float(self.inputs["y"].get()),
                "color": self.inputs["color"].get(),
                "heading": 0,
            }
        except Exception:
            messagebox.showerror("Error", "Invalid base values.")
            return

        t = p["type"]

        try:
            if t == "spiral":
                p["repeat"] = int(self.r.get())
                p["turn_angle"] = float(self.turn.get())
                p["start_length"] = float(self.startl.get())
                p["grow"] = float(self.grow.get())

            elif t == "flower":
                p["petals"] = int(self.petals.get())
                p["radius"] = float(self.radius.get())

            elif t == "mandala":
                p["layers"] = int(self.layers.get())
                p["step"] = float(self.step.get())
                p["circles"] = int(self.circles.get())

            elif t == "grid":
                p["rows"] = int(self.rows.get())
                p["cols"] = int(self.cols.get())
                p["cell_size"] = float(self.cell.get())

            elif t == "random_walk":
                p["steps"] = int(self.steps.get())
                p["step_len"] = float(self.slen.get())

        except Exception:
            messagebox.showerror("Error", "Invalid pattern values.")
            return

        self.result = p
        self.destroy()


#sidebar
class DesignFrame(ttk.Frame):
    def __init__(self, parent, app):
        self.color_cycle_running = False
        self.color_cycle_hue = 0

        super().__init__(parent)
        self.app = app

        self.project_name = None
        self.objects = []

        self.dragging_index = None
        self.offset_x = 0
        self.offset_y = 0

        side = tk.Frame(self, bg="#1f2b5b", padx=15, pady=15)
        side.pack(side="left", fill="y")

        tk.Label(
            side,
            text="Tools",
            fg="white",
            bg="#1f2b5b",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=10)

        def btn(text, cmd):
            tk.Button(
                side,
                text=text,
                bg="#3047a5",
                fg="white",
                activebackground="#4868d6",
                relief="flat",
                width=18,
                pady=5,
                command=cmd,
            ).pack(pady=5)

        btn("Draw Shape", self.draw_shape)
        btn("Draw Pattern", self.draw_pattern)
        btn("Background Color", self.bg_color)
        btn("Animation", self.animation)
        btn("Undo", self.undo)
        btn("Save", self.save_project)
        btn("Save As", self.save_as)
        btn("Back", lambda: self.app.show_frame("DashboardFrame"))

        wrap = tk.Frame(self, bg="#ccd4ff", bd=3, relief="ridge")
        wrap.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas_mgr = TurtleCanvasManager(wrap)

        c = self.canvas_mgr.canvas
        c.bind("<Button-1>", self.drag_start)
        c.bind("<B1-Motion>", self.drag_move)
        c.bind("<ButtonRelease-1>", self.drag_stop)

    #canvas (0,0 top-left) -> turtle (0,0 center)
    def to_turtle(self, cx, cy):
        return cx - 425, 300 - cy

    #hitbox drag
    def hit(self, obj, x, y):
        t = obj["type"]
        if t in ["square", "triangle", "star", "polygon", "circle"]:
            r = obj.get("size", 50)
            return (obj["x"] - r <= x <= obj["x"] + r) and (
                obj["y"] - r <= y <= obj["y"] + r
            )
        if t == "rectangle":
            w = obj["width"]
            h = obj["height"]
            return (obj["x"] - w <= x <= obj["x"] + w) and (
                obj["y"] - h <= y <= obj["y"] + h
            )
        return False

    #drag
    def drag_start(self, e):
        tx, ty = self.to_turtle(e.x, e.y)
        for i, o in enumerate(reversed(self.objects)):
            if o["kind"] == "shape" and self.hit(o, tx, ty):
                self.dragging_index = len(self.objects) - 1 - i
                self.offset_x = o["x"] - tx
                self.offset_y = o["y"] - ty
                return

    def drag_move(self, e):
        if self.dragging_index is None:
            return
        tx, ty = self.to_turtle(e.x, e.y)
        o = self.objects[self.dragging_index]
        o["x"] = tx + self.offset_x
        o["y"] = ty + self.offset_y
        self.fast_redraw(self.dragging_index)

    def drag_stop(self, e):
        self.dragging_index = None

    def fast_redraw(self, dragging=None):
        mgr = self.canvas_mgr
        mgr.reset()

        for i, o in enumerate(self.objects):
            if i == dragging:
                continue
            if o["kind"] == "shape":
                mgr.draw_shape(o)
            else:
                mgr.draw_pattern(o)

        if dragging is not None:
            o = self.objects[dragging]
            if o["kind"] == "shape":
                mgr.draw_shape(o)
            else:
                mgr.draw_pattern(o)

        mgr.screen.update()

    #redraw
    def redraw(self):
        mgr = self.canvas_mgr
        mgr.reset()
        for o in self.objects:
            if o["kind"] == "shape":
                mgr.draw_shape(o)
            else:
                mgr.draw_pattern(o)
        mgr.screen.update()

    #shape & pattern
    def draw_shape(self):
        dlg = ShapeDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.objects.append(dlg.result)
            self.redraw()

    def draw_pattern(self):
        dlg = PatternDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.objects.append(dlg.result)
            self.redraw()

    #background
    def bg_color(self):
        c = simpledialog.askstring("Background", "Enter color:")
        if not c:
            return
        try:
            self.canvas_mgr.screen.bgcolor(c)
            self.canvas_mgr.screen.update()
        except Exception:
            messagebox.showerror("Error", "Invalid color")
    #rgb
    def run_color_cycle(self):
        if not self.color_cycle_running:
            return
        

        #inc hue
        self.color_cycle_hue = (self.color_cycle_hue + 3) % 360
        hue = self.color_cycle_hue / 360

        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        rgb = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

        
        for o in self.objects:
            if o["kind"] == "shape":
                o["fill_color"] = rgb

        self.redraw()
        self.after(20, self.run_color_cycle)

    def animation(self):
        mode = simpledialog.askstring(
            "Animation",
            "rotate, move, blink, expand, contract, color_cycle",
        )
        if not mode:
            return
        mode = mode.lower()

        if mode == "rotate":
            self.color_cycle_running = False
            for _ in range(36):
                for o in self.objects:
                    o["heading"] = o.get("heading", 0) + 10
                self.redraw()
                self.update()
            return

        #move
        if mode == "move":
            self.color_cycle_running = False
            for _ in range(25):
                for o in self.objects:
                    o["x"] += 10
                self.redraw()
                self.update()
            return

        #expand
        if mode == "expand":
            self.color_cycle_running = False
            for _ in range(15):
                for o in self.objects:
                    if o["kind"] == "shape":
                        if o["type"] == "rectangle":
                            o["width"] *= 1.05
                            o["height"] *= 1.05
                        else:
                            o["size"] *= 1.05
                self.redraw()
                self.update()
            return

        #minimize
        if mode == "contract":
            self.color_cycle_running = False
            for _ in range(15):
                for o in self.objects:
                    if o["kind"] == "shape":
                        if o["type"] == "rectangle":
                            o["width"] *= 0.95
                            o["height"] *= 0.95
                        else:
                            o["size"] *= 0.95
                self.redraw()
                self.update()
            return

        #rgb
        if mode == "color_cycle":
            if not self.color_cycle_running:
                self.color_cycle_running = True
                self.color_cycle_hue = 0
                self.run_color_cycle()
            return




        #blink
        if mode == "blink":
            self.color_cycle_running = False
            backup = [dict(o) for o in self.objects]

            for i in range(10):
                if i % 2 == 0:
                    self.canvas_mgr.clear()
                else:
                    self.redraw()
                self.update()

            self.objects = backup
            self.redraw()
            return

    #undo
    def undo(self):
        if self.objects:
            self.objects.pop()
            self.redraw()

    #save
    def save_project(self):
        user = self.app.logged_in_user
        if not user:
            messagebox.showerror("Error", "Login required")
            return

        if not self.project_name:
            name = simpledialog.askstring("Project name", "Name:")
            if not name:
                return
            self.project_name = name

        path = os.path.join(get_user_project_dir(user), self.project_name + ".json")

        with open(path, "w") as f:
            json.dump({"objects": self.objects}, f, indent=2)

        messagebox.showinfo("Saved", path)

    #save as
    def save_as(self):
        user = self.app.logged_in_user
        if not user:
            messagebox.showerror("Error", "Login required")
            return

        name = simpledialog.askstring("Save As", "New name:")
        if not name:
            return

        self.project_name = name
        self.save_project()

    #load
    def load_project(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        self.objects = data.get("objects", [])
        self.project_name = os.path.splitext(os.path.basename(path))[0]
        self.redraw()

#gallery
class GalleryFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")

        ttk.Label(header, text="My Gallery", font=("Segoe UI", 20, "bold")).pack(
            side="left"
        )
        ttk.Button(
            header, text="Back", command=lambda: app.show_frame("DashboardFrame")
        ).pack(side="right")

        main = ttk.Frame(self)
        main.pack(expand=True, fill="both")

        self.listbox = tk.Listbox(main, width=30)
        self.listbox.pack(side="left", fill="y", padx=10)
        self.listbox.bind("<<ListboxSelect>>", self.preview)

        prev = ttk.Frame(main)
        prev.pack(side="right", expand=True, fill="both")
        ttk.Label(prev, text="Preview", font=("Segoe UI", 14, "bold")).pack()

        self.preview_canvas = TurtleCanvasManager(prev)

    def on_show(self):
        self.listbox.delete(0, tk.END)
        user = self.app.logged_in_user
        if not user:
            return

        d = get_user_project_dir(user)
        for f in os.listdir(d):
            if f.endswith(".json"):
                self.listbox.insert(tk.END, f)

        self.preview_canvas.clear()

    def preview(self, _):
        if not self.listbox.curselection():
            return

        fname = self.listbox.get(self.listbox.curselection()[0])
        user = self.app.logged_in_user
        path = os.path.join(get_user_project_dir(user), fname)

        with open(path, "r") as f:
            data = json.load(f)

        self.preview_canvas.reset()

        for o in data.get("objects", []):
            if o["kind"] == "shape":
                self.preview_canvas.draw_shape(o)
            else:
                self.preview_canvas.draw_pattern(o)

        self.preview_canvas.screen.update()


#dashboard
class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="ShapeCraft Studio", font=("Segoe UI", 24, "bold")).pack(
            pady=20
        )

        self.user_label = ttk.Label(self, text="", font=("Segoe UI", 11))
        self.user_label.pack()

        grid = ttk.Frame(self)
        grid.pack(pady=15)

        menu = [
            ("🎨 New Design", lambda: app.show_frame("DesignFrame")),
            ("📂 Open Existing", self.open_existing),
            ("🖼️ My Gallery", lambda: app.show_frame("GalleryFrame")),
            ("🚪 Logout", app.logout),
        ]

        for i, (text, cmd) in enumerate(menu):
            cell = ttk.Frame(grid, padding=15, relief="ridge", borderwidth=1)
            cell.grid(row=i // 2, column=i % 2, padx=15, pady=15)

            ttk.Label(cell, text=text, font=("Segoe UI", 13, "bold")).pack(pady=5)
            ttk.Button(cell, text="Open", command=cmd).pack()

    def on_show(self):
        self.user_label.config(text=f"Logged in as: {self.app.logged_in_user}")

    def open_existing(self):
        user = self.app.logged_in_user
        if not user:
            messagebox.showerror("Error", "Login required")
            return

        path = filedialog.askopenfilename(
            initialdir=get_user_project_dir(user),
            filetypes=[("JSON Files", "*.json")],
        )
        if not path:
            return

        self.app.frames["DesignFrame"].load_project(path)
        self.app.show_frame("DesignFrame")

#login page
class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        box = ttk.Frame(self, padding=20)
        box.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(box, text="ShapeCraft Studio", font=("Segoe UI", 22, "bold")).pack()
        ttk.Label(box, text="Login or Register").pack(pady=5)

        ttk.Label(box, text="Username").pack(anchor="w")
        self.u = ttk.Entry(box)
        self.u.pack()

        ttk.Label(box, text="Password").pack(anchor="w")
        self.p = ttk.Entry(box, show="*")
        self.p.pack()

        row = ttk.Frame(box)
        row.pack(pady=10)

        ttk.Button(row, text="Login", command=self.login).grid(row=0, column=0, padx=5)
        ttk.Button(row, text="Register", command=self.register).grid(
            row=0, column=1, padx=5
        )

    def login(self):
        self.app.login(self.u.get().strip(), self.p.get().strip())

    def register(self):
        self.app.register(self.u.get().strip(), self.p.get().strip())


class ShapeCraftApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShapeCraft Studio")
        self.geometry("1300x750")

        self.logged_in_user = None
        self.frames = {}

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (LoginFrame, DashboardFrame, DesignFrame, GalleryFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        f = self.frames[name]
        f.tkraise()
        if hasattr(f, "on_show"):
            f.on_show()

    def login(self, u, p):
        users = load_users()
        if u in users and users[u]["password"] == p:
            self.logged_in_user = u
            self.show_frame("DashboardFrame")
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self, u, p):
        if not u or not p:
            messagebox.showerror("Error", "Username/password required")
            return

        users = load_users()
        if u in users:
            messagebox.showerror("Error", "Username exists")
            return

        users[u] = {"password": p}
        save_users(users)
        messagebox.showinfo("Success", "Account created")

    def logout(self):
        self.logged_in_user = None
        self.show_frame("LoginFrame")



load_users()
app = ShapeCraftApp()
app.mainloop()
