# models.py
class Atributo:
    def __init__(self, nombre, tipo):
        self.nombreAtributo = nombre
        self.tipoAtributo = tipo


class Tabla:
    def __init__(self, nombre):
        self.nombre = nombre
        self.atributos = []
