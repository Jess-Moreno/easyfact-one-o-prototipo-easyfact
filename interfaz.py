import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import datetime
import os
from PIL import Image, ImageTk

from db import conectar
from mysql.connector import Error

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "assets", "icons", "logo.png")

COLOR_BG = "#AFEEEE"
COLOR_HEADER = "#003366"
COLOR_TEXT = "#1F0954"
CARD_BG = "#E8F8F8"

def fetch_clients():
    conn = conectar()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_products():
    conn = conectar()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def insert_client(nombre, documento, direccion, telefono, correo):
    conn = conectar()
    if not conn:
        return False, "No hay conexión"
    cur = conn.cursor()
    try:
        sql = """INSERT INTO clientes (nombre, documento, direccion, telefono, correo)
                 VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(sql, (nombre, documento, direccion, telefono, correo))
        conn.commit()
        return True, None
    except Error as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def insert_product(nombre, descripcion, precio, stock):
    conn = conectar()
    if not conn:
        return False, "No hay conexión"
    cur = conn.cursor()
    try:
        sql = """INSERT INTO productos (nombre, descripcion, precio, stock)
                 VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, (nombre, descripcion, precio, stock))
        conn.commit()
        return True, None
    except Error as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def get_client_id_by_name(nombre):
    conn = conectar()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT id_cliente FROM clientes WHERE nombre = %s", (nombre,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None


def get_product_by_name(nombre):
    conn = conectar()
    if not conn:
        return None, None
    cur = conn.cursor()
    cur.execute("SELECT id_producto, precio FROM productos WHERE nombre = %s", (nombre,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0], float(row[1])
    return None, None


def insert_invoice_and_detail(id_cliente, id_producto, cantidad, precio):
    conn = conectar()
    if not conn:
        return False, "No hay conexión"
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO facturas (id_cliente, fecha) VALUES (%s, CURDATE())", (id_cliente,))
        id_factura = cur.lastrowid

        cur.execute(
            "INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio) VALUES (%s, %s, %s, %s)",
            (id_factura, id_producto, cantidad, precio)
        )

        cur.execute("""
            UPDATE facturas f SET total = (
               SELECT SUM(df.subtotal) FROM detalle_factura df WHERE df.id_factura = f.id_factura
            ) WHERE f.id_factura = %s
        """, (id_factura,))

        conn.commit()
        return True, None
    except Error as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()


def fetch_invoices(filter_cliente=None):
    conn = conectar()
    if not conn:
        return []
    cur = conn.cursor()
    base = """SELECT f.id_factura, c.nombre, f.fecha, f.total
              FROM facturas f
              JOIN clientes c ON f.id_cliente = c.id_cliente"""
    if filter_cliente:
        cur.execute(base + " WHERE c.nombre LIKE %s ORDER BY f.fecha DESC", (f"%{filter_cliente}%",))
    else:
        cur.execute(base + " ORDER BY f.fecha DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

class Login(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=80)
        header.pack(fill="x")
        ttk.Label(header, text="EasyFact One - Login", foreground="white",
                  background=COLOR_HEADER, font=controller.title_font).pack(padx=20, pady=18)

        body = ttk.Frame(self, padding=30)
        body.pack(expand=True)

        ttk.Label(body, text="Usuario").grid(row=0, column=0, pady=5)
        self.user = ttk.Entry(body, width=40)
        self.user.grid(row=0, column=1, pady=5)

        ttk.Label(body, text="Contraseña").grid(row=1, column=0, pady=5)
        self.passw = ttk.Entry(body, show="*", width=40)
        self.passw.grid(row=1, column=1, pady=5)

        ttk.Button(body, text="Entrar",
                   command=lambda: controller.show_frame("Dashboard")).grid(row=2, column=0, columnspan=2, pady=15)


class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=70)
        header.pack(fill="x")

        logo_frame = tk.Frame(header, bg=COLOR_HEADER)
        logo_frame.pack(side="left", padx=20)

        lbl_logo = tk.Label(logo_frame, image=controller.logo, bg=COLOR_HEADER)

        lbl_logo.image = controller.logo
        lbl_logo.pack()

        ttk.Label(header, text="Menu Principal", foreground="white",
                  background=COLOR_HEADER, font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)

        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(expand=True)

        cards = tk.Frame(body, bg=COLOR_BG)
        cards.pack()

        self.card("Registrar factura", cards, 0, 0,
        lambda: controller.show_frame("RegisterInvoice"),controller.icon_factura)

        self.card("Consultar facturas", cards, 0, 1,
        lambda: controller.show_frame("ConsultInvoices"),controller.icon_consultar)

        self.card("Registrar cliente", cards, 1, 0,
        lambda: controller.show_frame("RegisterClient"),controller.icon_cliente)

        self.card("Registrar producto", cards, 1, 1,
        lambda: controller.show_frame("RegisterProduct"),controller.icon_producto)

        ttk.Button(body, text="Cerrar sesión",
                   command=lambda: controller.show_frame("Login")).pack(pady=10)

    def card(self, text, container, r, c, cmd,icon):
        frame = tk.Frame(container, bg=CARD_BG, width=420, height=150, bd=1, relief="raised")
        frame.grid(row=r, column=c, padx=12, pady=12)
        frame.grid_propagate(False)

        
        tk.Label(frame, image=icon, bg=CARD_BG).pack(pady=10)
        tk.Label(frame, text=text, bg=CARD_BG, fg=COLOR_TEXT,
             font=self.controller.title_font).pack()

        ttk.Button(frame, text="Abrir", command=cmd).pack(pady=8)


class RegisterInvoice(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Registrar factura", foreground="white",
                  background=COLOR_HEADER, font=controller.title_font).pack(padx=20, pady=12)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Cliente:").grid(row=0, column=0, pady=6, sticky="w")
        self.cb_cliente = ttk.Combobox(body, width=40)
        self.cb_cliente.grid(row=0, column=1, pady=6)

        ttk.Label(body, text="Producto:").grid(row=1, column=0, pady=6, sticky="w")
        self.cb_producto = ttk.Combobox(body, width=40)
        self.cb_producto.grid(row=1, column=1, pady=6)

        ttk.Label(body, text="Precio").grid(row=2, column=0, pady=6, sticky="w")
        self.txt_precio = ttk.Entry(body, width=40)
        self.txt_precio.grid(row=2, column=1, pady=6)

        ttk.Label(body, text="Cantidad").grid(row=3, column=0, pady=6, sticky="w")
        self.txt_cantidad = ttk.Entry(body, width=40)
        self.txt_cantidad.grid(row=3, column=1, pady=6)

        self.lbl_total = ttk.Label(body, text="Total: $0", font=("Segoe UI", 12, "bold"))
        self.lbl_total.grid(row=4, column=0, columnspan=2, pady=12)

        btns = ttk.Frame(body)
        btns.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Calcular", command=self.calcular).pack(side="left", padx=8)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side="left", padx=8)
        ttk.Button(btns, text="Volver",
                   command=lambda: controller.show_frame("Dashboard")).pack(side="left", padx=8)

        self.load_data()

    def load_data(self):
        clients = fetch_clients()
        products = fetch_products()
        self.cb_cliente["values"] = [c[1] for c in clients]
        self.cb_producto["values"] = [p[1] for p in products]

    def calcular(self):
        try:
            p = float(self.txt_precio.get())
            c = int(self.txt_cantidad.get())
            self.lbl_total.config(text=f"Total: ${p*c:.2f}")
        except:
            messagebox.showerror("Error", "Datos inválidos")

    def guardar(self):
        cliente = self.cb_cliente.get()
        producto = self.cb_producto.get()
        cantidad = self.txt_cantidad.get()

        if not cliente or not producto or not cantidad:
            messagebox.showerror("Error", "Completa todos los campos")
            return

        try:
            cantidad = int(cantidad)
        except:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        id_cliente = get_client_id_by_name(cliente)
        id_producto, precio = get_product_by_name(producto)

        ok, err = insert_invoice_and_detail(id_cliente, id_producto, cantidad, precio)
        if ok:
            messagebox.showinfo("Éxito", "Factura guardada correctamente")
            self.cb_cliente.set("")
            self.cb_producto.set("")
            self.txt_precio.delete(0, tk.END)
            self.txt_cantidad.delete(0, tk.END)
            self.lbl_total.config(text="Total: $0")
        else:
            messagebox.showerror("Error", err)


class ConsultInvoices(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="Consultar facturas",
            foreground="white",
            background=COLOR_HEADER,
            font=controller.title_font
        ).pack(padx=20, pady=12)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        sf = ttk.Frame(body)
        sf.pack(fill="x")
        ttk.Label(sf, text="Buscar cliente:").pack(side="left")
        self.txt_buscar = ttk.Entry(sf, width=40)
        self.txt_buscar.pack(side="left", padx=6)
        ttk.Button(sf, text="Buscar", command=self.buscar).pack(side="left", padx=6)
        ttk.Button(sf, text="Ver todo", command=self.cargar_todo).pack(side="left", padx=6)

        cols = ("id", "cliente", "fecha", "total")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=200)
        self.tree.pack(fill="both", expand=True, pady=10)

    
        ttk.Button(
            body,
            text="Volver al menú",
            command=lambda: controller.show_frame("Dashboard")
        ).pack(pady=10)

        self.cargar_todo()

    def cargar_todo(self):
        self.tree.delete(*self.tree.get_children())
        for r in fetch_invoices():
            self.tree.insert("", tk.END, values=r)

    def buscar(self):
        text = self.txt_buscar.get()
        self.tree.delete(*self.tree.get_children())
        for r in fetch_invoices(text):
            self.tree.insert("", tk.END, values=r)

class RegisterClient(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Registrar Cliente",
            foreground="white",
            background=COLOR_HEADER,
            font=controller.title_font
        ).pack(padx=20, pady=12)

        body = ttk.Frame(self, padding=20)
        body.pack(fill="both", expand=True)

        labels = ["Nombre", "Documento", "Teléfono", "Correo"]
        self.entries = {}

        for i, text in enumerate(labels):
            ttk.Label(body, text=text + ":").grid(row=i, column=0, pady=8, sticky="w")
            entry = ttk.Entry(body, width=40)
            entry.grid(row=i, column=1, pady=8)
            self.entries[text] = entry

        btns = ttk.Frame(body)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=20)

        ttk.Button(
            btns,
            text="Guardar",
            command=self.guardar_cliente
        ).pack(side="left", padx=10)

        ttk.Button(
            btns,
            text="Volver al menú",
            command=lambda: controller.show_frame("Dashboard")
        ).pack(side="left", padx=10)

    def guardar_cliente(self):
        messagebox.showinfo(
            "Prototipo",
            "Cliente registrado correctamente"
        )


class RegisterProduct(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Registrar producto", foreground="white",
                  background=COLOR_HEADER, font=controller.title_font).pack(padx=20, pady=12)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        labels = ["Nombre", "Descripción", "Precio", "Stock"]
        self.e = {}

        for i, lab in enumerate(labels):
            ttk.Label(body, text=lab+":").grid(row=i, column=0, pady=6, sticky="w")
            ent = ttk.Entry(body, width=50)
            ent.grid(row=i, column=1, pady=6)
            self.e[lab.lower()] = ent

        btns = ttk.Frame(body)
        btns.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side="left", padx=8)
        ttk.Button(btns, text="Volver",
                   command=lambda: controller.show_frame("Dashboard")).pack(side="left", padx=8)

    def guardar(self):
        n = self.e["nombre"].get()
        p = self.e["precio"].get()

        if not n or not p:
            messagebox.showerror("Error", "Nombre y precio obligatorios")
            return

        try:
            precio = float(p)
            stock = int(self.e["stock"].get()) if self.e["stock"].get() else 0
        except:
            messagebox.showerror("Error", "Precio o stock inválidos")
            return

        ok, err = insert_product(
            self.e["nombre"].get(),
            self.e["descripción"].get(),
            precio,
            stock
        )

        if ok:
            messagebox.showinfo("Guardado", "Producto registrado")
            for x in self.e.values():
                x.delete(0, tk.END)
        else:
            messagebox.showerror("Error", err)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.icon_factura = ImageTk.PhotoImage(
    Image.open("assets/icons/factura.png").resize((55, 55))
        )
        self.icon_consultar = ImageTk.PhotoImage(
    Image.open("assets/icons/consultar.png").resize((55, 55))
        )
        self.icon_cliente = ImageTk.PhotoImage(
    Image.open("assets/icons/cliente.png").resize((55, 55))
        )
        self.icon_producto = ImageTk.PhotoImage(
    Image.open("assets/icons/producto.png").resize((55, 55))            
        )

        self.title("EasyFact One - Sistema de Facturación")
        self.geometry("1000x650")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        
        LOGO_PATH = os.path.join("assets", "icons", "logo.png")
        self.logo_img = Image.open(LOGO_PATH).resize((70, 70),Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(self.logo_img)
        
        logo_frame = tk.Frame(bg=COLOR_HEADER)
        logo_frame.pack(side="left", padx=20)

        self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.frames = {}
        for F in (Login, Dashboard, RegisterInvoice, ConsultInvoices, RegisterClient, RegisterProduct):
            page = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Login")

    def show_frame(self, page):
        self.frames[page].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
