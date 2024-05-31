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

# Variable para almacenar el nombre de la base de datos
global_database_name = ""


class MySQLErrorListener(ErrorListener):
    def __init__(self, error_area):
        super(MySQLErrorListener, self).__init__()
        self.error_area = error_area
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.error_area.insert(
            tk.END, f"Error de sintaxis en linea {line}, columna {column}: {msg}\n"
        )
        self.has_errors = True


def set_database_name(db_name):
    global global_database_name
    global_database_name = db_name


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

    tree = parser.inicio()  # Definir el árbol de análisis antes de pasarlo al traductor

    translator = MySQLTranslator(output_area, error_area, set_database_name)
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
        global global_database_name
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
        messagebox.showinfo(
            "Exito", f"Base de datos '{global_database_name}' creada exitosamente."
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al crear la base de datos: {err}")


def generate_application_code():
    try:
        global global_database_name
        # Verificar si se ha seleccionado una base de datos
        if not global_database_name:
            messagebox.showerror(
                "Error", "No se ha seleccionado ninguna base de datos."
            )
            return

        # Conectar a MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=global_database_name,  # Usar el nombre de la base de datos desde el código compilado
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
                code_file.write(f"database = '{global_database_name}'\n\n")
                code_file.write("def insert_data():\n")
                code_file.write("    try:\n")
                code_file.write("        connection = mysql.connector.connect(\n")
                code_file.write("            host=host,\n")
                code_file.write("            user=user,\n")
                code_file.write("            password=password,\n")
                code_file.write("            database=database\n")
                code_file.write("        )\n")
                code_file.write("        cursor = connection.cursor()\n")

                insert_query = f"INSERT INTO {table_name} ("
                data_values = ""
                data_entries = ""

                for column in columns:
                    if (
                        "auto_increment" in column[5]
                    ):  # Excluir campos auto incrementables y llaves foráneas
                        continue
                    insert_query += f"{column[0]}, "
                    data_values += "%s, "
                    data_entries += f"{column[0]}_entry.get(), "

                insert_query = (
                    insert_query.rstrip(", ")
                    + ") VALUES ("
                    + data_values.rstrip(", ")
                    + ")"
                )

                code_file.write(f'        insert_query = "{insert_query}"\n')
                code_file.write("        data = (\n")
                code_file.write(f"            {data_entries.rstrip(', ')}\n")
                code_file.write("        )\n")
                code_file.write("        cursor.execute(insert_query, data)\n")
                code_file.write("        connection.commit()\n")
                code_file.write("        cursor.close()\n")
                code_file.write("        connection.close()\n")
                code_file.write(
                    "        messagebox.showinfo('Exito', 'Datos insertados exitosamente.')\n"
                )
                code_file.write("    except mysql.connector.Error as err:\n")
                code_file.write(
                    "        messagebox.showerror('Error', f'Error al insertar datos: {err}')\n\n"
                )

                code_file.write("root = tk.Tk()\n")
                code_file.write(f"root.title('Insertar datos en {table_name}')\n\n")

                for column in columns:
                    if (
                        "auto_increment" in column[5]
                    ):  # Excluir campos auto incrementables y llaves foráneas
                        continue
                    code_file.write(
                        f"{column[0]}_label = tk.Label(root, text='{column[0]} ({column[1]})')\n"
                    )
                    code_file.write(f"{column[0]}_label.pack(pady=5)\n")
                    code_file.write(f"{column[0]}_entry = tk.Entry(root)\n")
                    code_file.write(f"{column[0]}_entry.pack(pady=5)\n\n")

                code_file.write(
                    "insert_button = tk.Button(root, text='Insertar', command=insert_data, bg='#4caf50', fg='white', font=('Helvetica', 12), padx=10, pady=5)\n"
                )
                code_file.write("insert_button.pack(pady=10)\n\n")
                code_file.write("root.configure(bg='#2b2b2b')\n")
                code_file.write("root.mainloop()\n")

        cursor.close()
        connection.close()
        messagebox.showinfo("Exito", "Codigo de la aplicacion generado exitosamente.")
    except mysql.connector.Error as err:
        messagebox.showerror(
            "Error", f"Error al generar el codigo de la aplicacion: {err}"
        )


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
        messagebox.showinfo(
            "Bases de Datos", f"Bases de datos en el servidor:\n{databases_list}"
        )

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al consultar las bases de datos: {err}")


# Configuración de la ventana principal
root = tk.Tk()
root.title("MySQL Translator")

# Estilo general
root.configure(bg="#2b2b2b")
font_style = ("Terminal", 11)
button_style = {
    "font": font_style,
    "bg": "#40e050",
    "fg": "white",
    "padx": 10,
    "pady": 5,
    "relief": "flat",
    "bd": 0,
}
label_style = {"font": font_style, "bg": "#2b2b2b", "fg": "white"}

# Área de entrada
input_label = tk.Label(root, text="Entrada:", **label_style)
input_label.pack(pady=(10, 0))
input_area = scrolledtext.ScrolledText(
    root,
    width=80,
    height=10,
    font=font_style,
    bg="#1e1e1e",
    fg="white",
    insertbackground="white",
    borderwidth=1,
    relief="sunken",
)
input_area.pack(pady=(0, 10))

# Área de salida
output_label = tk.Label(root, text="Salida:", **label_style)
output_label.pack(pady=(10, 0))
output_area = scrolledtext.ScrolledText(
    root,
    width=80,
    height=10,
    font=font_style,
    bg="#1e1e1e",
    fg="white",
    insertbackground="white",
    borderwidth=1,
    relief="sunken",
)
output_area.pack(pady=(0, 10))

# Área de errores
error_label = tk.Label(root, text="Errores:", **label_style)
error_label.pack(pady=(10, 0))
error_area = scrolledtext.ScrolledText(
    root,
    width=80,
    height=10,
    font=font_style,
    bg="#1e1e1e",
    fg="white",
    insertbackground="white",
    borderwidth=1,
    relief="sunken",
)
error_area.pack(pady=(0, 10))

# Botón para ejecutar la traducción
translate_button = tk.Button(
    root, text="Traducir", command=run_translator, **button_style
)
translate_button.pack(pady=(10, 0))

# Botón para crear la base de datos
create_db_button = tk.Button(
    root,
    text="Crear base de datos",
    command=create_database,
    state=tk.DISABLED,
    **button_style,
)
create_db_button.pack(pady=(10, 0))

# Botón para generar el código de la aplicación
generate_code_button = tk.Button(
    root,
    text="Generar Codigo de Aplicacion",
    command=generate_application_code,
    state=tk.DISABLED,
    **button_style,
)
generate_code_button.pack(pady=(10, 0))

# Botón para consultar bases de datos
query_db_button = tk.Button(
    root,
    text="Consultar Bases de Datos",
    command=query_databases,
    state=tk.DISABLED,
    **button_style,
)
query_db_button.pack(pady=(10, 20))

# Iniciar la aplicación
root.mainloop()
