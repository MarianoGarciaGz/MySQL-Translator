# MySQL Translator with ANTLR

MySQL Translator es una aplicación que permite transformar instrucciones MySQL escritas en español a lenguaje SQL estándar. Además, genera código para formularios en Python que permiten la inserción de datos en las tablas creadas en la base de datos.

## Características

- Traducción de comandos MySQL en español a SQL estándar.
- Generación de código Python para formularios de inserción de datos.
- Conexión y creación de bases de datos en MySQL.
- Interfaz gráfica amigable y estilizada.

## Requisitos

- Python 3.x
- MySQL Server
- Conector MySQL para Python (`mysql-connector-python`)
- ANTLR 4

## Instalación

1. Clona el repositorio:

   ```sh
   git clone https://github.com/tu_usuario/mysql-translator.git
   cd mysql-translator
   ```

2. Instala las dependencias:

   ```sh
   pip install -r requirements.txt
   ```

3. Asegúrate de tener ANTLR 4 instalado y disponible en tu PATH. Puedes descargar el jar de ANTLR 4 desde [aquí](https://www.antlr.org/download.html).

4. Genera los archivos de ANTLR para Python:
   ```sh
   java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 MySQL.g4
   ```

## Uso

1. Ejecuta la aplicación principal:

   ```sh
   python main.py
   ```

2. En la interfaz gráfica:

   - Ingresa las instrucciones MySQL en español en el área de entrada.
   - Haz clic en "Traducir" para convertir las instrucciones a SQL estándar.
   - Si no hay errores, podrás crear la base de datos y generar el código de aplicación.

3. Para crear la base de datos:

   - Haz clic en "Crear base de datos".

4. Para generar el código de la aplicación:
   - Haz clic en "Generar Código de Aplicación".
   - Los archivos generados se guardarán en la carpeta `app`.

## Ejemplo de Instrucciones MySQL en Español

```sql
crear mi_base_datos;
usar mi_base_datos;
tabla empleados inicio
  id_empleado numeros,
  nombre letras,
  edad numeros,
  fecha_nac fecha
fin;
tabla departamentos inicio
  id_departamento numeros,
  nombre letras,
  fk_empleado_id dependeDe empleados
fin;
cerrar;
```

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, abre un issue o un pull request para discutir cualquier cambio o mejora.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
