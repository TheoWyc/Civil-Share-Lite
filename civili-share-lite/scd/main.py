from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import hashlib
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware  # ← Ajouter cette ligne
from sqlalchemy.orm import Session
from database import Base, engine
import models
from database import engine, get_db
# from main2 import *

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialiser la base SQLite
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            admin_status BOOLEAN DEFAULT FALSE,
            password_set BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Ajouter un utilisateur admin
    add_user('admin', '123', cursor, True)
    
    # Ajoute quelque utilisateur
    users= ["lucas", "gabin", "theo", "yoan"]
    password="321"
    for user in users:
        add_user(user, password, cursor) # is_admin=False par defaut
    
    # Ajouter un utilisateur sans mot de passe configuré
    add_new_user("erwann", cursor)
    add_new_user("nicoals", cursor)


    conn.commit()
    conn.close()

# Fonction pour vérifier les credentials et récupérer les infos user
def verify_user(username: str, password: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT id, username, admin_status FROM users WHERE username = ? AND password = ? AND password_set = 1', 
                    (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user

# Ajouter un nouvel utilisateur sans mdp configuré
def add_new_user(username: str, cursor: sqlite3.Cursor):
    cursor.execute('INSERT OR IGNORE INTO users (username, password, password_set) VALUES (?, ?, ?)', 
                    (username, 'UNSET_PASSWORD', 0))

# Ajouter un utilisateur
def add_user(username: str, password: str, cursor: sqlite3.Cursor, is_admin: bool=False):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('INSERT OR IGNORE INTO users (username, password, admin_status) VALUES (?, ?, ?)', 
                    (username, hashed, is_admin)) # par default le password_set est true

# Reset le mdp d'un utilisateur
def reset_password(username: str, cursor: sqlite3.Cursor):
    # cursor.execute('UPDATE users (username, password, password_set) VALUES (?, ?, ?)', 
    cursor.execute('UPDATE users SET password = ?, password_set = 0 WHERE username = ?', 
                    ('UNSET_PASSWORD', username))

# Mettre à jour le mot de passe
def change_password(username: str, password: str, cursor: sqlite3.Cursor):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('UPDATE users SET password = ?, password_set = 1 WHERE username = ?', 
                    (hashed, username))


# Page de login (GET)
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Traitement du login (POST)
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = verify_user(username, password)
    if user:
        user_id, username, is_admin = user
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"✅ Bienvenue {username} !",
            "success": True,
            "is_admin": bool(is_admin), 
            "username": username
        })
    else:
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Utilisateur ou mot de passe incorrect",
            "success": False,
            "is_admin": False
        })


# Page de premiere connexion au compte (GET)
@app.get("/first_login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("first_login.html", {"request": request})

# Configuration du mot de passe (POST)
@app.post("/setup-password")
async def setup_password(request: Request,
                        username: str = Form(...),
                        password: str = Form(...),
                        confirm_password: str = Form(...)):
    
    # Vérifier que les mots de passe correspondent
    if password != confirm_password:
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Les mots de passe ne correspondent pas",
            "success": False
        })
    
    # Vérifier que les mots de passe ne sont pas vides
    if not password or not confirm_password:
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Les mots de passe ne peuvent pas être vides",
            "success": False
        })
    
    # Vérifier que l'utilisateur existe et n'a pas encore défini son mot de passe
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_set = 0', (username,))
    user = cursor.fetchone()
    
    if not user: # aucun résultat
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Utilisateur inexistant ou mot de passe déjà configuré",
            "success": False
        })
    
    # Mettre à jour le mot de passe
    change_password(username, password, cursor)

    conn.commit()
    conn.close()
    
    return templates.TemplateResponse("result.html", {
        "request": request, 
        "message": f"🎉 Félicitations {username} ! Votre mot de passe a été configuré avec succès.",
        "success": True
    })

# Page du panneau administrateur (GET)
@app.get("/admin_panel", response_class=HTMLResponse)
async def login_page(request: Request):
    # Récupère tous les utilisateurs
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_set, admin_status FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users})

# Reset password d'un utilisateur (POST)
@app.post("/admin-reset-password")
async def admin_reset_password(request: Request, 
                            target_user: str = Form(...), 
                            admin_username: str = Form(...),
                            admin_password: str = Form(...)):
    
    # Vérifier que l'admin qui fait l'action existe et a le bon mot de passe
    admin_user = verify_user(admin_username, admin_password)  # AXE D'AMELIORATION
    
    if not admin_user:
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Mot de passe admin incorrect",
            "success": False
        })
    
    # Reset du mot de passe de l'utilisateur cible
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vérifier que l'utilisateur cible existe
    cursor.execute('SELECT id FROM users WHERE username = ?', (target_user,))
    if not cursor.fetchone():
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"❌ Utilisateur '{target_user}' non trouvé",
            "success": False
        })
    
    # Reset: remettre password à UNSET_PASSWORD et password_set à 0
    cursor.execute('UPDATE users SET password = ?, password_set = 0 WHERE username = ?', 
                    ('UNSET_PASSWORD', target_user,))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/admin_panel", status_code=303)

# Promouvoir un utilisateur en admin (POST)
@app.post("/admin-promote-user")
async def admin_promote_user(request: Request, 
                            target_user: str = Form(...), 
                            admin_username: str = Form(...),
                            admin_password: str = Form(...)):
    
    # Vérifier que l'admin qui fait l'action existe et a le bon mot de passe
    admin_user = verify_user(admin_username, admin_password)
    
    if not admin_user:
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Mot de passe admin incorrect",
            "success": False
        })
    
    # Promouvoir l'utilisateur en admin
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vérifier que l'utilisateur cible existe
    cursor.execute('SELECT id, admin_status FROM users WHERE username = ?', (target_user,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"❌ Utilisateur '{target_user}' non trouvé",
            "success": False
        })
    
    if user[1]:  # Déjà admin
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"⚠️ '{target_user}' est déjà administrateur",
            "success": False
        })
    
    # Promouvoir en admin
    cursor.execute('UPDATE users SET admin_status = 1 WHERE username = ?', (target_user,))
    conn.commit()
    conn.close()
    
    # Rediriger vers le panneau admin au lieu d'afficher result.html
    return RedirectResponse(url="/admin_panel", status_code=303)

# Ajouter un nouvel utilisateur (POST)
@app.post("/admin-add-user")
async def admin_add_user(request: Request, new_username: str = Form(...)):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vérifier si l'utilisateur existe déjà
    cursor.execute('SELECT id FROM users WHERE username = ?', (new_username,))
    if cursor.fetchone():
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"❌ L'utilisateur '{new_username}' existe déjà",
            "success": False
        })
    
    # Ajouter le nouvel utilisateur avec password non configuré
    add_new_user(new_username, cursor)

    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/admin_panel", status_code=303)

# Supprimer un utilisateur (POST)
@app.post("/admin-delete-user")
async def admin_delete_user(request: Request, 
                            target_user: str = Form(...), 
                            admin_username: str = Form(...),
                            admin_password: str = Form(...)):
    
    # Vérifier que l'admin qui fait l'action existe et a le bon mot de passe
    admin_user = verify_user(admin_username, admin_password)
    
    if not admin_user or not admin_user[2]:  # Pas admin ou pas trouvé
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Identifiants admin incorrects ou pas d'autorisation admin",
            "success": False
        })
    
    # Vérifier que l'utilisateur cible existe
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, admin_status FROM users WHERE username = ?', (target_user,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": f"❌ Utilisateur '{target_user}' non trouvé",
            "success": False
        })
    
    # Empêcher la suppression de son propre compte
    if target_user == admin_username:
        conn.close()
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "message": "❌ Vous ne pouvez pas supprimer votre propre compte",
            "success": False
        })
    
    # Supprimer l'utilisateur
    cursor.execute('DELETE FROM users WHERE username = ?', (target_user,))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/admin_panel", status_code=303)

# Initialiser la DB au démarrage
@app.on_event("startup")
async def startup_event():
    init_db()




# -------- notes ----------

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_next_filename(original_name):
    # ex: fichier01.png, fichier02.png
    existing = [f for f in os.listdir(UPLOAD_DIR) if f.startswith("fichier")]
    next_index = len(existing) + 1
    ext = os.path.splitext(original_name)[1]  # .png, .mp4, etc
    return f"fichier{next_index:02d}{ext}"


# ← Ajouter ce bloc CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Page de notes
@app.get("/notes", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("notes.html", {"request": request})
# return RedirectResponse(url="/notes.html", status_code=303)

@app.get("/api/notes")
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(models.Notes).all()
    return {"notes": notes}

@app.post("/api/notes")
def create_note(note_data: dict, db: Session = Depends(get_db)):
    note = models.Notes(**note_data)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.delete("/reset-db/")
def reset_db():
    Base.metadata.drop_all(bind=engine)   # Supprime toutes les tables
    Base.metadata.create_all(bind=engine) # Les recrée vides
    return {"message": "Base de données réinitialisée ✅"}

@app.delete("/api/notes/reset/{save_name}")
def delete_notes_by_save(save_name: str, db: Session = Depends(get_db)):
    db.query(models.Notes).filter(models.Notes.save_name == save_name).delete()
    db.commit()
    return {"message": f"Notes de la sauvegarde '{save_name}' supprimées"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = get_next_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_url": f"/{UPLOAD_DIR}/{filename}"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)