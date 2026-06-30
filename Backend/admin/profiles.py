from flask import Blueprint, request, jsonify
from model import get_db_connection

profiles_bp = Blueprint('profiles', __name__)


def ensure_profile_columns(conn, cursor):
    cursor.execute("SHOW COLUMNS FROM profil LIKE 'about_description'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE profil ADD COLUMN about_description TEXT")
        conn.commit()


@profiles_bp.route('/api/profile', methods=['GET', 'POST'])
def manage_profile():
    conn = get_db_connection()
    cursor = conn.cursor()

    if conn is None:
        return jsonify({"status": "gagal", "pesan": "Koneksi database gagal"}), 500

    ensure_profile_columns(conn, cursor)

    if request.method == 'GET':
        cursor.execute("SELECT id, nama, peran, bio, foto, about_description FROM profil LIMIT 1")
        profile = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(profile or {})

    elif request.method == 'POST':
        data = request.get_json(silent=True) or {}
        nama = data.get('nama')
        peran = data.get('peran')
        bio = data.get('bio')
        foto = data.get('foto')
        about_description = data.get('about_description', data.get('deskripsi_tentang_saya', ''))

        cursor.execute("SELECT id FROM profil LIMIT 1")
        exist = cursor.fetchone()

        if exist:
            cursor.execute(
                "UPDATE profil SET nama=%s, peran=%s, bio=%s, foto=%s, about_description=%s WHERE id=%s",
                (nama, peran, bio, foto, about_description, exist['id'])
            )
        else:
            cursor.execute(
                "INSERT INTO profil (nama, peran, bio, foto, about_description) VALUES (%s, %s, %s, %s, %s)",
                (nama, peran, bio, foto, about_description)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "sukses"})