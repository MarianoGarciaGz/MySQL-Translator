# main.py
import tkinter as tk
from tkinter import scrolledtext
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener  # Importar ErrorListener
from MySQLLexer import MySQLLexer
from MySQLParser import MySQLParser
from translator import MySQLTranslator


class MySQLErrorListener(ErrorListener):
    def __init__(self, error_area):
        super(MySQLErrorListener, self).__init__()
        self.error_area = error_area

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.error_area.insert(
            tk.END, f"Error de sintaxis en línea {line}, columna {column}: {msg}\n"
        )


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

# Iniciar la aplicación
root.mainloop()
