# pyrefly: ignore [missing-import]
import streamlit as st
import datetime
import json
import os
import threading
import time
# pyrefly: ignore [missing-import]
import streamlit.components.v1 as components
import random
import base64
import firebase_admin
from firebase_admin import credentials, firestore

def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "static", "education_logo.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode('utf-8')}"
        except Exception:
            pass
    return "https://upload.wikimedia.org/wikipedia/commons/9/9c/Logo_Tut_Wuri_Handayani.png"


# Page config
st.set_page_config(
    page_title="CBT Application Portal",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kunci Jawaban Resmi Ujian Kimia Pascasarjana / Sarjana Lanjut
ANSWER_KEY = {
    "1": "B", "2": "C", "3": "B", "4": "A", "5": "D", "6": "B", "7": "C", "8": "A", "9": "C", "10": "D",
    "11": "B", "12": "C", "13": "A", "14": "D", "15": "A", "16": "C", "17": "B", "18": "D", "19": "B", "20": "A",
    "21": "C", "22": "B", "23": "A", "24": "D", "25": "C", "26": "B", "27": "D", "28": "A", "29": "C", "30": "B"
}

# Bank Soal Ujian (30 Soal)
QUESTIONS = [
    {
        "id": 1,
        "text": "Berdasarkan data praktikum analisis konduktometri yang telah dikalibrasi ulang, berapakah nilai konduktivitas yang paling akurat untuk larutan tawas (alum) pada konsentrasi 1M dan 3M?",
        "options": [
            "1M: 2,59 mS dan 3M: 2,97 mS",
            "1M: 2,54 mS dan 3M: 2,42 mS",
            "1M: 1,95 mS dan 3M: 2,10 mS",
            "1M: 3,10 mS dan 3M: 3,50 mS",
            "1M: 2,42 mS dan 3M: 2,54 mS"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 2,
        "text": "Dalam Teori Orbital Molekul Hückel (HMO) terapan pada sistem konjugasi, fungsi gelombang dibangun dari kombinasi linear orbital atom. Manakah dari berikut ini yang merupakan asumsi dasar metode HMO?",
        "options": [
            "Integral tumpang tindih (overlap integral) bernilai 1 untuk semua atom yang berdekatan.",
            "Interaksi elektron-elektron diperhitungkan secara eksplisit dalam Hamiltonian.",
            "Integral resonansi (β) diasumsikan bernilai nol untuk atom-atom yang tidak berikatan langsung.",
            "Energi tolakan inti diabaikan sepenuhnya dalam perhitungan energi total molekul.",
            "Integral Coulomb (α) memiliki nilai yang berbeda untuk setiap atom karbon dalam cincin benzena."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 3,
        "text": "Solusi persamaan Schrödinger untuk 'partikel dalam kotak 1D' menunjukkan kuantisasi energi. Mengapa energi tingkat dasar (ground state, n=1) untuk sistem ini tidak pernah bernilai nol?",
        "options": [
            "Karena partikel memiliki massa yang tak terhingga.",
            "Sesuai dengan Prinsip Ketidakpastian Heisenberg, ketidakpastian posisi (Δx) yang terbatas menyebabkan ketidakpastian momentum (Δp) > 0, sehingga energi kinetik > 0.",
            "Karena fungsi gelombang pada n=1 adalah garis lurus konstan.",
            "Karena energi potensial di dalam kotak bernilai tak terhingga.",
            "Kondisi batas (boundary conditions) mengharuskan amplitudo probabilitas bernilai maksimum di dinding kotak."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 4,
        "text": "Tinjau proses ekspansi isotermal reversibel dari suatu gas ideal. Pernyataan manakah yang benar mengenai perubahan termodinamikanya?",
        "options": [
            "Perubahan energi dalam (ΔU) bernilai nol dan q = -w.",
            "Sistem melepaskan panas ke lingkungan.",
            "Perubahan entalpi (ΔH) bernilai negatif.",
            "Kerja (w) yang dilakukan oleh sistem bernilai positif.",
            "Perubahan entropi lingkungan (ΔS_surr) bernilai positif."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 5,
        "text": "Peluruhan isotop radioaktif mengikuti kinetika reaksi orde pertama. Jika waktu paruh (t1/2) isotop tersebut adalah 20 menit, berapakah fraksi isotop yang tersisa setelah 1 jam?",
        "options": [
            "1/2",
            "1/3",
            "1/6",
            "1/8",
            "1/16"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 6,
        "text": "Pada spektroskopi Resonansi Magnetik Inti (NMR) 1H, proton yang terikat pada karbon aldehida (R-CHO) biasanya muncul pada rentang pergeseran kimia (chemical shift, δ) yang mana?",
        "options": [
            "0.9 - 1.5 ppm",
            "9.0 - 10.0 ppm",
            "6.5 - 8.0 ppm",
            "3.5 - 4.5 ppm",
            "11.0 - 12.0 ppm"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 7,
        "text": "Reaksi substitusi nukleofilik unimolekuler (SN1) memiliki karakteristik khusus dibandingkan SN2. Manakah dari sifat berikut yang PALING tepat menggambarkan reaksi SN1?",
        "options": [
            "Laju reaksi bergantung pada konsentrasi substrat dan nukleofil.",
            "Reaksi berlangsung dalam satu tahap tanpa pembentukan intermediet.",
            "Menghasilkan campuran rasemat jika substrat adalah karbon kiral.",
            "Laju reaksi meningkat seiring dengan berkurangnya kepolaran pelarut.",
            "Hanya terjadi pada alkil halida primer."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 8,
        "text": "Dalam elektrokimia, Persamaan Nernst sangat fundamental untuk menentukan potensial sel. Persamaan Nernst menghubungkan potensial sel terukur dengan...",
        "options": [
            "Potensial sel standar dan kuosien reaksi (Q) dari spesi elektroaktif.",
            "Hanya suhu dan konstanta Faraday.",
            "Laju transfer elektron pada permukaan elektroda.",
            "Energi aktivasi dari reaksi redoks selular.",
            "Konduktivitas molar ekuivalen dari larutan elektrolit."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 9,
        "text": "Di dalam mekanika kuantum kimiawi, Operator Hamiltonian (Ĥ) beroperasi pada fungsi gelombang (Ψ) suatu sistem. Nilai eigen (eigenvalue) yang dihasilkan dari operasi ĤΨ = EΨ merepresentasikan...",
        "options": [
            "Momentum sudut orbital partikel.",
            "Probabilitas densitas elektron.",
            "Energi total observabel dari sistem tersebut.",
            "Vektor posisi rata-rata partikel.",
            "Fungsi kerapatan spin."
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 10,
        "text": "Menurut Teori Medan Kristal (Crystal Field Theory), ketika ligan mendekati ion logam transisi dalam geometri oktahedral, terjadi pembelahan (splitting) orbital d. Orbital mana yang mengalami kenaikan energi paling besar (berada pada tingkat eg)?",
        "options": [
            "dxy dan dyz",
            "dxz dan dxy",
            "dz^2 dan dxy",
            "dx^2-y^2 dan dz^2",
            "dyz dan dx^2-y^2"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 11,
        "text": "Dalam spektrometri massa, puncak dasar (base peak) didefinisikan sebagai...",
        "options": [
            "Puncak ion molekul",
            "Puncak dengan kelimpahan relatif 100%",
            "Puncak isotop M+1",
            "Puncak dengan massa terbesar",
            "Puncak fragmen kation radikal"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 12,
        "text": "Manakah dari berikut ini yang merupakan sifat koligatif larutan?",
        "options": ["Densitas", "Tegangan permukaan", "Penurunan tekanan uap", "Indeks bias", "Viskositas"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 13,
        "text": "Hukum Raoult menyatakan bahwa tekanan uap pelarut dalam larutan ideal...",
        "options": [
            "Berbanding lurus dengan fraksi mol pelarut",
            "Berbanding lurus dengan molalitas zat terlarut",
            "Berbanding terbalik dengan suhu absolut",
            "Tidak bergantung pada konsentrasi",
            "Sama dengan tekanan osmotik"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 14,
        "text": "Dalam titrasi asam-basa, titik ekuivalen adalah saat...",
        "options": [
            "Indikator berubah warna",
            "pH larutan mencapai 7",
            "Laju reaksi maju dan mundur sama",
            "Mol asam tepat habis bereaksi dengan mol basa",
            "Titrasi dihentikan"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 15,
        "text": "Pada sel galvanik, setengah reaksi oksidasi terjadi pada...",
        "options": ["Anoda", "Katoda", "Jembatan garam", "Elektrolit", "Kabel luar"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 16,
        "text": "Enzim bertindak sebagai biokatalis dengan cara...",
        "options": [
            "Menggeser kesetimbangan ke kanan",
            "Meningkatkan perubahan entalpi",
            "Menurunkan energi aktivasi reaksi",
            "Meningkatkan energi kinetik rata-rata",
            "Mengubah mekanisme termodinamika"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 17,
        "text": "Isomer optik (enantiomer) dapat dipisahkan menggunakan teknik...",
        "options": ["Distilasi fraksional", "Kromatografi kiral", "Ekstraksi pelarut cair-cair", "Kristalisasi sederhana", "Sublimasi"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 18,
        "text": "Menurut teori asam-basa Lewis, asam adalah...",
        "options": [
            "Donor proton (H+)",
            "Akseptor proton",
            "Donor pasangan elektron",
            "Akseptor pasangan elektron",
            "Donor ion OH-"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 19,
        "text": "Persamaan gas ideal (PV = nRT) paling akurat pada kondisi...",
        "options": [
            "Tekanan tinggi dan suhu tinggi",
            "Tekanan rendah dan suhu tinggi",
            "Tekanan tinggi dan suhu rendah",
            "Tekanan rendah dan suhu rendah",
            "Volume gas mendekati nol"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 20,
        "text": "Ikatan hidrogen paling kuat terjadi pada molekul yang mengandung atom hidrogen yang berikatan dengan...",
        "options": ["F, O, atau N", "C, H, atau O", "Cl, Br, atau I", "S, P, atau Se", "Logam transisi"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 21,
        "text": "Dalam kromatografi cair kinerja tinggi (HPLC), waktu retensi dipengaruhi oleh...",
        "options": [
            "Suhu detektor",
            "Konsentrasi sampel",
            "Polaritas fase diam dan fase gerak",
            "Ketebalan sel aliran",
            "Tekanan pompa hampa gas"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 22,
        "text": "Efek Tyndall merupakan karakteristik utama dari...",
        "options": ["Larutan sejati", "Sistem koloid", "Suspensi kasar", "Emulsi padat", "Aerosol cair"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 23,
        "text": "Pada reaksi eksotermik, nilai perubahan entalpi (ΔH) adalah...",
        "options": ["Negatif", "Positif", "Nol", "Tak terhingga", "Bergantung katalis"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 24,
        "text": "Polimer yang terbentuk dari monomer asam amino melalui ikatan peptida adalah...",
        "options": ["Polisakarida", "DNA/RNA", "Lipid", "Protein", "Nilon"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 25,
        "text": "Senyawa aromatik mematuhi aturan Hückel jika memiliki elektron pi sebanyak...",
        "options": ["2n", "4n", "4n + 2", "4n - 2", "2n + 4"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 26,
        "text": "Konfigurasi elektron keadaan dasar untuk ion Fe3+ (Z=26) adalah...",
        "options": ["[Ar] 4s2 3d3", "[Ar] 3d5", "[Ar] 4s1 3d4", "[Ar] 3d6", "[Ar] 4s2 3d4"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 27,
        "text": "Dalam termodinamika, entropi (S) adalah ukuran dari...",
        "options": [
            "Kandungan panas total",
            "Energi bebas sistem",
            "Laju reaksi termal",
            "Ketidakteraturan atau keacakan sistem",
            "Kapasitas kalor sistem"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 28,
        "text": "Prinsip Le Chatelier menyatakan bahwa...",
        "options": [
            "Sistem kesetimbangan akan bergeser untuk meminimalkan gangguan",
            "Massa zat sebelum dan sesudah reaksi sama",
            "Energi tidak dapat diciptakan atau dimusnahkan",
            "Tekanan total sama dengan jumlah tekanan parsial",
            "Semua gas ideal berkelakuan sama"
        ],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 29,
        "text": "Dalam reaksi redoks, zat yang mengalami penurunan bilangan oksidasi bertindak sebagai...",
        "options": ["Reduktor", "Katalis", "Oksidator", "Indikator", "Intermediet"],
        "keys": ["A", "B", "C", "D", "E"]
    },
    {
        "id": 30,
        "text": "Metode titrasi Karl Fischer digunakan secara spesifik untuk menentukan kadar...",
        "options": ["Asam", "Air", "Basa", "Klorida", "Logam berat"],
        "keys": ["A", "B", "C", "D", "E"]
    }
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.json')
_db_lock = threading.Lock()
_firestore_db = None

def init_firebase():
    global _firestore_db
    if _firestore_db is not None:
        return _firestore_db
        
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                # Perbaiki format private key yang mengandung literal \n dari secrets
                if "private_key" in cred_dict:
                    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(cred_dict)
            else:
                cred = credentials.Certificate('firebase_credentials.json')
            firebase_admin.initialize_app(cred)
        # Using specific named database 'cbt-application-pro' as requested
        _firestore_db = firestore.client(database="cbt-application-pro")
        return _firestore_db
    except Exception as e:
        print(f"Failed to connect to Firebase: {e}")
        return None

def load_db():
    with _db_lock:
        fdb = init_firebase()
        default_data = {"users": {}, "results": {}, "cheats": []}
        
        # 1. Jika Firebase tidak ada/gagal, gunakan database lokal (database.json)
        if fdb is None:
            if os.path.exists(DB_FILE):
                try:
                    with open(DB_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "users" not in data: data["users"] = {}
                        if "results" not in data: data["results"] = {}
                        if "cheats" not in data: data["cheats"] = []
                        return data
                except Exception as e:
                    print(f"Error reading local database.json: {e}")
            return default_data
            
        # 2. Jika Firebase berhasil, gunakan Firestore
        try:
            doc_ref = fdb.collection('cbt_exam_pro').document('database')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                if "users" not in data: data["users"] = {}
                if "results" not in data: data["results"] = {}
                if "cheats" not in data: data["cheats"] = []
                return data
            else:
                return default_data
        except Exception as e:
            print(f"Error reading from Firestore: {e}")
            return default_data

def save_db(data):
    with _db_lock:
        fdb = init_firebase()
        
        # 1. Simpan ke lokal (sebagai backup utama atau fallback)
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving to local database.json: {e}")
            
        # 2. Simpan ke Firebase (hanya jika terkoneksi)
        if fdb is not None:
            try:
                doc_ref = fdb.collection('cbt_exam_pro').document('database')
                doc_ref.set(data)
            except Exception as e:
                print(f"Error saving to Firestore: {e}")

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "nim" not in st.session_state:
    st.session_state.nim = ""
if "nama" not in st.session_state:
    st.session_state.nama = ""
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "doubts" not in st.session_state:
    st.session_state.doubts = {}
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "strikes" not in st.session_state:
    st.session_state.strikes = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "photo_captured" not in st.session_state:
    st.session_state.photo_captured = None
if "simulasi_done" not in st.session_state:
    st.session_state.simulasi_done = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Global Sidebar Theme Toggle (Icon Only)
with st.sidebar:
    theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
    if st.button(theme_icon, key="theme_toggle_btn", help="Ubah Tema"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()


# Captcha generation
if "captcha_val" not in st.session_state:
    n1 = random.randint(2, 9)
    n2 = random.randint(2, 5)
    st.session_state.captcha_text = f"Berapa Hasil {n1}x{n2}"
    st.session_state.captcha_val = n1 * n2

# Inject Modern CSS Styling & Zero-Gravity Interactive Canvas Background
def render_professional_background():
    # Make Streamlit containers transparent to show the interactive canvas behind them
    css_file = "static/html/app_style_dark.html" if st.session_state.theme == "dark" else "static/html/app_style.html"
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)
    
    # JavaScript payload for zero-gravity constellation background following cursor
    # Runs directly in the parent window context via base64 decoding on invalid image onerror,
    # completely bypassing cross-origin iframe blockage!
    with open("static/js/bg_animation.js", "r", encoding="utf-8") as f:
        bg_js = f.read()
    
    import base64
    encoded_bg_js = base64.b64encode(bg_js.encode('utf-8')).decode('utf-8')
    st.markdown(f'<img src="x" onerror="eval(atob(\'{encoded_bg_js}\'))" style="display:none;">', unsafe_allow_html=True)

render_professional_background()

# Hidden triggers listener
def render_anti_cheat_listener():
    with open("static/js/anti_cheat.js", "r", encoding="utf-8") as f:
        cheat_script = f.read()
    import base64
    encoded_cheat_js = base64.b64encode(cheat_script.encode('utf-8')).decode('utf-8')
    st.markdown(f'<img src="x" onerror="eval(atob(\'{encoded_cheat_js}\'))" style="display:none;">', unsafe_allow_html=True)

# JS Countdown timer widget
def render_countdown_timer(duration_seconds):
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, int(duration_seconds - elapsed))
    
    with open("static/js/timer.js", "r", encoding="utf-8") as f:
        timer_js = f.read().replace("{remaining}", str(remaining))
    import base64
    encoded_timer_js = base64.b64encode(timer_js.encode('utf-8')).decode('utf-8')
    st.markdown(f'<img src="x" onerror="eval(atob(\'{encoded_timer_js}\'))" style="display:none;">', unsafe_allow_html=True)

# Live webcam stream component for side proctoring
def render_live_webcam():
    with open("static/html/webcam.html", "r", encoding="utf-8") as f:
        webcam_html = f.read()
    with open("static/js/webcam.js", "r", encoding="utf-8") as f:
        webcam_js = f.read()
    import base64
    encoded_webcam_js = base64.b64encode(webcam_js.encode('utf-8')).decode('utf-8')
    st.markdown(webcam_html + f'<img src="x" onerror="eval(atob(\'{encoded_webcam_js}\'))" style="display:none;">', unsafe_allow_html=True)

def submit_exam_results(is_forced=False):
    score, correct, wrong, empty, predicate = calculate_results()
    nim = st.session_state.nim
    status_ujian = "Disikualifikasi" if is_forced else "Selesai Normal"
    
    record = {
        "nim": nim,
        "score": score,
        "correct": correct,
        "wrong": wrong,
        "empty": empty,
        "strikes": st.session_state.strikes,
        "status": status_ujian,
        "predicate": predicate,
        "answers": dict(st.session_state.answers),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    db = load_db()
    db["results"][nim] = record
    save_db(db)
    
    st.session_state.results = record
    st.session_state.page = "results"
    st.rerun()

def calculate_results():
    correct = 0
    wrong = 0
    empty = 0
    
    for q in QUESTIONS:
        q_id = str(q["id"])
        ans = st.session_state.answers.get(q_id)
        correct_ans = ANSWER_KEY[q_id]
        if not ans:
            empty += 1
        elif ans == correct_ans:
            correct += 1
        else:
            wrong += 1
            
    score = int((correct / len(QUESTIONS)) * 100)
    
    if score >= 85:
        predicate = "Dengan Pujian (Cum Laude)"
    elif score >= 70:
        predicate = "Sangat Memuaskan"
    elif score >= 55:
        predicate = "Memuaskan"
    else:
        predicate = "Kurang / Tidak Lulus"
        
    return score, correct, wrong, empty, predicate

# --- PAGE ROUTING ---

# 1. Login Page
if st.session_state.page == "login":
    col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
    with col_l2:
        st.markdown("<div class='cbt-container' style='padding-top: 30px;'>", unsafe_allow_html=True)
        # Curve banner header
        logo_url = get_logo_base64()
        st.markdown("""
        <div class="cbt-logo-wrap">
            <img src="{logo_url}">
        </div>
        <div class="cbt-title">Kampus Inovatif CBT</div>
        <div class="cbt-subtitle">Selamat datang! Silakan masuk dengan NIM & kata sandi Anda.</div>
        """.format(logo_url=logo_url), unsafe_allow_html=True)
        
        nim = st.text_input("Username", value=st.session_state.get("reg_nim", ""))
        password = st.text_input("Password", type="password", value=st.session_state.get("reg_password", ""))
        
        # Math captcha
        captcha_ans = st.text_input(st.session_state.captcha_text, placeholder="Masukkan Hasil")
        
        if st.button("Login", use_container_width=True, type="primary"):
            nim = nim.strip()
            password = password.strip()
            captcha_ans = captcha_ans.strip()
            
            try:
                entered_val = int(captcha_ans)
            except ValueError:
                entered_val = None
                
            if not nim or not password or not captcha_ans:
                st.error("Semua kolom isian wajib diisi!")
            elif entered_val != st.session_state.captcha_val:
                st.error("Hasil perhitungan matematika (Captcha) salah!")
                # Regen captcha on fail
                n1 = random.randint(2, 9)
                n2 = random.randint(2, 5)
                st.session_state.captcha_text = f"Berapa Hasil {n1}x{n2}"
                st.session_state.captcha_val = n1 * n2
                st.rerun()
            else:
                db = load_db()
                if nim not in db["users"]:
                    st.error("Akun tidak ditemukan. Silakan daftar terlebih dahulu.")
                elif db["users"][nim]["password"] != password:
                    st.error("Kata sandi salah.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.nim = nim
                    st.session_state.nama = db["users"][nim]["nama"]
                    st.session_state.page = "dashboard"
                    st.rerun()
                    
        st.markdown("---")
        if st.button("Belum punya akun? Daftar", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
            
        st.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 20px;'>
            © CBT Application. Avnet.id, 2025
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 2. Register Page
elif st.session_state.page == "register":
    col_r1, col_r2, col_r3 = st.columns([1, 1.8, 1])
    with col_r2:
        st.markdown("<div class='cbt-container'>", unsafe_allow_html=True)
        st.markdown("""
            <div class="cbt-logo-wrap" style="margin-top: 10px;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;border-radius:16px;background:#eff6ff;color:#1a56db;font-size:2.5rem;border:1px solid #bfdbfe;">📝</span>
            </div>
            <div class="cbt-title">Pendaftaran Akun</div>
            <div class="cbt-subtitle">Buat profil baru untuk mengikuti ujian CBT</div>
        """, unsafe_allow_html=True)
        
        nim = st.text_input("Nomor Induk Mahasiswa (NIM)")
        nama = st.text_input("Nama Lengkap")
        password = st.text_input("Kata Sandi", type="password")
        
        if st.button("Daftarkan Akun", use_container_width=True, type="primary"):
            nim = nim.strip()
            nama = nama.strip()
            password = password.strip()
            
            if not nim or not nama or not password:
                st.error("Semua kolom isian wajib diisi!")
            else:
                db = load_db()
                if nim in db["users"]:
                    st.error("NIM sudah terdaftar!")
                else:
                    db["users"][nim] = {"nama": nama, "password": password}
                    save_db(db)
                    st.session_state.reg_nim = nim
                    st.session_state.reg_password = password
                    st.success("Pendaftaran berhasil! Mengalihkan ke login...")
                    time.sleep(1.5)
                    st.session_state.page = "login"
                    st.rerun()
                    
        if st.button("Sudah punya akun? Masuk", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 3. Student Dashboard
elif st.session_state.page == "dashboard":
    # Sidebar Navigation
    st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 40px; margin-top: 20px;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #1a56db; line-height: 1.2;">Kampus<br>Inovatif</div>
            <div style="font-size: 0.7rem; color: #64748b;">Oleh GuruInovatif.id</div>
        </div>
        <div style="font-size: 0.8rem; color: #64748b; font-weight: 700; margin-bottom: 12px; margin-left: 12px;">Menu</div>
        <div style="background: #1a56db; color: white; padding: 12px 16px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; gap: 12px; margin-bottom: 8px; cursor: pointer;">
            <span>🏠</span> Beranda
        </div>
        <div style="color: #64748b; padding: 12px 16px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; gap: 12px; margin-bottom: 24px; cursor: pointer;">
            <span>📋</span> Kelas
        </div>
        <div style="font-size: 0.8rem; color: #64748b; font-weight: 700; margin-bottom: 12px; margin-left: 12px;">Lainnya</div>
        <div style="color: #64748b; padding: 12px 16px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; gap: 12px; cursor: pointer;">
            <span>⚙️</span> Pengaturan
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()

    # Main Content Area
    st.markdown("<div style='max-width: 1080px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    # Header profile
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 20px;">
            <div>
                <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Beranda</h1>
                <div style="color: #64748b; font-size: 0.85rem;">Menu / Beranda</div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: #94a3b8; font-size: 1.2rem;">🔔</span>
                <img src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=100&h=100&q=80" 
                     style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover;">
                <div>
                    <div style="font-weight: 700; color: #1e293b; font-size: 0.95em;">{st.session_state.nama}</div>
                    <div style="color: #64748b; font-size: 0.8em; font-weight: 500;">Mahasiswa</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Metrics Cards
    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px;">
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="background: #dcfce7; color: #16a34a; width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem;">✅</div>
                <div>
                    <div style="color: #0f172a; font-weight: 700; font-size: 1rem; margin-bottom: 4px;">Total Ujian</div>
                    <div style="color: #16a34a; font-weight: 800; font-size: 1.5rem;">20 <span style="font-size: 0.5em; color: #64748b;">Ujian</span></div>
                </div>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="background: #fef3c7; color: #d97706; width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem;">📄</div>
                <div>
                    <div style="color: #0f172a; font-weight: 700; font-size: 1rem; margin-bottom: 4px;">Ujian Diambil</div>
                    <div style="color: #d97706; font-weight: 800; font-size: 1.5rem;">10 <span style="font-size: 0.5em; color: #64748b;">Ujian</span></div>
                </div>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="background: #fee2e2; color: #dc2626; width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem;">📚</div>
                <div>
                    <div style="color: #0f172a; font-weight: 700; font-size: 1rem; margin-bottom: 4px;">Ujian Tersisa</div>
                    <div style="color: #dc2626; font-weight: 800; font-size: 1.5rem;">10 <span style="font-size: 0.5em; color: #64748b;">Ujian</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<h3 style='color: #1e293b; font-size: 1.2em; font-weight: 700; margin-bottom: 20px;'>Ujian Mendatang</h3>", unsafe_allow_html=True)
        
    # Stylized Exam Card (Kampus Inovatif Style)
    st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #1e293b; margin-bottom: 8px;">KIMIA DASAR TA 24</div>
            <div style="background: #1e293b; border-radius: 16px; overflow: hidden; position: relative; padding: 24px; color: white;">
                <!-- Decorative rings -->
                <div style="position: absolute; right: -20px; top: -20px; width: 100px; height: 100px; border: 15px solid #1a56db; border-radius: 50%; opacity: 0.8;"></div>
                <div style="position: absolute; right: 30px; bottom: -30px; width: 80px; height: 80px; border: 12px solid #f59e0b; border-radius: 50%; opacity: 0.9;"></div>
                
                <h3 style="color: white; font-size: 1.3rem; margin: 0 0 8px 0; font-weight: 700; position: relative; z-index: 2;">Ujian Akhir Semester</h3>
                <div style="font-size: 0.9rem; color: #94a3b8; position: relative; z-index: 2;">{st.session_state.nama}</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 8px; border-bottom: 1px solid #e2e8f0;">
                <div style="color: #1a56db; font-weight: 600; font-size: 0.9rem;">04 Juni 2026</div>
                <div style="border: 1px solid #e2e8f0; padding: 6px 16px; border-radius: 8px; color: #1a56db; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    👁️ Preview
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Exam Actions
    if not st.session_state.simulasi_done:
        if st.button("Ikuti Ujian Ini", use_container_width=True, type="primary"):
            st.session_state.simulasi_done = True
            st.rerun()
    else:
        if st.button("Kerjakan Ujian", use_container_width=True, type="primary"):
            st.session_state.page = "gated_rules"
            st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True) # End of container

    # Mock Bottom Navigation menu matching screenshots
    st.markdown("""
        <div style="
            display: flex;
            justify-content: space-around;
            align-items: center;
            border-top: 1px solid #cbd5e1;
            padding-top: 15px;
            margin-top: 35px;
            background: #f8fafc;
            margin-left: -30px;
            margin-right: -30px;
            margin-bottom: -30px;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            padding-bottom: 15px;
        ">
            <div style="text-align: center; color: #1d4ed8; font-weight: bold; cursor: pointer;">
                <div style="font-size: 1.25em;">🏠</div>
                <div style="font-size: 0.72em; margin-top: 2px;">Beranda</div>
            </div>
            <div style="text-align: center; color: #64748b; cursor: pointer;">
                <div style="font-size: 1.25em;">📋</div>
                <div style="font-size: 0.72em; margin-top: 2px;">Riwayat Saya</div>
            </div>
            <div style="text-align: center; color: #64748b; cursor: pointer;">
                <div style="font-size: 1.25em;">👤</div>
                <div style="font-size: 0.72em; margin-top: 2px;">Profil</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Gated rules (Identification photo scan)
elif st.session_state.page == "gated_rules":
    st.markdown("<div style='max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0f172a; font-weight: 800; font-size: 1.8rem; margin-bottom: 8px;'>🛡️ Validasi Identitas & Pengawasan</h2>", unsafe_allow_html=True)
    st.write("Silakan izinkan kamera dan ambil foto verifikasi wajah Anda sebelum membuka lembar ujian.")
    
    agree = st.checkbox("Saya setuju untuk mengikuti tata tertib pengawasan ujian akademik.",
                        value=st.session_state.get("gated_agree", False))
    st.session_state.gated_agree = agree

    photo = st.camera_input("Ambil Foto Verifikasi Wajah")
    
    # Simpan foto ke session_state segera saat ada foto baru
    if photo is not None:
        st.session_state.photo_captured = photo.getvalue()
    
    # Tampilkan status foto
    if st.session_state.photo_captured is not None:
        st.success("✅ Wajah Anda telah terekam dan terverifikasi! Klik **Mulai Ujian** untuk melanjutkan.")
    else:
        st.info("📷 Silakan ambil foto wajah Anda terlebih dahulu menggunakan kamera di atas.")
    
    # Tombol Mulai Ujian — aktif jika agree DAN foto sudah ada di session_state
    photo_ok = st.session_state.photo_captured is not None
    btn_disabled = not (agree and photo_ok)
    
    if btn_disabled:
        if not agree:
            st.warning("⚠️ Centang persetujuan tata tertib di atas untuk melanjutkan.")
        elif not photo_ok:
            st.warning("⚠️ Ambil foto verifikasi wajah terlebih dahulu.")
    
    if st.button("▶️ Mulai Ujian", use_container_width=True, type="primary", disabled=btn_disabled):
        st.session_state.page = "exam"
        st.session_state.start_time = time.time()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 5. Exam Page
elif st.session_state.page == "exam":
    elapsed = time.time() - st.session_state.start_time
    if elapsed >= 5400:
        submit_exam_results(is_forced=True)
        
    render_anti_cheat_listener()
    
    # Sidebar: Live record webcam proctoring
    st.sidebar.markdown("### 👤 Identitas Mahasiswa")
    st.sidebar.info(f"**NIM**: {st.session_state.nim}\n\n**Nama**: {st.session_state.nama}")
    
    st.sidebar.markdown("### 📷 Pengawasan Aktif")
    render_live_webcam()
    
    st.sidebar.markdown("---")
    
    # (Peta Navigasi Soal removed from sidebar as it is now in the main left column)
    # Hidden controls
    st.markdown("<div class='hidden-btn-container'>", unsafe_allow_html=True)
    if st.button("__TRIGGER_STRIKE__", key="trigger_strike_btn"):
        st.session_state.strikes += 1
        db = load_db()
        db["cheats"].append({
            "nim": st.session_state.nim,
            "strike_count": st.session_state.strikes,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_db(db)
        if st.session_state.strikes >= 4:
            submit_exam_results(is_forced=True)
            
    if st.button("__TIMER_EXPIRED__", key="timer_expired_btn"):
        submit_exam_results(is_forced=False)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.strikes > 0:
        st.markdown(f"""
        <div style='background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; color: #ef4444;'>
            🚨 DETEKSI AKTIVITAS ILEGAL! Anda meninggalkan jendela lembar ujian.<br>
            Strike Pelanggaran: {st.session_state.strikes} / 3<br>
            <span style='font-size: 0.85em; font-weight: normal; color: #fca5a5;'>Peringatan: Pada strike berikutnya (ke-4), lembar ujian Anda akan langsung dikunci otomatis.</span>
        </div>
        """, unsafe_allow_html=True)

    # Main Question Panel (Single Column Layout matching middle screen in screenshot)
    st.markdown("<div style='max-width: 1080px; margin: 0 auto; padding-top: 25px;'>", unsafe_allow_html=True)
    
    # 2 Column layout for Exam Grid and Question
    col_q1, col_q2 = st.columns([1, 2.5], gap="large")
    
    with col_q1:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 16px; font-size: 1.1rem;">Navigasi Soal</div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">
        """, unsafe_allow_html=True)
        
        # Grid directly in col_q1
        for q_num in range(1, len(QUESTIONS) + 1):
            is_current = (st.session_state.current_q == q_num)
            is_doubt = st.session_state.doubts.get(str(q_num), False)
            is_answered = (st.session_state.answers.get(str(q_num)) is not None)
            
            # Use columns to render the grid properly without creating a huge HTML string,
            # wait, streamlit buttons inside columns are better.
            # But grid layout in HTML with Streamlit buttons is tricky. We can use a Streamlit grid or columns.
            pass
            
        # We will render the grid using Streamlit columns inside col_q1
        for row in range(6):
            cols = st.columns(5)
            for col_idx in range(5):
                q_num = row * 5 + col_idx + 1
                if q_num > len(QUESTIONS): continue
                with cols[col_idx]:
                    is_current = (st.session_state.current_q == q_num)
                    is_doubt = st.session_state.doubts.get(str(q_num), False)
                    is_answered = (st.session_state.answers.get(str(q_num)) is not None)
                    
                    if is_current:
                        label = f"👉{q_num}"
                    elif is_doubt:
                        label = f"🟡{q_num}"
                    elif is_answered:
                        label = f"🟢{q_num}"
                    else:
                        label = f"⚪{q_num}"
                        
                    if st.button(label, key=f"nav_grid_{q_num}", use_container_width=True):
                        st.session_state.current_q = q_num
                        st.rerun()
                        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Calculations
        answered_c = len([ans for ans in st.session_state.answers.values() if ans])
        doubt_c = len([dbt for dbt in st.session_state.doubts.values() if dbt])
        not_answered_c = len(QUESTIONS) - answered_c
        
        st.markdown(f"""
        <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e2e8f0;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 16px; font-size: 1.1rem;">Keterangan</div>
            <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.9rem;">
                <div style="display: flex; justify-content: space-between;"><span>🟢 Dijawab</span> <strong>{answered_c}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>🟡 Ragu-ragu</span> <strong>{doubt_c}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>⚪ Belum</span> <strong>{not_answered_c}</strong></div>
            </div>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 15px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span style="font-size: 0.85em; font-weight: 600; color: #64748b;">Sisa Waktu</span>
                <span style="font-weight: 800; color: #ef4444; background: #fee2e2; padding: 4px 12px; border-radius: 20px;" id="countdown">--:--</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_countdown_timer(5400) # 90 minutes
        
        if st.button("Selesaikan Ujian", type="primary", use_container_width=True):
            submit_exam_results(is_forced=False)
            
    with col_q2:
        q_data = QUESTIONS[st.session_state.current_q - 1]
        q_id_str = str(q_data["id"])
        
        # Question header
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; padding: 24px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 1.4rem;">Pertanyaan {st.session_state.current_q}/{len(QUESTIONS)}</h2>
                <div style="background: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600;">Pilihan Ganda</div>
            </div>
            <div style="font-size: 1.1rem; line-height: 1.7; color: #1e293b; margin-bottom: 24px;">
                {q_data["text"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Question body text card
    st.markdown(f"""
    <div style="border: 1.5px solid #cbd5e1; border-top: none; background: white; padding: 25px; font-size: 1.05em; line-height: 1.6; color: #1e293b; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; margin-bottom: 20px;">
        {q_data["text"]}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("Pilih jawaban yang menurut anda benar:")
    
    # Answering options styling
    current_ans = st.session_state.answers.get(q_id_str)
    opt_index = None
    if current_ans in q_data["keys"]:
        opt_index = q_data["keys"].index(current_ans)
        
    selected_opt = st.radio(
        "Jawaban",
        options=q_data["options"],
        index=opt_index,
        key=f"q_radio_opt_{st.session_state.current_q}",
        label_visibility="collapsed"
    )
    
    if selected_opt:
        opt_key = q_data["keys"][q_data["options"].index(selected_opt)]
        st.session_state.answers[q_id_str] = opt_key
        st.session_state.doubts[q_id_str] = False
        
        
    # We removed the generic checkbox because we use the "Tandai Soal" button below
    
    # Empty section since summary badges are now in the left column        
    # Bottom Navigation action bar with layout matching the mockup
    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        if st.button("← Sebelumnya", key="prev_btn", use_container_width=True, disabled=(st.session_state.current_q == 1)):
            st.session_state.current_q -= 1
            st.rerun()
    with nav_col2:
        # We handle doubt marking differently now
        # Streamlit doesn't easily let us change the button style based on session state on the fly without custom components,
        # but we can use a regular button to toggle
        is_current_doubt = st.session_state.doubts.get(q_id_str, False)
        doubt_label = "Unmark Ragu" if is_current_doubt else "Tandai Soal"
        if st.button(doubt_label, key="doubt_btn_toggle", use_container_width=True):
            st.session_state.doubts[q_id_str] = not is_current_doubt
            st.rerun()
            
    with nav_col3:
        if st.session_state.current_q < len(QUESTIONS):
            if st.button("Selanjutnya →", key="next_btn", use_container_width=True, type="primary"):
                st.session_state.current_q += 1
                st.rerun()
        else:
            if st.button("Selesai & Kumpulkan", use_container_width=True, type="primary"):
                st.session_state.page = "confirm_submit"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Confirm Submit Page
elif st.session_state.page == "confirm_submit":
    col_c1, col_c2, col_c3 = st.columns([1, 2.2, 1])
    with col_c2:
        st.markdown("<div class='cbt-container' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2>📋 Konfirmasi Penyerahan Ujian</h2>", unsafe_allow_html=True)
        st.write("Apakah Anda sudah yakin dengan seluruh jawaban Anda? Hasil evaluasi akan dikalkulasi secara otomatis oleh server.")
        
        col_cf1, col_cf2 = st.columns(2)
        with col_cf1:
            if st.button("Cek Kembali", use_container_width=True):
                st.session_state.page = "exam"
                st.rerun()
        with col_cf2:
            if st.button("Kumpulkan Sekarang", use_container_width=True, type="primary"):
                submit_exam_results(is_forced=False)
        st.markdown("</div>", unsafe_allow_html=True)

# 6. Results Page
elif st.session_state.page == "results":
    res = st.session_state.results
    col_rs1, col_rs2, col_rs3 = st.columns([1, 2.2, 1])
    with col_rs2:
        st.markdown("<div class='cbt-container' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2>Ujian Selesai</h2>", unsafe_allow_html=True)
        
        if res["status"] == "Disikualifikasi":
            st.markdown("""
            <div style='background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; color: #ef4444;'>
                AKSES DIKUNCI SISTEM<br>
                <span style='font-size: 0.9em; font-weight: normal; color: #fca5a5;'>Anda telah melanggar aturan kunci jendela ujian sebanyak 4 kali.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #10b981; font-weight: bold;'>Ujian Anda telah terekam penuh di sistem akademik.</p>", unsafe_allow_html=True)
            
        st.markdown(f"""
            <div class="score-radial">
                <span class="score-value">{res["score"]}</span>
                <span class="score-label">Skor Ujian</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<h4 style='color: #1d4ed8; margin-bottom: 25px;'>Predikat: {res['predicate']}</h4>", unsafe_allow_html=True)
        
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1:
            st.markdown(f"<h3 style='color: #10b981; margin:0;'>{res['correct']}</h3><label style='color:#64748b;'>Benar</label>", unsafe_allow_html=True)
        with col_st2:
            st.markdown(f"<h3 style='color: #ef4444; margin:0;'>{res['wrong']}</h3><label style='color:#64748b;'>Salah</label>", unsafe_allow_html=True)
        with col_st3:
            st.markdown(f"<h3 style='color: #f59e0b; margin:0;'>{res['empty']}</h3><label style='color:#64748b;'>Kosong</label>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- SECTION PEMBAHASAN ---
        st.markdown("<h3 style='color: var(--text-main); margin-bottom: 20px;'>📖 Pembahasan Hasil Ujian</h3>", unsafe_allow_html=True)
        user_answers = res.get("answers", {})
        for i, q in enumerate(QUESTIONS):
            q_id = str(q["id"])
            user_ans = user_answers.get(q_id, "")
            correct_ans = ANSWER_KEY.get(q_id, "")
            
            is_correct = user_ans == correct_ans
            status_icon = "✅ Benar" if is_correct else "❌ Salah"
            if not user_ans:
                status_icon = "⚠️ Kosong"
                user_ans = "Tidak dijawab"
                
            with st.expander(f"Soal {i+1} — {status_icon}"):
                st.markdown(f"**Pertanyaan:**<br>{q['text']}", unsafe_allow_html=True)
                st.markdown(f"**Jawaban Anda:** {user_ans}<br>**Kunci Jawaban:** {correct_ans}", unsafe_allow_html=True)
                st.info("💡 **Pembahasan:**\nPembahasan untuk soal ini belum tersedia dari dosen pengampu.")
                
        st.markdown("---")
        
        if st.button("Keluar & Tutup Aplikasi", use_container_width=True, type="primary"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
