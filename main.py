import pyodbc
import openai
import config
import typer
from rich import print
from rich.table import Table
import re
import replicate
import os


# Configuración de la base de datos
server = '(localdb)\ServidorDemos'
database = 'DB_LLMs_TEST'
username = ''
password = ''
driver= '{ODBC Driver 17 for SQL Server}'

connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = connection.cursor()

def fetch_from_db():
    cursor.execute('SELECT * FROM BOOKSTORE')
    results = []
    for row in cursor:
        results.append(row)
    return results


def get_table_schema_and_columns(table_name: str) -> dict:
    cursor.execute(f"SELECT TABLE_SCHEMA, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
    columns = cursor.fetchall()

    # Asumiendo que todos los registros tienen el mismo esquema para un nombre de tabla dado
    table_schema = columns[0].TABLE_SCHEMA if columns else None

    column_details = [
        {"name": row.COLUMN_NAME, "type": row.DATA_TYPE} for row in columns
    ]

    return column_details


def get_sql_from_prompt(prompt: str, table_name: str, table_details: list) -> str:
    """Usa GPT-3 para obtener una consulta SQL a partir de un prompt."""

    # Dado que table_details es ahora una lista, puedes crear directamente columns_detail
    columns_detail = ', '.join([f"{col['name']} ({col['type']})" for col in table_details])

    # Ahora, en la construcción del mensaje de contexto, ya no necesitas referenciar a ['columns'] o ['schema']
    # (porque no existen en la lista). Sin embargo, si quieres agregar el esquema, tendrías que pasarlo 
    # como un parámetro separado o hacer una suposición sobre él.

    context_msg = (f"Estás trabajando con la tabla DBO.{table_name}, "  # Suponemos que el esquema es "DBO"
                   f"la cual tiene las siguientes columnas: {columns_detail}."
                   "Genera una consulta SQL Server basada en la descripción dada. "
                   "Genera únicamente la consulta, sin comentarios, textos adicionales ni saltos de línea."
                   "Recuerda que SQL Server no utiliza la cláusula LIMIT."
                   "Tu respuesta sera igual a 'sql_query' y se ejecutara con 'cursor.execute(sql_query)'."
                   """
                    Este es un ejemplo correcto de una respuesta:
                    SELECT * FROM tabla WHERE FECHA = (SELECT MIN(FECHA) FROM tabla) UNION SELECT * FROM tabla WHERE FECHA = (SELECT MAX(FECHA) tabla)
                    Este es uno incorrecto
                    SELECT TOP 1 * FROM tabla ORDER BY FECHA ASC UNION SELECT TOP 1 * FROM tabla ORDER BY FECHA DESC
                   """)
    
    messagesCont = [
        {"role": "system", "content": context_msg},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messagesCont)
    print(response.choices[0].message.content)
    # result = extract_sql_from_response(response.choices[0].message.content)
    result = response.choices[0].message.content

    return result


def extract_sql_from_response(response: str) -> str:
    """Extrae la consulta SQL de una respuesta completa."""
    match = re.search(r'SELECT.*FROM.*(?:WHERE.*?(?:SELECT.*FROM.*?)*?)?(?:ORDER BY.*?(?:ASC|DESC))?(?:LIMIT\s*\d+)?;', response, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else None

def execute_sql(sql_query: str):
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append(row)
    return results

def main():
    openai.api_key = config.OPENAI_API_KEY
    os.environ["REPLICATE_API_TOKEN"] = config.LLAMA_REPLICATE_API_KEY
    
    print("💬 [bold green]ChatGPT API en Python[/bold green]")

    table = Table("Comando", "Descripción")
    table.add_row("exit", "Salir de la aplicación")
    table.add_row("new", "Crear una nueva conversación con GPT 3.5 🤖 💬")
    table.add_row("GPT3", "Crear una nueva conversación con GPT 3.5 🤖 💬")
    table.add_row("LLAMA2", "Crear una nueva conversación LLAMA 2 🦙 💬")
    table.add_row("Obtener_libros", "Consulta en la tabla  BOOKSTORE(libros de la base de datos)")
    table.add_row("Obtener_libros_x_Query", "Busca en la tabla BOOKSTORE por medio de consultas SQL")

    print(table)

    # Contexto del asistente
    context = {
        "role": "system",
        "content": "Eres un asistente experto en promps, bases de datos y programación. Solo respondes una vez como 'Asistente'"
    }
    messages = [context]

    while True:
        
        content = __prompt()

        if content == "new":
            print("🆕 Nueva conversación creada")
            messages = [context]
            content = __prompt()
        elif content.startswith("LLAMA2"):
            print("🆕 Nueva conversación creada 🦙 ")
            messages = [context]
            content = __prompt()
            # messages.append({"role": "user", "content": content})
            flag = 'LLAMA'
            
            output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                                    input={"prompt": concatenated_content, # Prompts
                                    "temperature":0.1, "top_p":0.9, "max_length":300, "repetition_penalty":1})  # Model parameters
            response_content = ""

            for item in output:
                response_content += item
                
            messages.append({"role": "user", "content": content})
            # Concatenar los valores de 'content'
            concatenated_content = '\n'.join([f"{message['role']}: {message['content']}" for message in messages])
            print(f"concatenated_content:{concatenated_content}")
            # Generate LLM response
            output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                                    input={"prompt": concatenated_content, # Prompts
                                    "temperature":0.1, "top_p":0.9, "max_length":300, "repetition_penalty":1})  # Model parameters
            response_content = ""

            for item in output:
                response_content += item    
                
            
        elif content == "Obtener_libros":
            flag = 'GPT3'
            books = fetch_from_db()
            response_content = f"He encontrado {len(books)} libros en la base de datos: " + ", ".join([book[1] for book in books])
            # Agregar los libros al contexto de mensajes
            books_text = books_to_text(books)
            messages.append({"role": "assistant", "content": books_text})
            #response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            #response_content = response.choices[0].message.content
            messages.append({"role": "assistant", "content": response_content})

        elif content.startswith("Obtener_libros_x_Query"):
            flag = 'QUERY'
            table_name = "BOOKSTORE"
            table_details = get_table_schema_and_columns(table_name)
            prompt = content.replace("Obtener_libros_x_Query", "").strip()
            messages.append({"role": "user", "content": prompt})
            print(f"prompt:{prompt}")
            sql_query = get_sql_from_prompt(prompt, table_name, table_details)
            print(f"sql_query:{sql_query}")

            if not sql_query:
                print(f"[bold red]Error:[/bold red] No pude generar una consulta SQL válida.")
                continue
            results = execute_sql(sql_query)
            response_content = f"He encontrado {len(results)} resultados: " + ", ".join([str(result) for result in results])
            messages.append({"role": "assistant", "content": response_content})
        else:
                print("🆕 Nueva conversación creada")
                messages.append({"role": "user", "content": content})

                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                response_content = response.choices[0].message.content
                messages.append({"role": "assistant", "content": response_content})
            
        
        print(f"messages:[blue]{messages}[/blue]")
        print(f"[bold green]> [/bold green] [green]{response_content}[/green]")


def books_to_text(books):
    text = "Los libros en la base de datos son:\n"
    for book in books:
        text += f"- Título: {book[1]}, Autor: {book[2]}, Fecha de Publicación: {book[3]}, Descripción: {book[4]}, Estado: {book[5]}\n"
    return text

def __prompt() -> str:
    prompt = typer.prompt("\n¿Sobre qué quieres hablar? ")

    if prompt == "exit":
        exit = typer.confirm("✋ ¿Estás seguro?")
        if exit:
            print("👋 ¡Hasta luego!")
            raise typer.Abort()
        return __prompt()
    return prompt

if __name__ == "__main__":
    typer.run(main)


