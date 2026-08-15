import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

try:
    import resend
except ImportError:
    resend = None

# --- 1. MUAT VARIABEL LINGKUNGAN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- 2. SET PYTHON PATH UNTUK BACKEND ---
BACKEND_DIR = os.path.join(BASE_DIR, '..', 'Backend')  # ✅ PERBAIKAN PATH
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, BASE_DIR)

# --- 3. INISIALISASI FLASK ---
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'Frontend')  # ✅ PERBAIKAN PATH
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.secret_key = os.getenv("SECRET_KEY", "bintang-rahasia-pa-2026")

if CORS is not None:
    CORS(app)

# --- 4. IMPORT BLUEPRINT (DENGAN ERROR HANDLING) ---
try:
    from admin.login import login_bp
    from admin.dashboard import dashboard_bp
    from admin.profiles import profiles_bp
    from admin.skills import skills_bp
    from admin.experience import experience_bp
    from admin.projects import projects_bp
    from admin.upload import upload_bp
    from utama.utama import utama_bp
    
    # Register blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(experience_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(utama_bp)
except ImportError as e:
    app.logger.error(f"Error importing blueprints: {str(e)}")

# --- 5. RUTE FRONTEND ---
@app.route('/admin/login')
def login_page():
    return send_from_directory(FRONTEND_DIR, 'admin/login.html')

@app.route('/admin/dashboard')
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, 'admin/dashboard.html')

@app.route('/admin/profiles')
def profiles_page():
    return send_from_directory(FRONTEND_DIR, 'admin/profiles.html')

@app.route('/admin/skills')
def skills_page():
    return send_from_directory(FRONTEND_DIR, 'admin/skills.html')

@app.route('/admin/projects')
def projects_page():
    return send_from_directory(FRONTEND_DIR, 'admin/projects.html')

@app.route('/admin/experience')
def experience_page():
    return send_from_directory(FRONTEND_DIR, 'admin/experience.html')

# --- 6. ENDPOINT CONTACT FORM ---
@app.route('/api/contact', methods=['POST'])
def send_contact_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "gagal", "pesan": "Payload data kosong"}), 400

        nama_pengirim = data.get('nama', 'Anonim')
        email_pengirim = data.get('email', 'tidak-ada-email@example.com')
        pesan = data.get('message', '')

        if resend is None:
            return jsonify({"status": "gagal", "pesan": "Library Resend belum tersedia"}), 500

        resend.api_key = os.getenv("RESEND_API_KEY")
        
        if not resend.api_key:
            return jsonify({"status": "gagal", "pesan": "API Key Resend tidak ditemukan"}), 500

        r = resend.Emails.send({
            "from": "Portfolio Contact <onboarding@resend.dev>",
            "to": "nuelcorputty@gmail.com",
            "subject": f"Pesan Portofolio Baru dari {nama_pengirim}",
            "html": f"""
                <h3>Ada Pesan Masuk dari Website Portofolio!</h3>
                <p><strong>Nama Pengirim:</strong> {nama_pengirim}</p>
                <p><strong>Email Pengirim:</strong> {email_pengirim}</p>
                <p><strong>Isi Pesan:</strong></p>
                <p style="background: #f4f4f5; padding: 10px; border-radius: 5px;">{pesan}</p>
            """
        })
        
        return jsonify({
            "status": "sukses", 
            "pesan": "Pesan berhasil dikirim!",
            "id": r.get('id')
        }), 200

    except Exception as e:
        print(f"[Error Resend API]: {str(e)}")
        return jsonify({"status": "gagal", "pesan": str(e)}), 500

# --- 7. HEALTH CHECK ENDPOINT ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

# --- JALANKAN SERVER ---
if __name__ == '__main__':
    app.run(debug=False)

# --- WSGI HANDLER UNTUK VERCEL ---
def handler(request):
    return app(request)