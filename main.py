import tkinter as tk
from tkinter import scrolledtext, messagebox
import mysql.connector
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from MySQLLexer import MySQLLexer
from MySQLParser import MySQLParser
from translator import MySQLTranslator

# Definir las variables de conexión
host = "localhost"
user = "root"
password = ""
database = "your_database_name"  # Reemplaza con el nombre de tu base de datos


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

    # Habilitar o deshabilitar los botones según los errores
    if error_listener.has_errors or translator.errores > 0:
        create_db_button.config(state=tk.DISABLED)
        generate_code_button.config(state=tk.DISABLED)
        query_db_button.config(state=tk.DISABLED)
    else:
        create_db_button.config(state=tk.NORMAL)
        generate_code_button.config(state=tk.NORMAL)
        query_db_button.config(state=tk.NORMAL)


def create_database():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
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


def generate_application_code():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            with open(f"{table_name}_form.py", "w") as code_file:
                code_file.write("import tkinter as tk\n")
                code_file.write("from tkinter import messagebox\n")
                code_file.write("import mysql.connector\n\n")
                code_file.write(f"host = '{host}'\n")
                code_file.write(f"user = '{user}'\n")
                code_file.write(f"password = '{password}'\n")
                code_file.write(f"database = '{database}'\n\n")
                code_file.write("def insert_data():\n")
                code_file.write("    try:\n")
                code_file.write("        connection = mysql.connector.connect(\n")
                code_file.write("            host=host,\n")
                code_file.write("            user=user,\n")
                code_file.write("            password=password,\n")
                code_file.write("            database=database\n")
                code_file.write("        )\n")
                code_file.write("        cursor = connection.cursor()\n")
                code_file.write("        insert_query = f\"INSERT INTO ")
                code_file.write(f"{table_name} (")
                code_file.write(", ".join(column[0] for column in columns))
                code_file.write(") VALUES (")
                code_file.write(", ".join(["%s"] * len(columns)))
                code_file.write(")\"\n")
                code_file.write("        data = (\n")
                for column in columns:
                    code_file.write(f"            {column[0]}_entry.get(),\n")
                code_file.write("        )\n")
                code_file.write("        cursor.execute(insert_query, data)\n")
                code_file.write("        connection.commit()\n")
                code_file.write("        cursor.close()\n")
                code_file.write("        connection.close()\n")
                code_file.write("        messagebox.showinfo('Éxito', 'Datos insertados exitosamente.')\n")
                code_file.write("    except mysql.connector.Error as err:\n")
                code_file.write("        messagebox.showerror('Error', f'Error al insertar datos: {err}')\n\n")

                code_file.write("root = tk.Tk()\n")
                code_file.write(f"root.title('Insertar datos en {table_name}')\n\n")

                for column in columns:
                    code_file.write(f"{column[0]}_label = tk.Label(root, text='{column[0]} ({column[1]})')\n")
                    code_file.write(f"{column[0]}_label.pack()\n")
                    code_file.write(f"{column[0]}_entry = tk.Entry(root)\n")
                    code_file.write(f"{column[0]}_entry.pack()\n\n")

                code_file.write("insert_button = tk.Button(root, text='Insertar', command=insert_data)\n")
                code_file.write("insert_button.pack()\n\n")
                code_file.write("root.mainloop()\n")

        cursor.close()
        connection.close()
        messagebox.showinfo("Éxito", "Código de la aplicación generado exitosamente.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al generar el código de la aplicación: {err}")


def query_databases():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")

        # Obtener y mostrar las bases de datos
        databases = cursor.fetchall()
        databases_list = "\n".join(db[0] for db in databases)
        messagebox.showinfo("Bases de Datos", f"Bases de datos en el servidor:\n{databases_list}")

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al consultar las bases de datos: {err}")


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

# Botón para generar el código de la aplicación
generate_code_button = tk.Button(
    root, text="Generar Código de Aplicación", command=generate_application_code, state=tk.DISABLED
)
generate_code_button.pack()

# Botón para consultar bases de datos
query_db_button = tk.Button(
    root, text="Consultar Bases de Datos", command=query_databases, state=tk.DISABLED
)
query_db_button.pack()

# Iniciar la aplicación
root.mainloop()
