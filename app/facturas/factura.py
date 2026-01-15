from app.clientes.cliente import Cliente
from app.productos.producto import Producto

class Factura:
    def __init__(self, cliente: Cliente):
        self.cliente = cliente
        self.detalles = []

    def agregar_producto(self, producto: Producto, cantidad: int):
        self.detalles.append((producto, cantidad))

    def total(self):
        return sum(prod.precio * cant for prod, cant in self.detalles)
