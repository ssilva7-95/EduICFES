from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from markupsafe import Markup
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from os import getenv
from dotenv import load_dotenv
import markdown
from database import (
    add_user, get_user, check_password, create_email_index,
    create_chat, get_chats_for_user, get_chat, add_message_to_chat, update_chat_title, delete_chat
)

app = Flask(__name__)
app.secret_key = getenv("FLASK_SECRET_KEY", "una-clave-secreta-muy-segura")

@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text))

try:
    with app.app_context():
        create_email_index()
except Exception as e:
    print("\n\n!!! ERROR DE CONEXIÓN A MONGODB !!!")
    print("No se pudo conectar a la base de datos. Asegúrate de que MONGO_URI está bien configurada en tu archivo .env")
    print(f"Detalles del error: {e}")
    print("La aplicación se ejecutará, pero no funcionará correctamente hasta que se solucione la conexión.\n\n")

load_dotenv()
API_KEY = getenv("API_KEY")
genai.configure(api_key=API_KEY)

MODELO = 'gemini-2.5-flash'
config = GenerationConfig()
model = genai.GenerativeModel(
    model_name=MODELO,
    system_instruction="""
    Eres un bot profesional, amable y convincente.
    Tienes conocimientos en orientación vocacional, preparación académica (como pruebas Saber ICFES), técnicas de estudio y también en prácticas de mindfulness para el manejo del estrés.
    Tu objetivo es ayudar a los estudiantes a descubrir su camino educativo y apoyarlos emocionalmente cuando lo necesiten.

    Cuando un usuario exprese sentirse mal, estresado o abrumado, tu prioridad es ofrecerle apoyo. Responde con empatía y ofrécele un ejercicio de mindfulness o respiración. No ignores sus sentimientos.

    Tu estilo de respuesta debe ser claro y organizado. Usa Markdown para formatear tus respuestas, utilizando encabezados, listas, negritas y líneas horizontales (`---`) para separar secciones claramente y que la información sea fácil de leer.
    
    No te limites mucho en las respuestas pero intente usar la menor cantidad de tokens posibles
    """
)

def generate_chat_title(first_message):
    try:
        title_prompt = f"Resume la siguiente pregunta en máximo 4 palabras para usar como título de un chat: '{first_message}'"
        response = model.generate_content(title_prompt)
        return response.text.strip().replace('"', '')
    except Exception as e:
        print(f"Error al generar el título del chat: {e}")
        return "Nuevo chat"

@app.route("/")
def index():
    if "user_email" in session:
        return redirect(url_for("chat_page"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if get_user(email):
            return render_template("register.html", error="El correo ya está registrado.")

        add_user(name, email, password)
        session["user_email"] = email
        return redirect(url_for("chat_page"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user(email)
        if user and check_password(user["password"], password):
            session["user_email"] = email
            return redirect(url_for("chat_page"))

        return render_template("login.html", error="Correo o contraseña incorrectos.")

    return render_template("login.html")

@app.route("/chat")
def chat_page():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    user_chats = get_chats_for_user(session["user_email"])
    if not user_chats:
        chat_id = create_chat(session["user_email"])
        return redirect(url_for("chat_view", chat_id=chat_id))
    
    return redirect(url_for("chat_view", chat_id=user_chats[0]["_id"]))

@app.route("/chat/new")
def new_chat():
    if "user_email" not in session:
        return redirect(url_for("login"))

    chat_id = create_chat(session["user_email"])
    return redirect(url_for("chat_view", chat_id=chat_id))

@app.route("/chat/<chat_id>")
def chat_view(chat_id):
    if "user_email" not in session:
        return redirect(url_for("login"))

    chat = get_chat(chat_id)
    if not chat or chat["user_email"] != session["user_email"]:
        return "Chat no encontrado o no autorizado", 404

    user = get_user(session["user_email"])
    user_name = user.get("name", "Usuario") if user else "Usuario"

    return render_template("chat.html", user=user_name, chat=chat)

@app.route("/api/chats", methods=["GET"])
def get_user_chats():
    if "user_email" not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    chats = get_chats_for_user(session["user_email"])
    for chat in chats:
        chat["_id"] = str(chat["_id"]) # Convertir ObjectId a string

    return jsonify(chats)

@app.route("/send_message", methods=["POST"])
def send_message():
    if "user_email" not in session:
        return jsonify({"error": "No autorizado"}), 401

    chat_id = request.json.get("chat_id")
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"response": "No entendí tu mensaje 😅"})

    chat_data = get_chat(chat_id)
    if not chat_data or chat_data["user_email"] != session["user_email"]:
        return jsonify({"error": "Chat no encontrado o no autorizado"}), 404

    # Reconstruir el historial para el modelo
    history = []
    for message in chat_data["history"]:
        history.append({"role": message["role"], "parts": [{"text": message["content"]}]})

    chat_session = model.start_chat(history=history)

    try:
        response = chat_session.send_message(user_message)
        
        # Guardar mensajes en la base de datos
        add_message_to_chat(chat_id, {"role": "user", "content": user_message})
        add_message_to_chat(chat_id, {"role": "model", "content": response.text})

        json_response = {"response": response.text}

        # Generar título si es el primer mensaje
        if len(chat_data["history"]) == 0:
            title = generate_chat_title(user_message)
            update_chat_title(chat_id, title)
            json_response["new_title"] = title

        return jsonify(json_response)
    except Exception as e:
        return jsonify({"response": f"Ocurrió un error: {str(e)}"})

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("login"))

@app.route("/chat/delete/<chat_id>", methods=["POST"])
def delete_chat_route(chat_id):
    if "user_email" not in session:
        return jsonify({"error": "No autorizado"}), 401

    chat = get_chat(chat_id)
    if not chat or chat["user_email"] != session["user_email"]:
        return jsonify({"error": "Chat no encontrado o no autorizado"}), 404

    delete_chat(chat_id)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)