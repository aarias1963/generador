# Generador de Ejercicios de Español como Lengua Extranjera (ELE)

Esta aplicación Streamlit te permite generar ejercicios educativos para estudiantes de español como lengua extranjera (ELE) de nivel A1 a partir de cualquier contenido en formato PDF.

## Características

- **Procesamiento de PDF**: Sube cualquier PDF con contenido educativo.
- **Generación inteligente**: Utiliza Claude 3.7 Sonnet para crear ejercicios personalizados.
- **Diversas tipologías**: Selecciona entre 10 tipos diferentes de ejercicios.
- **Soluciones incluidas**: Todos los ejercicios vienen con sus soluciones.
- **Descarga de resultados**: Exporta los ejercicios generados en formato Markdown.

## Requisitos

```
streamlit==1.27.0
anthropic==0.7.0
PyPDF2==3.0.1
python-dotenv==1.0.0
```

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/tuusuario/generador-ejercicios-ele.git
cd generador-ejercicios-ele
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto con tu clave API de Anthropic:
```
ANTHROPIC_API_KEY=tu_clave_api_aquí
```

## Uso

1. Ejecuta la aplicación:
```bash
streamlit run app.py
```

2. Sube un PDF con el contenido del que quieres generar ejercicios.
3. Configura las opciones:
   - Número de ejercicios a generar
   - Tipos de ejercicios (opcional)
   - Tu clave API de Anthropic (si no está en el archivo .env)
4. Haz clic en "Generar Ejercicios".
5. Revisa los ejercicios generados y descárgalos si lo deseas.

## Tipos de ejercicios disponibles

1. **Arrastrar palabras**: Completar frases arrastrando palabras a espacios vacíos.
2. **Selección múltiple**: Seleccionar VARIAS respuestas correctas de una lista.
3. **Selección única**: Elegir UNA SOLA respuesta correcta entre varias opciones.
4. **Textos con espacios para rellenar**: Completar textos con diferentes tipos de respuestas.
5. **Emparejamiento**: Relacionar elementos de dos columnas.
6. **Producción de texto**: Escribir un texto libre como respuesta.
7. **Expresión oral**: Para respuestas habladas.
8. **Subir archivo**: Crear un documento como respuesta a una actividad.
9. **Selección de imagen**: Elegir la imagen correcta entre varias opciones.
10. **Multipregunta**: Agrupar varias preguntas en un bloque temático.

## Notas

- Todos los ejercicios generados son de nivel A1 según el Marco Común Europeo de Referencia para las Lenguas.
- El contenido extraído del PDF se muestra para que puedas revisarlo antes de generar los ejercicios.
- La generación puede tardar unos momentos dependiendo del tamaño del contenido y el número de ejercicios solicitados.
