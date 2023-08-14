context = {
        "role": "system",
        "content": "Eres un asistente experto en promps, bases de datos y programación."
    }

messages1 = [
    {'role': 'system', 'content': 'Eres un asistente experto en promps, bases de datos y programación. '},
    {'role': 'user', 'content': 'Que es el amor en pocas palabras?'},
    {
        'role': 'assistant',
        'content': 'El amor es un sentimiento profundo y complejo que se experimenta hacia otra persona, animal o actividad que nos hace sentir feliz, seguro y conectado. Se caracteriza por sentimientos de afecto, empatía, comprensión y deseo de estar juntos.'
    }
]

messages = [context]

concatenated_content = '\n'.join([f"{message['role']}: {message['content']}" for message in messages1])


print(concatenated_content)




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
    
    