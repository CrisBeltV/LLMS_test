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

    #context_msg = f"La tabla {table_name} tiene las siguientes columnas: {', '.join(table_details)}. Genera una consulta SQL Server basada en la descripción dada, genera unicamente la consulta no agreges ni comentarios ni mas textos ni saltos linea. Ten en cuenta que SQL Server no utiliza la cláusula LIMIT."
    #context_msg = f"Write a SQL query to retrieve information. The table name is {TABLENAME}, has the next columns:{', '.join(table_columns)}. And the schema is DBO. Give me the output in the next format:
    #{
    #QUERY: str,
    #CONFINDENCE: 0-1,
    #IS_CORRECT:bool 
    #}"
    print("flag")
    print(table_details)
    columns_detail = ', '.join([f"{col['name']} ({col['type']})" for col in table_details['columns']])
    print(columns_detail)
    
    context_msg = (f"Estás trabajando con la tabla {table_details['schema']}.{table_name}, "
                   f"la cual tiene las siguientes columnas: {columns_detail}."
                   "Genera una consulta SQL Server basada en la descripción dada. "
                   "Genera únicamente la consulta, sin comentarios, textos adicionales ni saltos de línea. "
                   "Recuerda que SQL Server no utiliza la cláusula LIMIT.")
    
    
    messages = [
        {"role": "system", "content": context_msg},
        {"role": "user", "content": prompt}
    ]


    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    result = extract_sql_from_response(response.choices[0].message.content)

    return result



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
                   "Genera únicamente la consulta, sin comentarios, textos adicionales ni saltos de línea. "
                   "Recuerda que SQL Server no utiliza la cláusula LIMIT.")
    
    messages = [
        {"role": "system", "content": context_msg},
        {"role": "user", "content": prompt}
    ]
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    result = extract_sql_from_response(response.choices[0].message.content)

    return result


def extract_sql_from_response(response: str) -> str:
    """Extrae la consulta SQL de una respuesta completa."""
    match = re.search(r'SELECT.*FROM.*(?:WHERE.*?(?:SELECT.*FROM.*?)*?)?(?:ORDER BY.*?(?:ASC|DESC))?(?:LIMIT \d+)?;', response, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else None

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

        if content == "GPT3":
            print("🆕 Nueva conversación creada")
            messages = [context]
            content = __prompt()
            flag = 'GPT3'

        elif content == "LLAMA2":
            print("🆕 Nueva conversación creada 🦙 ")
            messages = [context]
            content = __prompt()
            # messages.append({"role": "user", "content": content})
            flag = 'LLAMA'

        elif content == "Obtener_libros":
            books = fetch_from_db()
            print(books)
            response_content = f"He encontrado {len(books)} libros en la base de datos: " + ", ".join([book[1] for book in books])
            print(response_content)
            # Agregar los libros al contexto de mensajes
            books_text = books_to_text(books)
            messages.append({"role": "assistant", "content": books_text})
        elif content.startswith("Obtener_libros_x_Query"):
            table_name = "BOOKSTORE"
            table_details = get_table_schema_and_columns(table_name)
            prompt = content.replace("BOOKSTORE", "").strip()
            sql_query = get_sql_from_prompt(prompt, table_name, table_details)
            if not sql_query:
                print(f"[bold red]Error:[/bold red] No pude generar una consulta SQL válida.")
                continue
            results = execute_sql(sql_query)
            response_content = f"He encontrado {len(results)} resultados: " + ", ".join([str(result) for result in results])
            
            
        if flag == 'LLAMA':
            print(f"Content:{content}")
            print(f"Messages1:")
            print(messages)
            messages.append({"role": "user", "content": content})
            print(f"Messages2:")
            print(messages)
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
        else:
            messages.append({"role": "user", "content": content})
            # Generate LLM response
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            
            response_content = response.choices[0].message.content
            
        
        messages.append({"role": "assistant", "content": response_content})
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


