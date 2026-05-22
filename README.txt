========================================================================
SISTEM CBT WEB PRODUCTION READY VERSI 3 - ULTIMATE PROCTORING
========================================================================

Pembaruan besar pada arsitektur pengawasan (Proctoring Engine) dan struktur data 
di sisi server untuk aplikasi Computer Based Test (CBT) Full-Stack Flask Anda.

FITUR BARU & UTAMA DI VERSI 3:
1. UI/UX Refinement: Menggunakan Ultra Dark Theme Cyber-Aesthetic dengan 
   Glassmorphism blur berdensitas tinggi untuk mengurangi fatigue pada mata.
2. Predicate Engine: Backend server kini otomatis mengevaluasi rentang nilai 
   dan memberikan predikat kelulusan resmi (Cum Laude, Memuaskan, Kurang).
3. Evaluasi Kimia Komprehensif: Menggunakan 10 bank soal Kimia tingkat tinggi 
   (termasuk HMO, Persamaan Schrödinger, Elektrokimia, dan Kalibrasi Tawas Alum).
4. Dual-Input Controls: Navigasi keyboard ultra-responsif (Arrow Kanan/Kiri) 
   dan seleksi opsi (A-E) terisolasi penuh dari intervensi modal.
5. Secure Anti-Cheat (Visibility API + Screen Blur): Log deteksi kecurangan 
   langsung tersinkronisasi ke server Python saat kejadian berlangsung.
6. Session Eraser: Tombol logout membersihkan sisa data pendaftaran sesi di browser.

------------------------------------------------------------------------
CARA MENJALANKAN DI DESKTOP / LAPTOP:
------------------------------------------------------------------------
1. Pastikan lingkungan perangkat Anda telah memiliki Python 3.
2. Buka terminal atau command prompt tepat di dalam folder proyek versi 3 ini.
3. Instal framework Flask jika belum terinstal:
   pip install Flask
4. Jalankan aplikasi web server:
   python app.py
5. Akses portal login melalui tautan web browser Anda:
   http://127.0.0.1:5000

------------------------------------------------------------------------
SIMULASI RESPONSIF VIA HP (ANDROID / IOS):
------------------------------------------------------------------------
Sistem antarmuka didesain adaptif penuh di layar sentuh mobile webview:
1. Pastikan laptop server dan ponsel Anda tersambung di Wi-Fi lokal yang sama.
2. Ambil IP Lokal dari komputer Anda (Windows: `ipconfig` / macOS: `ifconfig`).
   Misalnya didapat IP: 192.168.1.12
3. Pada browser mobile Anda (Chrome/Safari), arahkan ke alamat IP tersebut:
   http://192.168.1.12:5000
4. Coba lakukan minimasi browser atau usap layar ke beranda untuk menguji 
   keandalan pop-up sistem anti-cheat.
   
========================================================================
SISTEM CBT WEB PRODUCTION READY VERSI LENGKAP - REGISTRATION & AUTH
========================================================================

Versi lengkap mencakup sistem autentikasi yang fungsional (simulasi database memori).
Kini, mahasiswa diwajibkan untuk mendaftar akun terlebih dahulu sebelum login dan 
masuk ke ruang ujian CBT.

FITUR BARU DI VERSI INI:
1. Pendaftaran Akun Baru (/register): Mahasiswa membuat profil dengan memasukkan 
   NIM, Nama Lengkap, dan Kata Sandi.
2. Validasi Login yang Ketat: Login membutuhkan kombinasi NIM, Kata Sandi, dan 
   Token Ujian yang valid.
3. Token Aktif: Telah dikunci dengan token 'KIMIA2026' di sistem backend.
4. Data Terintegrasi: Nama lengkap yang didaftarkan akan ditampilkan langsung
   di dashboard layar CBT untuk verifikasi identitas (Nama & NIM).

------------------------------------------------------------------------
CARA UJI COBA APLIKASI:
------------------------------------------------------------------------
1. Ekstrak folder proyek ini.
2. Buka Terminal / CMD, instal Flask (jika belum):
   pip install Flask
3. Jalankan server:
   python app.py
4. Buka Browser (http://127.0.0.1:5000).
5. ALUR PENGGUNAAN:
   - Klik "Belum punya akun? Daftar di sini".
   - Masukkan NIM, Nama Anda, dan Password. Klik Daftarkan Akun.
   - Anda akan dialihkan kembali ke halaman Login otomatis.
   - Masukkan NIM dan Password yang baru Anda buat.
   - Masukkan Token Ujian: KIMIA2026
   - Klik Otorisasi & Masuk!
