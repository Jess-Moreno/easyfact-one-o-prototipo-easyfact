import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import datetime


from db import conectar
from mysql.connector import Error


COLOR_BG = "#AFEEEE"     
COLOR_HEADER = "#003366" 
COLOR_TEXT = "#1F0954"   
CARD_BG = "#E8F8F8"      


def fetch_clients():
    conn = conectar()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_products():
    conn = conectar()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def insert_client(nombre, documento, direccion, telefono, correo):
    conn = conectar()
    if not conn: return False, "No hay conexión"
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
    if not conn: return False, "No hay conexión"
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
    if not conn: return None
    cur = conn.cursor()
    cur.execute("SELECT id_cliente FROM clientes WHERE nombre = %s", (nombre,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def get_product_by_name(nombre):
    conn = conectar()
    if not conn: return None, None
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
    if not conn: return False, "No hay conexión"
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO facturas (id_cliente, fecha) VALUES (%s, CURDATE())", (id_cliente,))
        id_factura = cur.lastrowid
        cur.execute("INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio) VALUES (%s, %s, %s, %s)",
                    (id_factura, id_producto, cantidad, precio))
       
        cur.execute("""UPDATE facturas f
                       SET f.total = (
                           SELECT SUM(df.subtotal) FROM detalle_factura df WHERE df.id_factura = f.id_factura
                       )
                       WHERE f.id_factura = %s""", (id_factura,))
        conn.commit()
        return True, None
    except Error as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def fetch_invoices(filter_cliente=None):
    conn = conectar()
    if not conn: return []
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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Facturación - Prototipo")
        self.geometry("1000x650")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)

        
        self.title_font = tkfont.Font(family='Segoe UI', size=16, weight="bold")
        self.card_font = tkfont.Font(family='Segoe UI', size=12, weight="bold")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.frames = {}
        for F in (LoginScreen, DashboardScreen, RegisterInvoiceScreen, ConsultInvoicesScreen,
                  RegisterClientScreen, RegisterProductScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()



class LoginScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="Card.TFrame")

        header = tk.Frame(self, bg=COLOR_HEADER, height=80)
        header.pack(fill="x")
        ttk.Label(header, text="EasyFact One - Facturación", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=18, anchor="w")

        body = ttk.Frame(self, padding=30)
        body.pack(expand=True)

        ttk.Label(body, text="Usuario").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_user = ttk.Entry(body, width=40)
        self.entry_user.grid(row=0, column=1, pady=5)
        ttk.Label(body, text="Contraseña").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_pass = ttk.Entry(body, width=40, show="*")
        self.entry_pass.grid(row=1, column=1, pady=5)

        btn = ttk.Button(body, text="Iniciar sesión", command=lambda: controller.show_frame("DashboardScreen"))
        btn.grid(row=2, column=0, columnspan=2, pady=15)

class DashboardScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Panel Principal", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=12, anchor="w")

        
        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        
        card_frame = tk.Frame(body, bg=COLOR_BG)
        card_frame.pack()

        
        self.card_btn("Registrar factura", card_frame, 0, 0, lambda: controller.show_frame("RegisterInvoiceScreen"))
        self.card_btn("Consultar facturas", card_frame, 0, 1, lambda: controller.show_frame("ConsultInvoicesScreen"))
        self.card_btn("Registrar cliente", card_frame, 1, 0, lambda: controller.show_frame("RegisterClientScreen"))
        self.card_btn("Registrar producto", card_frame, 1, 1, lambda: controller.show_frame("RegisterProductScreen"))

        
        logout = ttk.Button(body, text="Cerrar sesión", command=lambda: controller.show_frame("LoginScreen"))
        logout.pack(side="bottom", pady=10)

    def card_btn(self, text, container, row, col, cmd):
        frame = tk.Frame(container, bg=CARD_BG, width=420, height=150, relief="raised", bd=1)
        frame.grid(row=row, column=col, padx=12, pady=12)
        frame.grid_propagate(False)
        lbl = tk.Label(frame, text=text, bg=CARD_BG, fg=COLOR_TEXT, font=self.controller.title_font)
        lbl.pack(expand=True)
        btn = ttk.Button(frame, text="Abrir", command=cmd)
        btn.pack(pady=8)

class RegisterInvoiceScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Registrar factura", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=12, anchor="w")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        
        ttk.Label(body, text="Cliente:").grid(row=0, column=0, sticky="w", pady=6)
        self.cb_cliente = ttk.Combobox(body, width=40)
        self.cb_cliente.grid(row=0, column=1, pady=6)
        
        ttk.Label(body, text="Producto:").grid(row=1, column=0, sticky="w", pady=6)
        self.cb_producto = ttk.Combobox(body, width=40)
        self.cb_producto.grid(row=1, column=1, pady=6)
        
        ttk.Label(body, text="Precio (unitario):").grid(row=2, column=0, sticky="w", pady=6)
        self.txt_precio = ttk.Entry(body, width=40)
        self.txt_precio.grid(row=2, column=1, pady=6)
        
        ttk.Label(body, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=6)
        self.txt_cantidad = ttk.Entry(body, width=40)
        self.txt_cantidad.grid(row=3, column=1, pady=6)
        
        self.lbl_total = ttk.Label(body, text="Total: $0", font=("Segoe UI", 12, "bold"))
        self.lbl_total.grid(row=4, column=0, columnspan=2, pady=10)

        
        btn_frame = ttk.Frame(body)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Calcular total", command=self.calcular_total).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Guardar factura", command=self.guardar_factura).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Volver", command=lambda: controller.show_frame("DashboardScreen")).pack(side="left", padx=8)

        self.load_data()

    def load_data(self):
        clients = fetch_clients()
        products = fetch_products()
        self.cb_cliente['values'] = [c[1] for c in clients]
        self.cb_producto['values'] = [p[1] for p in products]

        
        self.product_map = {p[1]: (p[0], float(p[2])) for p in products}

    def calcular_total(self):
        try:
            precio = float(self.txt_precio.get())
            cantidad = int(self.txt_cantidad.get())
            total = precio * cantidad
            self.lbl_total.config(text=f"Total: ${total:.2f}")
        except:
            messagebox.showerror("Error", "Precio o cantidad inválidos")

    def guardar_factura(self):
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
        if id_cliente is None:
            messagebox.showerror("Error", "Cliente no encontrado en la base de datos")
            return

        id_producto, precio = get_product_by_name(producto)
        if id_producto is None:
            messagebox.showerror("Error", "Producto no encontrado en la base de datos")
            return

        ok, err = insert_invoice_and_detail(id_cliente, id_producto, cantidad, precio)
        if ok:
            messagebox.showinfo("Éxito", "Factura guardada correctamente")
            
            self.cb_cliente.set("")
            self.cb_producto.set("")
            self.txt_precio.delete(0, tk.END)
            self.txt_cantidad.delete(0, tk.END)
            self.lbl_total.config(text="Total: $0")
        else:
            messagebox.showerror("Error", f"No se pudo guardar la factura: {err}")

class ConsultInvoicesScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Consultar facturas", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=12, anchor="w")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        search_frame = ttk.Frame(body)
        search_frame.pack(fill="x", pady=6)
        ttk.Label(search_frame, text="Buscar por cliente:").pack(side="left", padx=6)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=6)
        ttk.Button(search_frame, text="Buscar", command=self.buscar).pack(side="left", padx=6)
        ttk.Button(search_frame, text="Mostrar todo", command=self.cargar_todo).pack(side="left", padx=6)

        
        cols = ("id", "cliente", "fecha", "total")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=200)
        self.tree.pack(fill="both", expand=True, pady=10)

        self.cargar_todo()

    def cargar_todo(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = fetch_invoices()
        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def buscar(self):
        term = self.search_entry.get()
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = fetch_invoices(filter_cliente=term)
        for r in rows:
            self.tree.insert("", tk.END, values=r)

class RegisterClientScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Registrar cliente", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=12, anchor="w")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        labels = ["Nombre", "Documento", "Dirección", "Teléfono", "Correo"]
        self.entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(body, text=lab + ":").grid(row=i, column=0, sticky="w", pady=6)
            e = ttk.Entry(body, width=50)
            e.grid(row=i, column=1, pady=6)
            self.entries[lab.lower()] = e

        btn_frame = ttk.Frame(body)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Guardar cliente", command=self.guardar_cliente).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Volver", command=lambda: controller.show_frame("DashboardScreen")).pack(side="left", padx=6)

    def guardar_cliente(self):
        nombre = self.entries["nombre"].get()
        documento = self.entries["documento"].get()
        direccion = self.entries["dirección"].get()
        telefono = self.entries["teléfono"].get()
        correo = self.entries["correo"].get()

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        ok, err = insert_client(nombre, documento, direccion, telefono, correo)
        if ok:
            messagebox.showinfo("Guardado", "Cliente guardado correctamente")
            for e in self.entries.values():
                e.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"No se pudo guardar: {err}")

class RegisterProductScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        ttk.Label(header, text="Registrar producto", foreground="white", background=COLOR_HEADER,
                  font=controller.title_font).pack(padx=20, pady=12, anchor="w")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        labels = ["Nombre", "Descripción", "Precio", "Stock"]
        self.entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(body, text=lab + ":").grid(row=i, column=0, sticky="w", pady=6)
            e = ttk.Entry(body, width=50)
            e.grid(row=i, column=1, pady=6)
            self.entries[lab.lower()] = e

        btn_frame = ttk.Frame(body)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Guardar producto", command=self.guardar_producto).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Volver", command=lambda: controller.show_frame("DashboardScreen")).pack(side="left", padx=6)

    def guardar_producto(self):
        nombre = self.entries["nombre"].get()
        descripcion = self.entries["descripción"].get()
        precio = self.entries["precio"].get()
        stock = self.entries["stock"].get()

        if not nombre or not precio:
            messagebox.showerror("Error", "Nombre y precio son obligatorios")
            return

        try:
            precio = float(precio)
            stock = int(stock) if stock else 0
        except:
            messagebox.showerror("Error", "Precio/stock inválidos")
            return

        ok, err = insert_product(nombre, descripcion, precio, stock)
        if ok:
            messagebox.showinfo("Guardado", "Producto guardado correctamente")
            for e in self.entries.values():
                e.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"No se pudo guardar: {err}")




if __name__ == "__main__":
    app = App()
    app.mainloop()
