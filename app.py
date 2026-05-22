# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import datetime

app = Flask(__name__)
app.secret_key = 'cbt_secret_key_ultimate_v3'

# Kunci Jawaban Resmi Ujian Kimia Pascasarjana / Sarjana Lanjut
ANSWER_KEY = {
    "1": "B",  # Tawas Alum: 1M = 2.54 mS, 3M = 2.42 mS
    "2": "C",  # HMO Theory: Integral resonansi atom tak berikatan = 0
    "3": "B",  # Schrödinger Box: Prinsip Ketidakpastian Heisenberg
    "4": "A",  # Termodinamika: Ekspansi isotermal reversibel ΔU=0, q=-w
    "5": "D",  # Kinetika Reaksi Orde 1: Sisa 1/8 setelah 3 kali waktu paruh
    "6": "B",  # Spektroskopi NMR: Proton aldehida di 9.0 - 10.0 ppm
    "7": "C",  # Mekanisme SN1: Campuran rasemat akibat intermediet karbokation planar
    "8": "A",  # Persamaan Nernst: Menghubungkan potensial sel dengan kuosien reaksi Q
    "9": "C",  # Operator Hamiltonian: Nilai eigen berupa energi total observabel
    "10": "D", # Teori Medan Kristal: Oktahedral eg mengisi dx^2-y^2 dan dz^2
    "11": "B", # Spektrometri massa base peak
    "12": "C", # Sifat koligatif larutan
    "13": "A", # Hukum Raoult
    "14": "D", # Titik ekuivalen titrasi
    "15": "A", # Oksidasi anoda
    "16": "C", # Enzim menurunkan energi aktivasi
    "17": "B", # Kromatografi kiral
    "18": "D", # Asam Lewis akseptor elektron
    "19": "B", # Gas ideal tekanan rendah suhu tinggi
    "20": "A", # Ikatan hidrogen FON
    "21": "C", # HPLC waktu retensi
    "22": "B", # Efek Tyndall koloid
    "23": "A", # Eksotermik ΔH negatif
    "24": "D", # Polimer asam amino
    "25": "C", # Aturan Hückel 4n+2
    "26": "B", # Konfigurasi Fe3+
    "27": "D", # Entropi
    "28": "A", # Prinsip Le Chatelier
    "29": "C", # Oksidator reduksi
    "30": "B"  # Titrasi Karl Fischer air
}

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.json')

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "results": {}, "cheats": []}
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    if "users" not in data:
        data["users"] = {}
    if "results" not in data:
        data["results"] = {}
    if "cheats" not in data:
        data["cheats"] = []
    return data

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Failed to save database to {DB_FILE}: {str(e)}")
        raise e

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.json
    nim = data.get("nim")
    nama = data.get("nama")
    password = data.get("password")
    db = load_db()
    if nim in db["users"]:
        return jsonify({"error": "NIM sudah terdaftar"}), 400
    db["users"][nim] = {"nama": nama, "password": password}
    save_db(db)
    return jsonify({"status": "success", "message": "Pendaftaran berhasil, silakan login"}), 200

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    nim = data.get("nim")
    password = data.get("password")
    token = data.get("token")
    
    db = load_db()
    if nim not in db["users"]:
        return jsonify({"error": "NIM tidak ditemukan, silakan daftar"}), 404
    
    if db["users"][nim]["password"] != password:
        return jsonify({"error": "Kata sandi salah"}), 401
        
    if token != 'KIMIA2026':
        return jsonify({"error": "Token Ujian tidak valid"}), 401
        
    return jsonify({"status": "success", "nama": db["users"][nim]["nama"]}), 200

@app.route('/exam')
def exam():
    return render_template('exam.html')

@app.route('/api/log-strike', methods=['POST'])
def log_strike():
    data = request.json
    nim = data.get("nim", "Anonim")
    strikes = data.get("strikes", 0)
    
    log_entry = {
        "nim": nim,
        "strike_count": strikes,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db = load_db()
    db["cheats"].append(log_entry)
    save_db(db)
    print(f"⚠️ [ANTI-CHEAT VERSI 3] Mahasiswa (NIM: {nim}) terdeteksi keluar tab! Pelanggaran ke-{strikes}")
    return jsonify({"status": "success", "message": "Log kecurangan tersimpan di server"}), 200

@app.route('/api/submit', methods=['POST'])
def submit_exam():
    # Debug log to verify endpoint is hit and view raw payload
    debug_log = os.path.join(BASE_DIR, 'submit_debug.log')
    try:
        raw_body = request.get_data(as_text=True)
        with open(debug_log, 'a') as f:
            f.write(f"\n=== SUBMIT REACHED AT {datetime.datetime.now()} ===\n")
            f.write(f"URL: {request.url}\n")
            f.write(f"Headers: {dict(request.headers)}\n")
            f.write(f"Raw Body: {raw_body}\n")
            f.write("-------------------------------------\n")
    except Exception as ex:
        print(f"❌ Failed to write to submit_debug.log: {ex}")

    try:
        data = request.json or {}
        nim = data.get("nim", "Anonim")
        user_answers = data.get("answers", {})
        status_ujian = data.get("status_ujian", "Selesai Normal")
        strikes = data.get("pelanggaran", 0)
        
        # Kalkulasi nilai otomatis (Scoring System)
        correct_count = 0
        wrong_count = 0
        empty_count = 0
        
        for q_id, correct_ans in ANSWER_KEY.items():
            user_ans = user_answers.get(str(q_id))
            if not user_ans:
                empty_count += 1
            elif user_ans == correct_ans:
                correct_count += 1
            else:
                wrong_count += 1
                
        score = int((correct_count / len(ANSWER_KEY)) * 100)
        
        # Predikat Kelulusan dinamis
        if score >= 85:
            predicate = "Dengan Pujian (Cum Laude)"
        elif score >= 70:
            predicate = "Sangat Memuaskan"
        elif score >= 55:
            predicate = "Memuaskan"
        else:
            predicate = "Kurang / Tidak Lulus"

        result_record = {
            "nim": nim,
            "score": score,
            "correct": correct_count,
            "wrong": wrong_count,
            "empty": empty_count,
            "strikes": strikes,
            "status": status_ujian,
            "predicate": predicate,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        db = load_db()
        if "results" not in db:
            db["results"] = {}
        db["results"][nim] = result_record
        save_db(db)
        print(f"✅ [SUBMIT VERSI 3] NIM: {nim} | Skor Akhir: {score} | Predikat: {predicate} | Status: {status_ujian}")
        
        return jsonify({
            "status": "success",
            "score": score,
            "correct": correct_count,
            "wrong": wrong_count,
            "empty": empty_count,
            "predicate": predicate,
            "message": "Evaluasi jawaban sukses"
        }), 200
    except Exception as e:
        import traceback
        print("❌ Error in /api/submit:")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": f"Gagal menyimpan jawaban: {str(e)}"
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    log_file = os.path.join(BASE_DIR, 'flask_errors.log')
    try:
        with open(log_file, 'a') as f:
            f.write(f"\n=== GLOBAL EXCEPTION AT {datetime.datetime.now()} ===\n")
            f.write(f"Request URL: {request.url}\n")
            f.write(f"Request Method: {request.method}\n")
            f.write(f"Request Headers: {dict(request.headers)}\n")
            f.write(f"Exception: {str(e)}\n")
            traceback.print_exc(file=f)
            f.write("=======================================\n")
    except Exception as ex:
        print(f"❌ Failed to write to flask_errors.log: {ex}")
    
    return jsonify({
        "status": "error",
        "error": f"Internal Server Error (Global Handler): {str(e)}"
    }), 500

if __name__ == '__main__':
    import sys
    use_https = '--https' in sys.argv or os.environ.get('USE_HTTPS') == 'true'
    ssl_ctx = 'adhoc' if use_https else None
    if use_https:
        print("🔒 Starting Flask server with Adhoc SSL/HTTPS protocol...")
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context=ssl_ctx)
