# EduICFES - Chatbot Orientador Motivacional 

Este proyecto es un **chatbot con Inteligencia Artificial** desarrollado en **Python 3.12**, pensado para orientar a estudiantes en su camino educativo, ayudarlos a practicar para las pruebas **Saber ICFES**, brindar orientación vocacional y enseñar técnicas de relajación y mindfulness.

---

##  Características principales

- Orientación vocacional y preparación académica.
- Preguntas y ejercicios estilo **Saber ICFES**.
- Técnicas de relajación y mindfulness frente al estrés.
- Sistema de retos y logros simbólicos para mantener la motivación.
- Respuestas cálidas y motivadoras.

---

##  Requisitos

- **Python 3.12**
- Librerías necesarias:

```bash
google-generativeai
python-dotenv
```

---

##  Instalación
1. Crea y activa un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate   # En Linux/Mac
venv\Scripts\activate      # En Windows
```

2. Instala las dependencias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

En caso de que no esté incluido, instala también **google-generativeai**:

```bash
pip install google-generativeai
```

En caso de que no este incluido, instala **pymongo**:
```bash
pip install pymongo
```

En caso de que no este incluido, instala **bcrypt**:
```bash
pip install bcrypt
```

En caso de que no este incluido, instala **flask**:
```bash
pip install flask
```

En caso de que no este incluido, instala **markdown**:
```bash
pip install markdown
```

En caso de que no este incluido, instala **markupsafe**:
```bash
pip install markupsafe
```
---

##  Configuración de la API Key

1. Crea un archivo **.env** en la raíz del proyecto con el siguiente contenido:

```env
API_KEY=tu_api_key_aqui
```

2. Obtén tu API Key desde [Google AI Studio](https://ai.google.dev/).

---

##  Uso
El bot iniciará con un mensaje de bienvenida. Puedes interactuar escribiendo tus preguntas o dudas.
Para finalizar la conversación, escribe:

```
terminar
```

---

##  Estructura del proyecto

```
EduICFES/
│── main.py             # Código principal del chatbot
│── README.md           # Documentación del proyecto
│── .env                # API Key (NO subir a GitHub)
│── requirements.txt    # Dependencias necesarias
│── venv/               # Entorno virtual (ignorar en GitHub)
```

---

##  Notas

- El modelo utilizado es: **gemini-2.5-flash-lite**.
- Si ocurre un error, revisa tu **.env** y tu conexión a internet.

---

##  Futuras mejoras

- Guardar historial de estudiantes con un sistema de memoria.
- Interfaz gráfica o integración con aplicaciones móviles/web.
- Ampliar el sistema de logros y retroalimentación personalizada.

---