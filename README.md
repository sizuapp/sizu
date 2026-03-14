# SIZU - Plataforma de Aprendizaje con IA

SIZU es un tutor académico inteligente diseñado para estudiantes de secundaria. Utiliza la API de Google Gemini para ofrecer tutorías personalizadas, generación de quices a partir de archivos PDF y evaluación semántica de respuestas.

## ✨ Características

- **Tutor SIZU:** Chatbot especializado en temas académicos con restricciones de contexto.
- **Generador de Quices:** Carga un PDF y obtén automáticamente preguntas de opción múltiple, completación y desarrollo.
- **Evaluación Semántica:** La IA califica respuestas abiertas comparando el significado, no solo palabras clave.

## 🚀 Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/sizuapp/sizu.git
   cd SIZU
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   - Copia el archivo `.env.example` a `.env`.
   - Agrega tu `GEMINI_API_KEY`.

5. **Ejecutar migraciones y servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 🛠️ Tecnologías
- Django
- Google Generative AI SDK
- Tailwind CSS