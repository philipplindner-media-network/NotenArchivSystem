from flask import Flask, render_template, request, redirect, session, flash, send_from_directory, url_for
import mysql.connector
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import barcode
from barcode.writer import ImageWriter
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from flask import send_file
from datetime import datetime
import traceback
import smtplib
from email.mime.text import MIMEText
import re
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from dotenv import load_dotenv
from functools import wraps
import shutil

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or 'NOTAS'
app.config.update(
    MAIL_SERVER='xxx',
    MAIL_PORT=465,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='xxx',
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    MAIL_DEFAULT_SENDER='xxx'
)

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_discord(discord):
    return re.match(r"^.{2,32}#[0-9]{4}$", discord)

with open("config.json") as f:
    db_config = json.load(f)

def get_db_connection():
    return mysql.connector.connect(**db_config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("rolle") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        benutzername = request.form["benutzername"]
        passwort = request.form["passwort"]
        email = request.form["email"]
        discord = request.form["discord"]

        if not is_valid_email(email):
            return "Ungültige E-Mail-Adresse!"
        if discord and not is_valid_discord(discord):
            return "Ungültiger Discord-Name (z. B. Nutzer#1234)"

        hashed_pw = generate_password_hash(passwort)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM benutzer WHERE email = %s", (email,))
        if cur.fetchone():
            return "Diese E-Mail ist bereits registriert!"

        rolle = "user"
        cur.execute(
            "INSERT INTO benutzer (benutzername, passwort_hash, email, discord, rolle) VALUES (%s, %s, %s, %s, %s)",
            (benutzername, hashed_pw, email, discord, rolle))
        conn.commit()
        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True)

        msg = Message("Noten Archiv – E-Mail bestätigen", recipients=[email])
        msg.body = f"Klicke auf den Link, um deine E-Mail zu bestätigen: {link}"
        mail.send(msg)

        cur.close()
        conn.close()
        return "Registrierung erfolgreich! Bitte bestätige deine E-Mail über den Link, den wir dir geschickt haben."
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nutzername = request.form["nutzername"]
        passwort = request.form["passwort"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("SELECT id, passwort_hash, rolle FROM benutzer WHERE nutzername=%s", (nutzername,))
            user = cur.fetchone()
            if user and check_password_hash(user[1], passwort):
                session["user_id"] = user[0]
                session["rolle"] = user[2]
                flash("Login erfolgreich.", "success")
                return redirect("/")
            else:
                flash("Login fehlgeschlagen. Bitte überprüfe Benutzername und Passwort.", "danger")
        except Exception as e:
            print(f"[Login Error] {e}")
            flash("Ein interner Fehler ist aufgetreten. Bitte versuche es später erneut.", "danger")
        finally:
            cur.close()
            conn.close()
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Abgemeldet.", "info")
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        titel = request.form["titel"]
        ordner = request.form.get("ordner") or request.form.get("ordner_neu") or ""
        file = request.files.get("file")
        filename = ""
        zufalls_id = str(uuid.uuid4())[:8]

        if file and file.filename.endswith(".pdf"):
            filename = f"{zufalls_id}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # QR-Code
            qr = qrcode.make(zufalls_id)
            qr.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{zufalls_id}_qr.png"))

            # Barcode
            ean = barcode.get("code128", zufalls_id, writer=ImageWriter())
            ean.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{zufalls_id}_barcode"))
        else:
            # Wenn keine PDF hochgeladen: Kopiere Blanko-PDF oder lasse filename leer
            blanko_path = os.path.join(app.config['UPLOAD_FOLDER'], "blanko.pdf")
            if os.path.exists(blanko_path):
                filename = f"{zufalls_id}_blanko.pdf"
                shutil.copy(blanko_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = ""

        cur.execute(
            "INSERT INTO noten (titel, ordner, dateiname, code, benutzer_id) VALUES (%s, %s, %s, %s, %s)",
            (titel, ordner, filename, zufalls_id, session["user_id"]))
        conn.commit()

    cur.execute("SELECT DISTINCT ordner FROM noten WHERE ordner != ''")
    ordner_liste = [row["ordner"] for row in cur.fetchall()]

    cur.execute("SELECT id, titel, ordner, code, dateiname FROM noten WHERE benutzer_id = %s ORDER BY titel",
                (session["user_id"],))
    noten = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", noten=noten, ordner_liste=ordner_liste, datetime=datetime)

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/download/<path:filename>")
@login_required
def download(filename):
    # Sicherheitscheck: keine Pfadmanipulation!
    if ".." in filename or filename.startswith("/"):
        return "Ungültiger Dateiname", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/notizen-pdf")
@login_required
def notizen_pdf():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT titel, ordner, code  FROM noten WHERE benutzer_id = %s ORDER BY titel", (session["user_id"],))
    noten = cur.fetchall()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 40, "Deine gespeicherten Noten")
    p.setFont("Helvetica", 12)

    y = height - 70
    for note in noten:
        titel = note[0]
        ordner = note[1]
        ID = note[2]
        if y < 40:
            p.showPage()
            y = height - 40
        p.drawString(50, y, f"• {titel} im Ordner {ordner} (ID: {ID})")
        y -= 20

    p.save()
    buffer.seek(0)
    cur.close()
    conn.close()
    return send_file(buffer, as_attachment=True, download_name="notenliste.pdf", mimetype="application/pdf")

@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

@app.errorhandler(500)
def internal_error(error):
    user_message = "Es ist ein interner Fehler aufgetreten. Wir wurden benachrichtigt."
    tb = traceback.format_exc()
    user = session.get("user_id", "Unbekannt")
    error_message = f"""
    Fehler beim Benutzer: {user}
    Fehler: {error}
    
    Traceback:
    {tb}
    """
    send_error_email("Interner Fehler im Notenarchiv", error_message)
    return render_template("error.html", message=user_message), 500

def send_error_email(subject, body):
    sender = "xxxx"
    recipient = "xxx"
    password = os.getenv("EMAIL_PASS")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    try:
        with smtplib.SMTP_SSL("xxx", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
    except Exception as e:
        print("Fehler beim Senden der Fehler-E-Mail:", e)

@app.route('/share/<int:note_id>')
@login_required
def share(note_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    token = str(uuid.uuid4())
    cur.execute("UPDATE noten SET share_token = %s WHERE id = %s", (token, note_id))
    conn.commit()
    cur.close()
    conn.close()
    share_url = url_for('shared_note', token=token, _external=True)
    return f"Freigabelink: <a href='{share_url}'>{share_url}</a>"

@app.route('/s/<token>')
def shared_note(token):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM noten WHERE share_token = %s", (token,))
    note = cur.fetchone()
    cur.close()
    conn.close()
    if note:
        # Passe dein shared_note.html so an, dass ein Downloadlink angezeigt wird:
        # {% if note.dateiname %}<a href="{{ url_for('download', filename=note.dateiname) }}">Download</a>{% endif %}
        return render_template("shared_note.html", note=note)
    else:
        return "Ungültiger oder abgelaufener Link", 404

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        return "Link ungültig oder abgelaufen."

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE benutzer SET bestaetigt = 1 WHERE email = %s", (email,))
    conn.commit()
    cur.close()
    conn.close()
    return "E-Mail bestätigt! Du kannst dich jetzt einloggen."

# Admin Dashboard
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM benutzer")
    users = cur.fetchall()
    cur.execute("SELECT * FROM noten")
    notes = cur.fetchall()
    cur.execute("SELECT * FROM paypal_payments ORDER BY payment_date DESC")
    zahlungen = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin_dashboard.html", users=users, notes=notes, zahlungen=zahlungen)

@app.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        rolle = request.form["rolle"]
        cur.execute("UPDATE benutzer SET nutzername=%s, email=%s, rolle=%s WHERE id=%s", (username, email, rolle, user_id))
        conn.commit()
        flash("Benutzer aktualisiert.")
        cur.close()
        conn.close()
        return redirect(url_for("admin_dashboard"))
    cur.execute("SELECT * FROM benutzer WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_user.html", user=user)

@app.route("/admin/edit_note/<int:note_id>", methods=["GET", "POST"])
@admin_required
def edit_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form["name"]
        beschreibung = request.form["beschreibung"]
        ordner = request.form["ordner"]
        cur.execute("UPDATE noten SET name=%s, beschreibung=%s, ordner=%s WHERE id=%s", (name, beschreibung, ordner, note_id))
        conn.commit()
        flash("Notiz aktualisiert.")
        cur.close()
        conn.close()
        return redirect(url_for("admin_dashboard"))
    cur.execute("SELECT * FROM noten WHERE id = %s", (note_id,))
    note = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_note.html", note=note)

@app.route("/admin/delete_user/<int:user_id>")
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM benutzer WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Benutzer gelöscht.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_note/<int:note_id>")
@admin_required
def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM noten WHERE id = %s", (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Notiz gelöscht.")
    return redirect(url_for("admin_dashboard"))

@app.route("/spenden", methods=["GET", "POST"])
@login_required
def spenden():
    if request.method == "POST":
        betrag = request.form["betrag"]
        # Hier ggf. weitere Logik für PayPal-Spende einfügen
        # Beispiel: Weiterleitung zu PayPal mit Betrag
        session["spenden_betrag"] = betrag
        return redirect(url_for("pay"))  # oder gleich zu PayPal-Checkout
    return render_template("spenden.html")  # Neues/angepasstes Template

@app.route("/pay")
@login_required
def pay():
    betrag = session.get("spenden_betrag", "5")  # Standardwert als Beispiel
    return render_template("pay.html", betrag=betrag)

@app.route("/payment_success")
@login_required
def payment_success():
    return "Vielen Dank für deine Spende!"

@app.route("/payment_cancelled")
@login_required
def payment_cancelled():
    return "Spende leider abgebrochen."

@app.route('/paypal/success', methods=['POST'])
@login_required
def paypal_success():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO paypal_payments (payer_name, payer_email, payment_id, amount, payment_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['payer_name'],
        data['payer_email'],
        data['payment_id'],
        data['amount'],
        datetime.now()
    ))
    conn.commit()
    cur.close()
    conn.close()
    return 'Zahlung gespeichert', 200

if __name__ == "__main__":
    app.run(debug=True)
