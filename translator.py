# translator.py
import tkinter as tk
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from MySQLParser import MySQLParser
from models import Tabla, Atributo


class MySQLTranslator(ParseTreeListener):
    def __init__(self, salida, error, db_name_callback):
        self.tablas = []
        self.tablaActual = None
        self.ok = False
        self.errores = 0
        self.nBD = ""
        self.salida = salida
        self.error = error
        self.db_name_callback = (
            db_name_callback  # Callback para establecer el nombre de la base de datos
        )

    def enterCreacion(self, ctx: MySQLParser.CreacionContext):
        self.nBD = ctx.ID().getText()
        self.db_name_callback(
            self.nBD
        )  # Establecer el nombre de la base de datos usando el callback
        self.ok = True
        self.salida.insert(tk.END, f"CREATE DATABASE IF NOT EXISTS {self.nBD};\n")

    def enterTabla(self, ctx: MySQLParser.TablaContext):
        self.ok = False
        tabla_nombre = ctx.ID().getText()
        self.salida.insert(
            tk.END,
            f"\nCREATE TABLE {self.nBD}.{tabla_nombre} (\n {tabla_nombre}_key INTEGER PRIMARY KEY AUTO_INCREMENT",
        )

        t = Tabla(tabla_nombre)
        self.tablas.append(t)
        self.tablaActual = t

        a = Atributo(f"{tabla_nombre}_key", "PRIMARY KEY")
        self.tablaActual.atributos.append(a)
        self.ok = True

    def exitTabla(self, ctx: MySQLParser.TablaContext):
        if self.ok:
            self.salida.insert(tk.END, "\n);\n")
        else:
            self.error.insert(tk.END, "Error en la creación de la tabla.\n")
            self.errores += 1

    def enterCampo(self, ctx: MySQLParser.CampoContext):
        self.ok = False
        id_nombre = ctx.ID().getText()
        tipo = ctx.getChild(1).getText()  # obteniendo el tipo de campo

        if tipo == "letras":
            self.salida.insert(tk.END, f"\n, {id_nombre} VARCHAR(400)")
            tipo = "VARCHAR(400)"
            self.ok = True
        elif tipo == "numeros":
            self.salida.insert(tk.END, f"\n, {id_nombre} DOUBLE")
            tipo = "DOUBLE"
            self.ok = True
        elif tipo == "fecha":
            self.salida.insert(tk.END, f"\n, {id_nombre} DATE")
            tipo = "DATE"
            self.ok = True
        else:
            self.error.insert(tk.END, f"Error de Tipos en ID: {id_nombre}\n")
            self.errores += 1

        if self.ok:
            a = Atributo(id_nombre, tipo)
            self.tablaActual.atributos.append(a)

    def enterForeign_key(self, ctx: MySQLParser.Foreign_keyContext):
        self.ok = False
        id1 = ctx.ID(0).getText()
        id2 = ctx.ID(1).getText()

        for tabla in self.tablas:
            if tabla.nombre == id2:
                for a in tabla.atributos:
                    if a.nombreAtributo == f"{id2}_key":
                        self.salida.insert(
                            tk.END, f"\n, fk_{id2}_{id1} INTEGER NOT NULL"
                        )
                        self.salida.insert(
                            tk.END,
                            f"\n, FOREIGN KEY (fk_{id2}_{id1}) REFERENCES {id2} ({id2}_key)",
                        )
                        a = Atributo(id1, "Llave Foranea")
                        self.tablaActual.atributos.append(a)
                        self.ok = True
                        break

        if not self.ok:
            self.error.insert(tk.END, "Error en generacion de Llave Foranea\n")
            self.errores += 1

    def enterCerrar(self, ctx: MySQLParser.CerrarContext):
        if self.ok and self.errores == 0:
            self.salida.insert(
                tk.END, "\n"
            )  # Terminar la última declaración CREATE TABLE
            for tabla in self.tablas:
                self.salida.insert(tk.END, f"\n\n -- Tabla: {tabla.nombre}")
                for a in tabla.atributos:
                    self.salida.insert(tk.END, f"\n-- Atributo:  {a.nombreAtributo}")
                    self.salida.insert(tk.END, f"\n \t-- TipoAtrib: {a.tipoAtributo}")
        else:
            self.error.insert(tk.END, f"Numero de Errores: {self.errores}")
