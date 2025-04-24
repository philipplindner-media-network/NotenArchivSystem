# NotenArchivSystem

NotenArchivSystem ist ein Python-basiertes Websystem zur Archivierung von Noten. Es ermöglicht Benutzern, digitale Noten zu speichern, zu organisieren und zu teilen. Das System bietet Benutzerregistrierung, Login, Admin-Dashboard und viele weitere Funktionen.

## Features

- **Benutzerregistrierung und Login**: Sichere Authentifizierung mit Passwort-Hashing.
- **Noten-Upload**: Hochladen und Speichern von PDF-Dateien mit automatischer QR- und Barcode-Generierung.
- **Noten-Verwaltung**: Noten hinzufügen, bearbeiten, löschen und durchsuchen.
- **Teilen von Noten**: Generieren von Freigabelinks für Noten.
- **PDF-Export**: Exportieren einer Liste aller gespeicherten Noten als PDF.
- **Admin-Dashboard**: Verwaltung von Benutzern und Noten durch Administratoren.
- **Sichere Kommunikation**: E-Mail-Bestätigung und Passwort-Zurücksetzen mit `Flask-Mail`.
- **Fehlerbenachrichtigung**: Automatische Benachrichtigung bei internen Fehlern per E-Mail.

## Technologien

Das Projekt basiert auf den folgenden Technologien:

- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Datenbank**: MySQL
- **Frontend**: HTML, CSS
- **Sonstige Bibliotheken**:
  - `qrcode` und `python-barcode` für QR- und Barcode-Generierung
  - `reportlab` für PDF-Generierung
  - `Flask-Mail` für E-Mail-Versand
  - `dotenv` für Umgebungsvariablen

## Installation

1. **Repository klonen**:
   ```bash
   git clone https://github.com/philipplindner-media-network/NotenArchivSystem.git
   cd NotenArchivSystem
2. **Virtuelle Umgebung erstellen**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Auf Windows: venv\Scripts\activate
3. **Abhängigkeiten Installieren**
    ```bash
    pip install -r requirements.txt
4. **Datenbank Anlegen und  Konfigurieren**
    - Dateien db,sql über phpmyadmin ( oder enlichensen ) auf deiene MYSQL Server hochladen
    - die datei config.json anpasse
5. **Umgebungsvariablen einrichten:**
     datei .env anlegen und folgened infos eintragen:
   ```bash
   SECRET_KEY=dein_secret_key
   EMAIL_PASS=dein_email_passwort
7. **Server starten**
   ```bash
   pyton3 app.py
   nun ist es auf online unter http://127.0.0.1:5000 zu ereichen''

## Nutzung
# Registrierung und Login
- Registriere dich mit Benutzernamen, Passwort und E-Mail-Adresse.
- Bestätige deine E-Mail-Adresse über den zugesendeten Link.
- Melde dich an, um Noten hochzuladen und zu verwalten.
# Noten hochladen
- Lade PDF-Dateien hoch und ordne sie einem Ordner zu.
- QR- und Barcodes werden automatisch generiert.
# Freigabelinks
- Teile deine Noten mit anderen über einen generierten Freigabelink.
# Admin-Dashboard
- Admins können Benutzer und Noten verwalten.
# Projektstruktur

NotenArchivSystem/
├── app.py                # Hauptanwendung
├── templates/            # HTML-Dateien
├── static/               # Statische Dateien (CSS, JS, Uploads)
├── config.json           # Datenbankkonfiguration
├── requirements.txt      # Abhängigkeiten
├── .env                  # Umgebungsvariablen
└── README.md             # Projektbeschreibung
# Lizenz
Dieses Projekt steht unter keiner spezifischen Lizenz und ist nur für interne Nutzung gedacht. Wende dich an den Autor, wenn du das Projekt verwenden möchtest.

#Kontakt
Falls du Fragen oder Probleme hast, wende dich bitte an:

E-Mail: post@philipp-lindner.de
Webseite: philipp-lindner.de
