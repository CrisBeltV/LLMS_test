import pyodbc
import openai
import config
import typer
from rich import print
from rich.table import Table

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


def main():
    openai.api_key = config.OPENAI_API_KEY
    print("💬 [bold green]ChatGPT API en Python[/bold green]")

    table = Table("Comando", "Descripción")
    table.add_row("exit", "Salir de la aplicación")
    table.add_row("new", "Crear una nueva conversación")
    table.add_row("get_books", "Consulta en los libros de la base de datos")
    print(table)

    # Contexto del asistente
    context = {
        "role": "system",
        "content": "Eres un asistente experto en promps, bases de datos y programación. y esta es tu base de datos"
    }
    messages = [context]

    while True:
        content = __prompt()

        if content == "new":
            print("🆕 Nueva conversación creada")
            messages = [context]
            content = __prompt()
        
        # Nuevo: comprobar si el usuario quiere obtener libros

        if content == "get_books":
            books = fetch_from_db()
            response_content = f"He encontrado {len(books)} libros en la base de datos: " + ", ".join([book[1] for book in books])
            # Agregar los libros al contexto de mensajes
            books_text = books_to_text(books)
            messages.append({"role": "assistant", "content": books_text})
        else:
            messages.append({"role": "user", "content": content})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages)
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


