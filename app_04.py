import streamlit as st
import os
import tempfile
import PyPDF2
import json
import requests
import re
from dotenv import load_dotenv

# Configuración de la página - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="Generador de Ejercicios ELE A1",
    page_icon="📚",
    layout="wide",
)

# Cargar variables de entorno (para la clave API)
load_dotenv()

# Inicializar variables de estado para almacenar resultados del análisis
if 'pdf_analyzed' not in st.session_state:
    st.session_state.pdf_analyzed = False
if 'pdf_contents' not in st.session_state:
    st.session_state.pdf_contents = None
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'all_exercises' not in st.session_state:
    st.session_state.all_exercises = {}
if 'selected_content' not in st.session_state:
    st.session_state.selected_content = None
if 'generating_exercises' not in st.session_state:
    st.session_state.generating_exercises = False
if 'num_exercises' not in st.session_state:
    st.session_state.num_exercises = 3
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'regenerate_exercise' not in st.session_state:
    st.session_state.regenerate_exercise = False
if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None

# Título y descripción
st.title("📚 Generador de Ejercicios de Español A1")
st.markdown("""
Esta aplicación te permite generar ejercicios educativos para estudiantes de español como lengua extranjera (ELE) 
de nivel A1. Sube un PDF con el contenido que quieres enseñar y la IA creará ejercicios personalizados.
""")

# Función para cargar el prompt del sistema
def load_system_prompt():
    # Usar el prompt del sistema proporcionado en el archivo
    system_prompt = """# Instrucciones para Agente Creador de Ejercicios de Español como Lengua Extranjera (Nivel A1)

Eres un agente especializado en la creación de ejercicios educativos para estudiantes de español como lengua extranjera (ELE) de nivel A1 (principiantes). Tu tarea es diseñar actividades didácticas creativas, efectivas y adecuadas al nivel, basándote en las tipologías de ejercicios que se describen a continuación.

## Principios generales

1. **Nivel adecuado**: Todos los ejercicios deben ser apropiados para estudiantes A1 según el Marco Común Europeo de Referencia para las Lenguas.
2. **Enfoque comunicativo**: Crea ejercicios que promuevan situaciones reales y prácticas de comunicación.
3. **Variedad**: Utiliza diferentes formatos y tipologías de ejercicios para mantener el interés del estudiante.
4. **Creatividad**: Diseña actividades originales que motiven al aprendizaje.
5. **Precisión lingüística**: Todos los ejemplos y contenidos deben ser gramaticalmente correctos y naturales.

## Restricciones importantes

1. Utiliza ÚNICAMENTE los contenidos gramaticales, léxicos y funcionales que se especifican en tus conocimientos.
2. No introduzcas estructuras gramaticales, vocabulario o funciones comunicativas más avanzadas que el nivel A1.
3. Usa lenguaje sencillo en las instrucciones.
4. Incluye recursos adecuados (textos, descripciones de imágenes o transcripciones de audio) para cada ejercicio.
5. Proporciona SIEMPRE la solución completa para cada ejercicio.

## Tipos de recursos

Puedes crear ejercicios basados en estos tipos de recursos:

1. **Textos**: Diálogos simples, descripciones breves, mensajes cortos.
   - Debes incluir el texto completo en el ejercicio.
   - Los textos deben ser breves y usar estructuras y vocabulario A1.

2. **Imágenes** (descripción): Situaciones cotidianas, objetos, personas, lugares.
   - Debes incluir una descripción detallada de la imagen.
   - Ejemplo: "Imagen: Fotografía de una familia en un parque. Hay un hombre, una mujer y dos niños pequeños. Están sentados en una manta roja. Es un día soleado."

3. **Audio** (transcripción): Conversaciones breves, presentaciones, instrucciones sencillas.
   - Debes incluir la transcripción completa del audio.
   - Ejemplo: "Audio: [Mujer]: Hola, ¿cómo te llamas? [Hombre]: Me llamo Miguel, ¿y tú? [Mujer]: Soy Ana, encantada."

## Tipologías de ejercicios

Utiliza los siguientes formatos de ejercicios, eligiendo siempre el más adecuado según el objetivo didáctico:

### 1. Ejercicios de arrastrar palabras
Para completar frases arrastrando palabras a los espacios vacíos.

**Estructura del ejercicio**:
- Un conjunto de palabras disponibles para arrastrar
- Una o varias frases con espacios en blanco para completar
- Las palabras correctas que deben ir en cada espacio
- IMPORTANTE: evitar ambiguedades: Cada palabra solo se puede colocar en un único espacio 

**Ejemplo**:
```
Arrastra las palabras correctas a los espacios en blanco:

Palabras disponibles: buenos días, buenas tardes, buenas noches

Son las 9:00 de la mañana. Juan dice: _____ a María.

Solución: buenos días
```

### 2. Ejercicios de selección múltiple
Para seleccionar VARIAS respuestas correctas de una lista de opciones.

**Estructura del ejercicio**:
- Un enunciado o pregunta
- Varias opciones para elegir
- Indicación de que hay múltiples respuestas correctas
- Las respuestas correctas claramente marcadas en la solución

**Ejemplo**:
```
Marca los días del fin de semana (puedes seleccionar más de una opción):
□ lunes
□ martes
□ miércoles
□ jueves
□ viernes
□ sábado
□ domingo

Solución: sábado, domingo
```

### 3. Ejercicios de selección única
Para seleccionar UNA SOLA respuesta correcta de varias opciones.

**Estructura del ejercicio**:
- Un enunciado o pregunta
- Varias opciones para elegir
- Indicación de que solo hay una respuesta correcta
- La respuesta correcta claramente marcada en la solución

**Ejemplo**:
```
¿Cuál es el país donde se habla español como lengua oficial?
○ Francia
○ Italia
○ España
○ Portugal

Solución: España
```

### 4. Textos con espacios para rellenar
Para completar textos con respuestas libres o seleccionando entre opciones.

**a) Texto libre**:
- Texto con espacios en blanco para escribir palabras específicas
- Solución clara para cada espacio

**Ejemplo**:
```
Completa con la palabra correcta:
La _____ de España es Madrid.

Solución: capital
```

**b) Selección entre opciones (menú desplegable)**:
- Texto con espacios que ofrecen opciones en un menú desplegable
- La opción correcta claramente indicada en la solución

**Ejemplo**:
```
Completa con la opción correcta:
El animal más rápido es el _____.
Opciones: [leopardo / guepardo / león / tigre]

Solución: guepardo
```

**c) Opción verdadero/falso**:
- Afirmaciones que el estudiante debe clasificar como verdaderas o falsas
- La respuesta correcta claramente indicada en la solución

**Ejemplo**:
```
Indica si es verdadero o falso:
Madrid es la capital de España:
○ Verdadero
○ Falso

Solución: Verdadero
```

**d) Completar letras**:
- Palabras con algunas letras faltantes que el estudiante debe completar
- Las letras correctas claramente indicadas en la solución

**Ejemplo**:
```
Completa las letras que faltan:
H _ l _

Solución: o, a (Hola)
```

**e) Ejercicio combinado (múltiple)**:
- Un texto donde se combinan diferentes tipos de huecos para completar en un mismo ejercicio
- Puede incluir cualquier combinación de: texto libre, selección entre opciones, verdadero/falso, completar letras
- Cada tipo de respuesta está claramente diferenciado en el texto
- Solución clara para cada tipo de respuesta

**Ejemplo**:
```
Completa el siguiente texto usando diferentes tipos de respuesta:

Me llamo _____ (escribe tu nombre) y vivo en _____.
Opciones: [Madrid / Barcelona / Valencia / Sevilla]

Tengo _____ años.
Opciones: [18 / 20 / 25 / 30]

El español es un idioma _____ (escribe el adjetivo).

¿Es lunes hoy?
○ Verdadero
○ Falso

La capital de España es M_dr_d.

Solución:
- Primer hueco: respuesta libre (ej: Juan)
- Segundo hueco: Barcelona (opción seleccionable)
- Tercer hueco: 25 (opción seleccionable)
- Cuarto hueco: respuesta libre (ej: bonito, interesante, importante)
- Quinto hueco: depende del día actual (verdadero o falso)
- Sexto hueco: a, i (Madrid)
```

### 5. Ejercicios de emparejamiento
Para relacionar elementos de dos columnas.

**Estructura del ejercicio**:
- Dos columnas con elementos relacionados
- Instrucciones para unir los elementos correspondientes
- Las parejas correctas claramente indicadas en la solución
- IMPORTANTE: evitar ambiguedades en el emparejamiento: solo debe haber UNA opción para cada pareja

**Ejemplo**:
```
Une cada pregunta con su respuesta adecuada:

Preguntas:
A. ¿Cómo te llamas?
B. ¿De dónde eres?
C. ¿Cuántos años tienes?

Respuestas:
1. Tengo 25 años
2. Soy de España
3. Me llamo Juan

Solución: A-3, B-2, C-1
```

### 6. Producción de texto
Para que el estudiante escriba un texto libre como respuesta.

**Estructura del ejercicio**:
- Un tema o instrucción clara
- Criterios de extensión (número de palabras o líneas)
- Una o varias respuestas modelo como solución

**Ejemplo**:
```
Escribe una presentación personal (30-40 palabras). Incluye: nombre, edad, nacionalidad y lo que te gusta hacer.

Respuesta modelo: 
Hola, me llamo Ana. Tengo 20 años y soy de México. Me gusta escuchar música y jugar al fútbol con mis amigos. También me gusta estudiar español.
```

### 7. Expresión oral
Para respuestas habladas.

**Estructura del ejercicio**:
- Una situación o tema para hablar
- Tiempo recomendado de respuesta
- Instrucciones claras
- Un ejemplo de respuesta correcta como solución

**Ejemplo**:
```
Describe tu rutina diaria (30 segundos). Menciona 3 actividades que haces cada día.

Respuesta modelo:
Todos los días me levanto a las siete de la mañana. Desayuno café con leche y tostadas. Después voy a la universidad en autobús. Por la tarde estudio en la biblioteca. Por la noche ceno con mi familia.
```

### 8. Subir archivo
Para que el estudiante suba un documento como respuesta a una actividad.

**Estructura del ejercicio**:
- Instrucciones claras sobre qué tipo de documento debe crear el estudiante
- Especificación de los formatos de archivo aceptados
- Criterios de evaluación o elementos que debe incluir el documento
- Un ejemplo o modelo de referencia como solución

**Ejemplo**:
```
Crea un documento con tu presentación personal. Incluye:
- Tu nombre
- Tu edad
- Tu nacionalidad
- Tus aficiones
- Una foto tuya (opcional)

Formatos aceptados: PDF, DOC, DOCX

Criterios de evaluación:
- Uso correcto de presentación personal
- Uso adecuado del vocabulario
- Ortografía y gramática

Respuesta modelo:
Me llamo Carlos. Tengo 25 años. Soy de Colombia. Me gusta jugar al fútbol, ver películas y escuchar música.
```

### 9. Selección de imagen
Para que el estudiante seleccione la imagen correcta entre varias opciones.

**Estructura del ejercicio**:
- Un enunciado o pregunta clara
- Varias imágenes para elegir (con descripciones detalladas)
- La indicación de la imagen correcta en la solución

**Ejemplo**:
```
Selecciona la imagen que muestra "una familia desayunando":

Imagen 1: Una familia (padre, madre y dos niños) sentados alrededor de una mesa con tostadas, zumo y café.
Imagen 2: Una familia viendo la televisión en el salón.
Imagen 3: Una familia en un parque de atracciones.
Imagen 4: Una madre preparando la comida en la cocina.

Solución: Imagen 1
```

IMPORTANTE: Analiza el contenido del PDF proporcionado y primero extrae la unidad con la que se trabaja y los títulos de los contenidos de vocabulario, gramática y funciones que están en el PDF. Luego debes generar el número de ejercicios solicitado (entre 1 y 10) por cada contenido que hay en el PDF. Por ejemplo, si hay un cuadro que se llama "Los números del 1 al 31" debes generar los ejercicios relacionados con los números del 1 al 31. Al comienzo de cada grupo de ejercicios, incluye una cabecera con el nombre de la unidad."""
    
    return system_prompt

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

# Función para identificar contenidos en el texto del PDF
def identify_contents(pdf_text):
    # Patrones para identificar contenidos
    unit_pattern = r'UNIDAD\s+(\d+)'
    vocabulary_pattern = r'(\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+)'
    grammar_pattern = r'(\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+)'
    
    # Intentar identificar la unidad
    unit_match = re.search(unit_pattern, pdf_text)
    unit_number = unit_match.group(1) if unit_match else "No identificada"
    
    # Buscar secciones de contenido
    vocab_sections = re.findall(vocabulary_pattern, pdf_text)
    grammar_sections = []
    
    # Filtrar secciones específicas de vocabulario y gramática
    for section in re.findall(r'\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+', pdf_text):
        if "LOS" in section or "LA" in section or "EL" in section:
            if section not in vocab_sections:
                vocab_sections.append(section)
        elif any(word in section for word in ["VERB", "DEFINITE", "INDEFINITE", "PRONOUN", "SUBJECT"]):
            grammar_sections.append(section)
    
    # Identificar secciones de funciones
    function_sections = []
    for section in re.findall(r'(\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+)', pdf_text):
        if "GREETINGS" in section or "INTRODUCTION" in section or "ASKING" in section or "GIVING" in section:
            function_sections.append(section)
    
    # Estructura de los contenidos identificados
    contents = {
        "unidad": f"Unidad {unit_number}",
        "vocabulario": vocab_sections,
        "gramatica": grammar_sections,
        "funciones": function_sections
    }
    
    return contents

# Función para llamar a la API de Anthropic (Claude) para analizar PDF y obtener contenidos
def analyze_pdf_content(pdf_text, api_key):
    if not api_key:
        return "Error: No se ha proporcionado una clave API válida."
    
    # Crear un prompt para extraer los contenidos del PDF
    analyze_prompt = f"""
    Por favor, analiza el siguiente contenido extraído de un PDF de español como lengua extranjera (ELE). 
    Necesito que identifiques:
    
    1. Número de la unidad
    2. Contenidos de vocabulario (con sus títulos exactos, como "Los números del 0 al 31")
    3. Contenidos de gramática (con sus títulos exactos, como "Definite and Indefinite Articles")
    4. Contenidos de funciones comunicativas (con sus títulos exactos, como "Greetings, Introductions, and Saying Good-bye")
    
    Devuelve los resultados en formato JSON con esta estructura:
    {{
        "unidad": "Unidad X",
        "contenidos": [
            {{
                "tipo": "vocabulario",
                "titulo": "Título del contenido"
            }},
            {{
                "tipo": "gramatica",
                "titulo": "Título del contenido"
            }},
            {{
                "tipo": "funcion",
                "titulo": "Título del contenido"
            }}
        ]
    }}
    
    Contenido del PDF:
    {pdf_text}
    """
    
    try:
        headers = {
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": "claude-4-sonnet-20250514",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": analyze_prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            content = response.json()["content"][0]["text"]
            # Extraer el JSON de la respuesta
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', content)
            if json_match:
                json_str = json_match.group(1) if json_match.group(1) else json_match.group(2)
                return json.loads(json_str)
            else:
                try:
                    return json.loads(content)
                except:
                    return {"error": "No se pudo extraer JSON de la respuesta"}
        else:
            return {"error": f"Error al llamar a la API: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Error al analizar el PDF: {str(e)}"}

# Función para llamar a la API de Anthropic (Claude) para generar ejercicios
def generate_exercises_for_content(content_title, content_type, pdf_text, num_exercises, unidad_nombre, api_key):
    if not api_key:
        return "Error: No se ha proporcionado una clave API válida."
    
    # Cargar el prompt base del sistema
    system_prompt = load_system_prompt()
    
    # Añadir instrucciones específicas sobre formato markdown
    formato_adicional = """
INSTRUCCIONES IMPORTANTES SOBRE FORMATO Y ESTRUCTURA: 

Cuando generes los ejercicios, DEBES seguir exactamente esta estructura para cada ejercicio, NO AÑADAS ninguna otra opción:

1. **Numeración del ejercicio**: Ejemplo: "Ejercicio 1" (en negrita)
2. **Objetivo didáctico**: Explica qué aprenderá el estudiante
3. **Recurso**: Incluye el texto, descripción de imagen o transcripción de audio
4. **Tipo de ejercicio**: Especifica qué tipología estás utilizando
5. **Enunciado**: Proporciona instrucciones claras para el estudiante (en negrita)
6. **Ejercicio**: El contenido del ejercicio según la tipología seleccionada
7. **Solución**: Las respuestas correctas claramente explicadas, SIN usar formato de lista

REGLAS DE FORMATO ADICIONALES:

- IMPORTANTE: Comienza la respuesta con un título que incluya el nombre de la unidad en formato "# Unidad X - Contenido específico"
- Las instrucciones y todos los encabezados de sección deben ir en negrita
- Para las opciones de selección múltiple usa "□" al inicio de cada línea
- Para las opciones de selección única usa "○" al inicio de cada línea
- CRÍTICO: Cada opción DEBE estar en su PROPIA LÍNEA
- Para preguntas numeradas, usa formato de lista numerada (1., 2., 3.)

EJEMPLO DE FORMATO PARA LAS OPCIONES:

```
1. Pregunta
○ opción 1
○ opción 2
○ opción 3

2. Pregunta
□ opción 1
□ opción 2
□ opción 3
```

EJEMPLO DE SOLUCIÓN (SIN FORMATO DE LISTA):

**Solución:** 
Pregunta 1: opción 2
Pregunta 2: opciones 1 y 3
Pregunta 3: opción 1

Este formato y estructura deben seguirse EXACTAMENTE.
"""
# Añadir instrucciones adicionales del usuario si existen
    if 'additional_instructions' in st.session_state and st.session_state.additional_instructions.strip():
        additional_prompt = f"\n\n## Instrucciones adicionales del usuario:\n{st.session_state.additional_instructions}\n"
        system_prompt = system_prompt + additional_prompt
    
    # Añadir instrucciones de formato al final
    system_prompt = system_prompt + formato_adicional
    
    # Crear un mensaje específico para el contenido seleccionado
    user_prompt = f"""
    Por favor, crea {num_exercises} ejercicios educativos de español como lengua extranjera (ELE) para nivel A1 
    basados en el contenido "{content_title}" que es de tipo {content_type}.
    
    Utiliza el PDF completo que te proporciono como contexto, pero céntrate específicamente
    en crear ejercicios sobre "{content_title}".
    
    La unidad con la que estamos trabajando es: "{unidad_nombre}". Asegúrate de incluirlo en el título de los ejercicios.
    
    Asegúrate de:
    1. Hacer ejercicios variados (usa distintas tipologías)
    2. Que sean adecuados al nivel A1
    3. Que incluyan siempre las soluciones
    4. Que estén basados específicamente en el contenido "{content_title}"
    5. Incluir el título de la unidad al principio de los ejercicios
    
    Contexto completo del PDF:
    {pdf_text}
    """
    
    try:
        headers = {
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": "claude-4-sonnet-20250514",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error al llamar a la API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error al generar ejercicios: {str(e)}"

# Función para guardar los ejercicios generados
def save_exercises(exercises):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.md', mode='w+') as tmp:
        tmp.write(exercises)
        return tmp.name

# Función para procesar el texto para ajustar el formato de opciones
def process_options_format(text):
    # Mejorar el espaciado en opciones
    text = re.sub(r'(\n[○□])', r'\n\n\1', text)
    return text

# Interfaz de usuario
st.sidebar.header("Configuración")

# Sección para cargar el PDF
uploaded_pdf = st.sidebar.file_uploader("Sube un PDF con el contenido", type="pdf", key="pdf_upload")

# Verificar si se ha cambiado el PDF
if uploaded_pdf is not None:
    # Calcular hash o nombre del PDF actual
    current_pdf_name = uploaded_pdf.name
    
    # Si es un nuevo PDF, limpiar los datos anteriores
    if st.session_state.current_pdf != current_pdf_name:
        st.session_state.current_pdf = current_pdf_name
        st.session_state.pdf_analyzed = False
        st.session_state.pdf_contents = None
        st.session_state.all_exercises = {}
        st.session_state.selected_content = None
        st.session_state.generating_exercises = False
        st.session_state.regenerate_exercise = False
        st.session_state.pdf_text = ""
        st.info(f"Se ha cargado un nuevo PDF: {current_pdf_name}. Se han limpiado los datos anteriores.")

# Botón para analizar el PDF e identificar contenidos
analyze_button = st.sidebar.button("Analizar PDF", type="primary")

# Clave API de Anthropic - Corregido para que funcione al primer intento
api_key = st.sidebar.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
if api_key and not st.session_state.api_key_set:
    os.environ["ANTHROPIC_API_KEY"] = api_key
    st.session_state.api_key_set = True
    st.success("Clave API guardada correctamente")

# Opciones para la configuración de ejercicios
with st.sidebar.expander("📋 Opciones de ejercicios", expanded=True):
    # Número de ejercicios por contenido
    num_exercises = st.slider("Número de ejercicios por contenido", 1, 10, 3, 
                              help="Número de ejercicios a generar para cada contenido identificado")
    
    # Guardar el número de ejercicios en el estado de la sesión
    if num_exercises != st.session_state.num_exercises:
        st.session_state.num_exercises = num_exercises
    
    # Selección de tipos de ejercicios
    st.subheader("Tipos de ejercicios preferidos")
    exercise_types = [
        "Arrastrar palabras",
        "Selección múltiple",
        "Selección única",
        "Textos con espacios para rellenar (texto libre)",
        "Textos con espacios para rellenar (menú desplegable)",
        "Textos con espacios para rellenar (verdadero/falso)",
        "Textos con espacios para rellenar (completar letras)",
        "Textos con espacios para rellenar (combinado)",
        "Emparejamiento",
        "Producción de texto",
        "Expresión oral",
        "Subir archivo",
        "Selección de imagen"
    ]
    selected_types = st.multiselect("Selecciona los tipos de ejercicios preferidos (opcional)", 
                                   exercise_types,
                                   help="Si seleccionas tipos específicos, el sistema intentará priorizar esos tipos al generar ejercicios")

# Opción para añadir instrucciones adicionales al prompt del sistema
with st.sidebar.expander("➕ Instrucciones adicionales para Claude", expanded=False):
    if 'additional_instructions' not in st.session_state:
        st.session_state.additional_instructions = ""
    
    st.write("Añade instrucciones adicionales para Claude sin modificar el prompt del sistema base:")
    additional_instructions = st.text_area(
        "Instrucciones adicionales",
        value=st.session_state.additional_instructions,
        height=200,
        placeholder="Ejemplo: 'Asegúrate de incluir ejercicios para practicar la pronunciación' o 'Enfócate en crear ejercicios para vocabulario de viajes'"
    )
    
    # Guardar cambios en las instrucciones adicionales
    if additional_instructions != st.session_state.additional_instructions:
        st.session_state.additional_instructions = additional_instructions
        st.success("Instrucciones adicionales actualizadas correctamente.")
    
    # Botón para limpiar las instrucciones adicionales
    if st.button("Limpiar instrucciones adicionales"):
        st.session_state.additional_instructions = ""
        st.success("Instrucciones adicionales eliminadas.")
        st.rerun()

# Sección de ayuda y documentación
with st.sidebar.expander("ℹ️ Acerca de los tipos de ejercicios"):
    st.markdown("""
    ### Tipos de ejercicios disponibles:
    
    1. **Arrastrar palabras**: Completar frases arrastrando palabras a espacios vacíos.
    2. **Selección múltiple**: Seleccionar VARIAS respuestas correctas de una lista.
    3. **Selección única**: Elegir UNA SOLA respuesta correcta entre varias opciones.
    4. **Textos con espacios para rellenar (texto libre)**: Completar textos escribiendo palabras específicas.
    5. **Textos con espacios para rellenar (menú desplegable)**: Completar textos seleccionando de un menú de opciones.
    6. **Textos con espacios para rellenar (verdadero/falso)**: Decidir si afirmaciones son verdaderas o falsas.
    7. **Textos con espacios para rellenar (completar letras)**: Completar palabras añadiendo las letras faltantes.
    8. **Textos con espacios para rellenar (combinado)**: Combinación de varios tipos de ejercicios en un texto.
    9. **Emparejamiento**: Relacionar elementos de dos columnas.
    10. **Producción de texto**: Escribir un texto libre como respuesta.
    11. **Expresión oral**: Para respuestas habladas.
    12. **Subir archivo**: Crear un documento como respuesta a una actividad.
    13. **Selección de imagen**: Elegir la imagen correcta entre varias opciones.
    """)

with st.sidebar.expander("❓ Instrucciones de uso"):
    st.markdown("""
    ### Cómo usar esta aplicación:
    
    1. **Sube un PDF** con el contenido del libro de texto o material didáctico.
    2. Haz clic en **Analizar PDF** para identificar la unidad y sus contenidos.
    3. Configura el **número de ejercicios** que deseas generar por cada contenido (entre 1 y 10).
    4. En la columna izquierda, selecciona un contenido específico para generar ejercicios.
    5. Alternativamente, usa el botón **Generar Ejercicios para TODOS los Contenidos** para crear ejercicios para toda la unidad.
    6. Descarga los ejercicios en formato Markdown (.md) usando los botones correspondientes.
    
    ### Recomendaciones:
    
    - Usa PDFs de buena calidad para mejorar la extracción del texto.
    - Para resultados óptimos, usa unidades completas del mismo libro de texto.
    - Si Claude no identifica correctamente algún contenido, puedes añadir instrucciones específicas en "Instrucciones adicionales para Claude".
    """)

# Añadir estilo CSS para alinear las cajas de información
st.markdown("""
<style>
    .stAlert {
        min-height: 80px;
        display: flex;
        align-items: center;
        padding: 10px 16px;
    }
</style>
""", unsafe_allow_html=True)

# Contenedor para mostrar contenido extraído y ejercicios generados
content_col, exercises_col = st.columns(2)

with content_col:
    st.header("Contenido del PDF")
    
    if uploaded_pdf is not None:
        # Guardar el PDF cargado en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_pdf.getvalue())
            tmp_pdf_path = tmp.name
        
        # Extraer y mostrar el contenido del PDF
        pdf_text = extract_text_from_pdf(tmp_pdf_path)
        st.session_state.pdf_text = pdf_text
        st.text_area("Texto extraído", pdf_text, height=400)
        os.unlink(tmp_pdf_path)  # Eliminar el archivo temporal
        
        # Analizar el PDF para identificar contenidos
        if analyze_button and api_key:
            with st.spinner("Analizando PDF para identificar contenidos..."):
                contents = analyze_pdf_content(pdf_text, api_key)
                if isinstance(contents, dict) and "error" not in contents:
                    st.session_state.pdf_contents = contents
                    st.session_state.pdf_analyzed = True
                    st.success(f"¡Análisis completado! Se ha identificado {contents['unidad']}")
                elif isinstance(contents, dict) and "error" in contents:
                    st.error(contents["error"])
                else:
                    st.error("Error al analizar el PDF")
    else:
        st.info("Sube un PDF para ver su contenido aquí.")
    
    # Mostrar contenidos identificados
    if st.session_state.pdf_analyzed and st.session_state.pdf_contents:
        st.subheader("Contenidos identificados")
        
        # Mostrar la unidad
        st.write(f"**{st.session_state.pdf_contents['unidad']}**")
        
        # Crear tabs para los diferentes tipos de contenido
        tabs = st.tabs(["Vocabulario", "Gramática", "Funciones"])
        
        with tabs[0]:
            if "contenidos" in st.session_state.pdf_contents:
                vocab_contents = [c for c in st.session_state.pdf_contents["contenidos"] if c["tipo"] == "vocabulario"]
                if vocab_contents:
                    for i, content in enumerate(vocab_contents):
                        # Añadir botón de regenerar junto al botón de contenido
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            if st.button(f"{content['titulo']}", key=f"vocab_{i}"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "vocabulario"
                                }
                                # Establecer regenerar a False para generar nuevos ejercicios solo si no existen
                                st.session_state.regenerate_exercise = False
                                if content["titulo"] not in st.session_state.all_exercises:
                                    st.session_state.generating_exercises = True
                                    st.rerun()
                        with col2:
                            if st.button("🔄", key=f"regen_vocab_{i}", help="Regenerar ejercicios"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "vocabulario"
                                }
                                # Establecer regenerar a True para forzar la regeneración
                                st.session_state.regenerate_exercise = True
                                st.session_state.generating_exercises = True
                                st.rerun()
                else:
                    st.write("No se han identificado contenidos de vocabulario.")
        
        with tabs[1]:
            if "contenidos" in st.session_state.pdf_contents:
                grammar_contents = [c for c in st.session_state.pdf_contents["contenidos"] if c["tipo"] == "gramatica"]
                if grammar_contents:
                    for i, content in enumerate(grammar_contents):
                        # Añadir botón de regenerar junto al botón de contenido
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            if st.button(f"{content['titulo']}", key=f"grammar_{i}"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "gramática"
                                }
                                # Establecer regenerar a False para generar nuevos ejercicios solo si no existen
                                st.session_state.regenerate_exercise = False
                                if content["titulo"] not in st.session_state.all_exercises:
                                    st.session_state.generating_exercises = True
                                    st.rerun()
                        with col2:
                            if st.button("🔄", key=f"regen_grammar_{i}", help="Regenerar ejercicios"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "gramática"
                                }
                                # Establecer regenerar a True para forzar la regeneración
                                st.session_state.regenerate_exercise = True
                                st.session_state.generating_exercises = True
                                st.rerun()
                else:
                    st.write("No se han identificado contenidos de gramática.")
        
        with tabs[2]:
            if "contenidos" in st.session_state.pdf_contents:
                function_contents = [c for c in st.session_state.pdf_contents["contenidos"] if c["tipo"] == "funcion"]
                if function_contents:
                    for i, content in enumerate(function_contents):
                        # Añadir botón de regenerar junto al botón de contenido
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            if st.button(f"{content['titulo']}", key=f"function_{i}"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "función comunicativa"
                                }
                                # Establecer regenerar a False para generar nuevos ejercicios solo si no existen
                                st.session_state.regenerate_exercise = False
                                if content["titulo"] not in st.session_state.all_exercises:
                                    st.session_state.generating_exercises = True
                                    st.rerun()
                        with col2:
                            if st.button("🔄", key=f"regen_function_{i}", help="Regenerar ejercicios"):
                                st.session_state.selected_content = {
                                    "titulo": content["titulo"],
                                    "tipo": "función comunicativa"
                                }
                                # Establecer regenerar a True para forzar la regeneración
                                st.session_state.regenerate_exercise = True
                                st.session_state.generating_exercises = True
                                st.rerun()
                else:
                    st.write("No se han identificado contenidos de funciones comunicativas.")

with exercises_col:
    st.header("Ejercicios Generados")
    
    # Definición de estilos CSS para formatear los ejercicios
    st.markdown("""
    <style>
    .ejercicios-container {
        font-size: 0.9rem;
        line-height: 1.2;
    }
    
    .ejercicios-container h1, 
    .ejercicios-container h2, 
    .ejercicios-container h3 {
        font-size: 1.2rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    .ejercicios-container p {
        margin: 0.4rem 0;
    }
    
    .ejercicios-container ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .ejercicios-container ol li {
        margin-bottom: 0.3rem;
    }
    
    .ejercicios-container ul {
        margin: 0.3rem 0;
        padding-left: 1.2rem;
    }
    
    .ejercicios-container hr {
        margin: 1rem 0;
        border-color: rgba(200, 200, 200, 0.2);
    }
    
    .ejercicios-container pre {
        margin: 0.5rem 0;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 0.5rem;
        border-radius: 4px;
    }
    
    /* Estilo específico para opciones en línea */
    .ejercicios-container p:has(> □), 
    .ejercicios-container p:has(> ○) {
        display: block;
        margin: 0.3rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Estilos CSS para ajustar el interlineado de las listas
    st.markdown("""
    <style>
    .reduced-spacing li {
        margin-bottom: 0;
        line-height: 1.3;
    }
    .reduced-spacing li p {
        margin-bottom: 0.2rem;
    }
    .reduced-spacing ul, .reduced-spacing ol {
        margin: 0.2rem 0;
        padding-left: 1.5rem;
    }
    .reduced-spacing h1, .reduced-spacing h2, .reduced-spacing h3 {
        margin-top: 1rem;
        margin-bottom: 0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Función para convertir los ejercicios al formato markdown de Streamlit
    def convert_to_streamlit_markdown(text):
        # Reemplazar símbolos de selección múltiple con viñetas Markdown
        text = re.sub(r'□\s*', '- [ ] ', text)
        
        # Reemplazar símbolos de selección única con asteriscos Markdown
        text = re.sub(r'○\s*', '* ', text)
        
        # Reemplazar negrita
        text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)
        
        return text
    
    # Generar ejercicios para el contenido seleccionado
    if st.session_state.generating_exercises and st.session_state.selected_content and api_key:
        # Si regenerate_exercise es True o el contenido no existe, generamos nuevos ejercicios
        if st.session_state.regenerate_exercise or st.session_state.selected_content['titulo'] not in st.session_state.all_exercises:
            with st.spinner(f"Generando {st.session_state.num_exercises} ejercicios para '{st.session_state.selected_content['titulo']}'... Esto puede tardar unos momentos."):
                exercises = generate_exercises_for_content(
                    st.session_state.selected_content['titulo'],
                    st.session_state.selected_content['tipo'],
                    st.session_state.pdf_text,
                    st.session_state.num_exercises,
                    st.session_state.pdf_contents['unidad'],
                    api_key
                )
                
                # Guardar los ejercicios generados en el estado de la sesión
                if not exercises.startswith("Error"):
                    st.session_state.all_exercises[st.session_state.selected_content['titulo']] = exercises
                    st.session_state.generating_exercises = False
                    st.session_state.regenerate_exercise = False
                else:
                    st.error(exercises)
                    st.session_state.generating_exercises = False
                    st.session_state.regenerate_exercise = False
        else:
            # Si no necesitamos regenerar, solo actualizamos el estado
            st.session_state.generating_exercises = False
            
    # Mostrar los ejercicios generados para el contenido seleccionado
    if st.session_state.selected_content and st.session_state.selected_content['titulo'] in st.session_state.all_exercises:
        st.subheader(f"Ejercicios para: {st.session_state.selected_content['titulo']}")
        
        exercises = st.session_state.all_exercises[st.session_state.selected_content['titulo']]
        streamlit_markdown = convert_to_streamlit_markdown(exercises)
        
        # Mostrar los ejercicios
        st.markdown(f'<div class="reduced-spacing">{streamlit_markdown}</div>', unsafe_allow_html=True)
        
        # Añadir botón para descargar los ejercicios
        exercises_file = save_exercises(exercises)
        with open(exercises_file, "r") as file:
            st.download_button(
                label=f"Descargar Ejercicios ({st.session_state.selected_content['titulo']})",
                data=file,
                file_name=f"ejercicios_{st.session_state.selected_content['titulo'].replace(' ', '_')}.md",
                mime="text/markdown"
            )
        os.unlink(exercises_file)  # Eliminar el archivo temporal
    
    # Botón para generar TODOS los ejercicios a la vez
    if st.session_state.pdf_analyzed and st.session_state.pdf_contents:
        if 'generating_all' not in st.session_state:
            st.session_state.generating_all = False
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("Generar Ejercicios para TODOS los Contenidos", type="primary"):
                st.session_state.generating_all = True
                # No regeneramos por defecto
                st.session_state.regenerate_exercise = False
                
        with col2:
            if st.button("🔄", help="Regenerar TODOS los ejercicios"):
                st.session_state.generating_all = True
                # Forzamos regeneración
                st.session_state.regenerate_exercise = True
            
        # Procesar la generación de todos los ejercicios
        if st.session_state.generating_all and api_key:
            all_contents = []
            if "contenidos" in st.session_state.pdf_contents:
                all_contents = st.session_state.pdf_contents["contenidos"]
            
            # Mostrar progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, content in enumerate(all_contents):
                # Saltar si ya tenemos ejercicios para este contenido y no estamos regenerando
                if content["titulo"] in st.session_state.all_exercises and not st.session_state.regenerate_exercise:
                    progress_value = (i + 1) / len(all_contents)
                    progress_bar.progress(progress_value)
                    status_text.text(f"Procesando {i+1}/{len(all_contents)}: {content['titulo']} (ya generado)")
                    continue
                    
                status_text.text(f"Procesando {i+1}/{len(all_contents)}: {content['titulo']}")
                
                exercises = generate_exercises_for_content(
                    content["titulo"],
                    content["tipo"],
                    st.session_state.pdf_text,
                    st.session_state.num_exercises,
                    st.session_state.pdf_contents['unidad'],
                    api_key
                )
                
                if not exercises.startswith("Error"):
                    st.session_state.all_exercises[content["titulo"]] = exercises
                
                # Actualizar la barra de progreso
                progress_value = (i + 1) / len(all_contents)
                progress_bar.progress(progress_value)
            
            # Completado
            status_text.text(f"¡Todos los ejercicios han sido generados! ({st.session_state.num_exercises} ejercicios por cada contenido)")
            st.session_state.generating_all = False
            st.session_state.regenerate_exercise = False
            
            # Opción para descargar todos los ejercicios
            all_exercises_text = f"# {st.session_state.pdf_contents['unidad']} - Todos los Ejercicios\n\n"
            for title, exercises in st.session_state.all_exercises.items():
                all_exercises_text += exercises
                all_exercises_text += "\n\n---\n\n"
            
            all_exercises_file = save_exercises(all_exercises_text)
            with open(all_exercises_file, "r") as file:
                st.download_button(
                    label="Descargar TODOS los Ejercicios",
                    data=file,
                    file_name=f"todos_los_ejercicios_{st.session_state.pdf_contents['unidad'].replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            os.unlink(all_exercises_file)
    
    # Mensaje informativo cuando no hay ejercicios
    if not st.session_state.pdf_analyzed:
        st.info("Primero analiza el PDF para identificar los contenidos y luego genera los ejercicios.")
    elif not st.session_state.selected_content and not st.session_state.all_exercises:
        st.info("Selecciona un contenido de la columna izquierda para generar ejercicios específicos o usa el botón 'Generar Ejercicios para TODOS los Contenidos'.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Desarrollado con ❤️ para profesores de ELE | Powered by Claude 3.7 Sonnet</div>", unsafe_allow_html=True)
