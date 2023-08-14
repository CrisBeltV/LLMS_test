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