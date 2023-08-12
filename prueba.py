import pyodbc
import openai
import config
import typer
from rich import print
from rich.table import Table
import re


# Configuración
openai.api_key = config.OPENAI_API_KEY
SERVER = config.SERVER
DATABASE = config.DATABASE
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
DRIVER = config.DRIVER


connection = pyodbc.connect('DRIVER=' + DRIVER + ';SERVER=' + SERVER + ';DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD)
cursor = connection.cursor()

def get_sql_from_prompt(prompt: str) -> str:
    """Usa GPT-3 para obtener una consulta SQL a partir de un prompt."""
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente experto en SQL. Genera consultas SQL basadas en las descripciones dadas."
        },
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content

def extract_sql_from_response(response: str) -> str:
    """Extrae la consulta SQL de una respuesta completa."""
    match = re.search(r'SELECT.*?FROM.*?(WHERE.*?)*;', response, re.IGNORECASE)
    return match.group(0) if match else None


def execute_sql(sql_query: str):
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append(row)
    return results

def main():
    openai.api_key = config.OPENAI_API_KEY
    print("💬 [bold green]ChatGPT API en Python[/bold green]")

    table = Table("Comando", "Descripción")
    table.add_row("exit", "Salir de la aplicación")
    table.add_row("new", "Crear una nueva conversación")
    table.add_row("get_books", "Consulta en los libros de la base de datos")
    print(table)

    while True:
        content = __prompt()
        
        if "consulta sql" in content:
            # El usuario desea una consulta SQL
            sql_query = get_sql_from_prompt(content)
            print(f"[bold blue]SQL[/bold blue]: [blue]{sql_query}[/blue]")
        else:
            # El usuario desea resultados
            sql_query = get_sql_from_prompt(f"Dame una consulta SQL para {content}")
            sql_query = extract_sql_from_response(sql_query)
            print(sql_query)
            results = execute_sql(sql_query)
            response_content = f"He encontrado {len(results)} resultados: " + ", ".join([str(result) for result in results])
            print(f"[bold green]> [/bold green] [green]{response_content}[/green]")

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
