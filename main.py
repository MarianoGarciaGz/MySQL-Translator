# main.py
import tkinter as tk
from tkinter import scrolledtext, messagebox  # Importar messagebox correctamente
import mysql.connector
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener  # Importar ErrorListener
from MySQLLexer import MySQLLexer
from MySQLParser import MySQLParser
from translator import MySQLTranslator


class MySQLErrorListener(ErrorListener):
    def __init__(self, error_area):
        super(MySQLErrorListener, self).__init__()
        self.error_area = error_area
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.error_area.insert(
            tk.END, f"Error de sintaxis en línea {line}, columna {column}: {msg}\n"
        )
        self.has_errors = True


def run_translator():
    input_text = input_area.get("1.0", tk.END)

    # Limpiar las áreas de texto
    output_area.delete("1.0", tk.END)
    error_area.delete("1.0", tk.END)

    input_stream = InputStream(input_text)

    lexer = MySQLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MySQLParser(stream)

    # Añadir el manejador de errores
    error_listener = MySQLErrorListener(error_area)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.inicio()

    translator = MySQLTranslator(output_area, error_area)
    walker = ParseTreeWalker()
    walker.walk(translator, tree)

    # Habilitar o deshabilitar el botón según los errores
    if error_listener.has_errors or translator.errores > 0:
        create_db_button.config(state=tk.DISABLED)
    else:
        create_db_button.config(state=tk.NORMAL)


def create_database():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Reemplaza con tu usuario de MySQL
            password="",  # Reemplaza con tu contraseña de MySQL
        )
        cursor = connection.cursor()

        # Ejecutar los comandos SQL compilados
        sql_commands = output_area.get("1.0", tk.END).strip()
        commands = sql_commands.split(";")
        for command in commands:
            if command.strip():
                cursor.execute(command.strip())

        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Éxito", "Base de datos creada exitosamente.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al crear la base de datos: {err}")


# Configuración de la ventana principal
root = tk.Tk()
root.title("MySQL Translator")

# Área de entrada
input_label = tk.Label(root, text="Entrada:")
input_label.pack()
input_area = scrolledtext.ScrolledText(root, width=80, height=10)
input_area.pack()

# Área de salida
output_label = tk.Label(root, text="Salida:")
output_label.pack()
output_area = scrolledtext.ScrolledText(root, width=80, height=10)
output_area.pack()

# Área de errores
error_label = tk.Label(root, text="Errores:")
error_label.pack()
error_area = scrolledtext.ScrolledText(root, width=80, height=10)
error_area.pack()

# Botón para ejecutar la traducción
translate_button = tk.Button(root, text="Traducir", command=run_translator)
translate_button.pack()

# Botón para crear la base de datos
create_db_button = tk.Button(
    root, text="Crear base de datos", command=create_database, state=tk.DISABLED
)
create_db_button.pack()

# Iniciar la aplicación
root.mainloop()
