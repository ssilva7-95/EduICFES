import pymongo
import os
import bcrypt
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("EduICFES")
users_collection = db.get_collection("users")
chats_collection = db.get_collection("chats")

def add_user(name, email, password):
    """Hashea la contraseña y agrega un nuevo usuario a la base de datos."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return False

def get_user(email):
    """Busca y devuelve un usuario por su email."""
    return users_collection.find_one({"email": email})

def check_password(stored_password_hash, provided_password):
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash)

def create_email_index():
    """Asegura que el índice único para el email exista."""
    users_collection.create_index("email", unique=True)

def create_chat(user_email, title="Nuevo chat"):
    """Crea un nuevo chat para un usuario."""
    chat = {
        "user_email": user_email,
        "title": title,
        "history": [],
        "timestamp": datetime.utcnow()
    }
    result = chats_collection.insert_one(chat)
    return result.inserted_id

def get_chats_for_user(user_email):
    """Obtiene todos los chats de un usuario."""
    return list(chats_collection.find({"user_email": user_email}).sort("timestamp", pymongo.DESCENDING))

def get_chat(chat_id):
    """Obtiene un chat por su ID."""
    return chats_collection.find_one({"_id": ObjectId(chat_id)})

def add_message_to_chat(chat_id, message):
    """Agrega un mensaje al historial de un chat."""
    chats_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$push": {"history": message}}
    )

def update_chat_title(chat_id, title):
    """Actualiza el título de un chat."""
    chats_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": {"title": title}}
    )

def delete_chat(chat_id):
    """Elimina un chat de la base de datos."""
    chats_collection.delete_one({"_id": ObjectId(chat_id)})
