import streamlit as st
from google import genai
from google.genai import types

# print("List of models that support generateContent:\n")
# for m in client.models.list():
#     for action in m.supported_actions:
#         if action == "generateContent" and m.name.endswith("lite"):
#             print(m.name)
#             print(m.input_token_limit)
#             print(m.output_token_limit)
#             print("=" * 40)


def generate_markdown_resume(json_data: str) -> str:

    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    system_prompt = """
    Eres un asesor académico de universidad experto. 
    Tu tarea es analizar el siguiente JSON y realizar una planificación
    de estudio perfecta para el inicio del curso (completa). 
    
    Este JSON contiene información del centro, titulación, curso (año) y asignaturas.
    Además contiene la guía docente de manera completa sobre cada asignatura, créditos,
    cuatrimestre (A/B) y carácter de tipo de formación (Básica / Obligatoria). 

    Hay algunas asignaturas en ciertas carreras que no tienen guía docente, en ese caso, lo deberas
    de avisar previamente y realizar aún así una estructuración del curso.
    
    El resultado debe ser generado de forma limpia en formato Markdown y para ser usado en Obsidian, 
    usa funcionalidades del mismo (tablas, desglose de asignaturas, checklist, consejos y tips, etc. TODO EN ESPAÑOL ).

    Usa una estructuración similar a:
    1. Resumen de asignatura y carga de créditos por cuatrimestre.
    2. Estructuración perfecta por cuatrimestre en base a dificultad y carga cognitiva y de estudio de cada asignatura.
        - Para evaluar la carga cognitiva, fíjate especialmente en los créditos de la asignatura y en el apartado de 'Evaluación' 
        (por ejemplo, si tiene muchos exámenes frente a entregas de trabajos).
    3. Consejos e información adicional para ir preparado de manera previa, estrategía y mejor manera de adquirir conocimientos.

    Ve directo al grano. No incluyas saludos, confirmaciones ni repitas el JSON proporcionado. Devuelve únicamente el contenido en Markdown.
    """

    user_prompt = f"Estos son los datos extraídos:\n\n{json_data}"

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,
            top_p=0.8,
            max_output_tokens=8192,
        ),
    )

    return response.text
