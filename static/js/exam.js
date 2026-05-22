// --- 1. CONFIG & EVALUATION POOL ---
const totalQuestions = 30;
let currentQuestion = 1;
let answers = {};
let doubts = {};

let strikes = 0;
let isExamActive = false;
let isWarningOpen = false;

// Face Recognition Globals
let isFaceModelsLoaded = false;
let baselineDescriptor = null;
let faceCheckInterval = null;
let isCameraInitializing = false;

async function loadFaceModels() {
    try {
        const cdnUrl = 'https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@master/weights';
        await faceapi.nets.tinyFaceDetector.loadFromUri(cdnUrl);
        await faceapi.nets.faceLandmark68Net.loadFromUri(cdnUrl);
        await faceapi.nets.faceRecognitionNet.loadFromUri(cdnUrl);
        isFaceModelsLoaded = true;
        console.log("AI Face Models loaded successfully from CDN!");
    } catch (err) {
        console.error("Failed to load Face AI models from CDN, falling back to local...", err);
        try {
            await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');
            await faceapi.nets.faceLandmark68Net.loadFromUri('/static/models');
            await faceapi.nets.faceRecognitionNet.loadFromUri('/static/models');
            isFaceModelsLoaded = true;
            console.log("AI Face Models loaded successfully from local fallback!");
        } catch (localErr) {
            console.error("Failed to load Face AI models from local fallback", localErr);
        }
    }
}

let timeRemaining = 90 * 60; // 90 Menit
let timerInterval;

const questionsData = [
    {
        id: 1,
        text: "Berdasarkan data praktikum analisis konduktometri yang telah dikalibrasi ulang, berapakah nilai konduktivitas yang paling akurat untuk larutan tawas (alum) pada konsentrasi 1M dan 3M?",
        options: [
            "1M: 2,59 mS dan 3M: 2,97 mS",
            "1M: 2,54 mS dan 3M: 2,42 mS",
            "1M: 1,95 mS dan 3M: 2,10 mS",
            "1M: 3,10 mS dan 3M: 3,50 mS",
            "1M: 2,42 mS dan 3M: 2,54 mS"
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 2,
        text: "Dalam Teori Orbital Molekul Hückel (HMO) terapan pada sistem konjugasi, fungsi gelombang dibangun dari kombinasi linear orbital atom. Manakah dari berikut ini yang merupakan asumsi dasar metode HMO?",
        options: [
            "Integral tumpang tindih (overlap integral) bernilai 1 untuk semua atom yang berdekatan.",
            "Interaksi elektron-elektron diperhitungkan secara eksplisit dalam Hamiltonian.",
            "Integral resonansi (β) diasumsikan bernilai nol untuk atom-atom yang tidak berikatan langsung.",
            "Energi tolakan inti diabaikan sepenuhnya dalam perhitungan energi total molekul.",
            "Integral Coulomb (α) memiliki nilai yang berbeda untuk setiap atom karbon dalam cincin benzena."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 3,
        text: "Solusi persamaan Schrödinger untuk 'partikel dalam kotak 1D' menunjukkan kuantisasi energi. Mengapa energi tingkat dasar (ground state, n=1) untuk sistem ini tidak pernah bernilai nol?",
        options: [
            "Karena partikel memiliki massa yang tak terhingga.",
            "Sesuai dengan Prinsip Ketidakpastian Heisenberg, ketidakpastian posisi (Δx) yang terbatas menyebabkan ketidakpastian momentum (Δp) > 0, sehingga energi kinetik > 0.",
            "Karena fungsi gelombang pada n=1 adalah garis lurus konstan.",
            "Karena energi potensial di dalam kotak bernilai tak terhingga.",
            "Kondisi batas (boundary conditions) mengharuskan amplitudo probabilitas bernilai maksimum di dinding kotak."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 4,
        text: "Tinjau proses ekspansi isotermal reversibel dari suatu gas ideal. Pernyataan manakah yang benar mengenai perubahan termodinamikanya?",
        options: [
            "Perubahan energi dalam (ΔU) bernilai nol dan q = -w.",
            "Sistem melepaskan panas ke lingkungan.",
            "Perubahan entalpi (ΔH) bernilai negatif.",
            "Kerja (w) yang dilakukan oleh sistem bernilai positif.",
            "Perubahan entropi lingkungan (ΔS_surr) bernilai positif."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 5,
        text: "Peluruhan isotop radioaktif mengikuti kinetika reaksi orde pertama. Jika waktu paruh (t1/2) isotop tersebut adalah 20 menit, berapakah fraksi isotop yang tersisa setelah 1 jam?",
        options: [
            "1/2",
            "1/3",
            "1/6",
            "1/8",
            "1/16"
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 6,
        text: "Pada spektroskopi Resonansi Magnetik Inti (NMR) 1H, proton yang terikat pada karbon aldehida (R-CHO) biasanya muncul pada rentang pergeseran kimia (chemical shift, δ) yang mana?",
        options: [
            "0.9 - 1.5 ppm",
            "9.0 - 10.0 ppm",
            "6.5 - 8.0 ppm",
            "3.5 - 4.5 ppm",
            "11.0 - 12.0 ppm"
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 7,
        text: "Reaksi substitusi nukleofilik unimolekuler (SN1) memiliki karakteristik khusus dibandingkan SN2. Manakah dari sifat berikut yang PALING tepat menggambarkan reaksi SN1?",
        options: [
            "Laju reaksi bergantung pada konsentrasi substrat dan nukleofil.",
            "Reaksi berlangsung dalam satu tahap tanpa pembentukan intermediet.",
            "Menghasilkan campuran rasemat jika substrat adalah karbon kiral.",
            "Laju reaksi meningkat seiring dengan berkurangnya kepolaran pelarut.",
            "Hanya terjadi pada alkil halida primer."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 8,
        text: "Dalam elektrokimia, Persamaan Nernst sangat fundamental untuk menentukan potensial sel. Persamaan Nernst menghubungkan potensial sel terukur dengan...",
        options: [
            "Potensial sel standar dan kuosien reaksi (Q) dari spesi elektroaktif.",
            "Hanya suhu dan konstanta Faraday.",
            "Laju transfer elektron pada permukaan elektroda.",
            "Energi aktivasi dari reaksi redoks selular.",
            "Konduktivitas molar ekuivalen dari larutan elektrolit."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 9,
        text: "Di dalam mekanika kuantum kimiawi, Operator Hamiltonian (Ĥ) beroperasi pada fungsi gelombang (Ψ) suatu sistem. Nilai eigen (eigenvalue) yang dihasilkan dari operasi ĤΨ = EΨ merepresentasikan...",
        options: [
            "Momentum sudut orbital partikel.",
            "Probabilitas densitas elektron.",
            "Energi total observabel dari sistem tersebut.",
            "Vektor posisi rata-rata partikel.",
            "Fungsi kerapatan spin."
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 10,
        text: "Menurut Teori Medan Kristal (Crystal Field Theory), ketika ligan mendekati ion logam transisi dalam geometri oktahedral, terjadi pembelahan (splitting) orbital d. Orbital mana yang mengalami kenaikan energi paling besar (berada pada tingkat eg)?",
        options: [
            "dxy dan dyz",
            "dxz dan dxy",
            "dz^2 dan dxy",
            "dx^2-y^2 dan dz^2",
            "dyz dan dx^2-y^2"
        ],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 11,
        text: "Dalam spektrometri massa, puncak dasar (base peak) didefinisikan sebagai...",
        options: ["Puncak ion molekul", "Puncak dengan kelimpahan relatif 100%", "Puncak isotop M+1", "Puncak dengan massa terbesar", "Puncak fragmen kation radikal"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 12,
        text: "Manakah dari berikut ini yang merupakan sifat koligatif larutan?",
        options: ["Densitas", "Tegangan permukaan", "Penurunan tekanan uap", "Indeks bias", "Viskositas"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 13,
        text: "Hukum Raoult menyatakan bahwa tekanan uap pelarut dalam larutan ideal...",
        options: ["Berbanding lurus dengan fraksi mol pelarut", "Berbanding lurus dengan molalitas zat terlarut", "Berbanding terbalik dengan suhu absolut", "Tidak bergantung pada konsentrasi", "Sama dengan tekanan osmotik"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 14,
        text: "Dalam titrasi asam-basa, titik ekuivalen adalah saat...",
        options: ["Indikator berubah warna", "pH larutan mencapai 7", "Laju reaksi maju dan mundur sama", "Mol asam tepat habis bereaksi dengan mol basa", "Titrasi dihentikan"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 15,
        text: "Pada sel galvanik, setengah reaksi oksidasi terjadi pada...",
        options: ["Anoda", "Katoda", "Jembatan garam", "Elektrolit", "Kabel luar"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 16,
        text: "Enzim bertindak sebagai biokatalis dengan cara...",
        options: ["Menggeser kesetimbangan ke kanan", "Meningkatkan perubahan entalpi", "Menurunkan energi aktivasi reaksi", "Meningkatkan energi kinetik rata-rata", "Mengubah mekanisme termodinamika"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 17,
        text: "Isomer optik (enantiomer) dapat dipisahkan menggunakan teknik...",
        options: ["Distilasi fraksional", "Kromatografi kiral", "Ekstraksi pelarut cair-cair", "Kristalisasi sederhana", "Sublimasi"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 18,
        text: "Menurut teori asam-basa Lewis, asam adalah...",
        options: ["Donor proton (H+)", "Akseptor proton", "Donor pasangan elektron", "Akseptor pasangan elektron", "Donor ion OH-"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 19,
        text: "Persamaan gas ideal (PV = nRT) paling akurat pada kondisi...",
        options: ["Tekanan tinggi dan suhu tinggi", "Tekanan rendah dan suhu tinggi", "Tekanan tinggi dan suhu rendah", "Tekanan rendah dan suhu rendah", "Volume gas mendekati nol"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 20,
        text: "Ikatan hidrogen paling kuat terjadi pada molekul yang mengandung atom hidrogen yang berikatan dengan...",
        options: ["F, O, atau N", "C, H, atau O", "Cl, Br, atau I", "S, P, atau Se", "Logam transisi"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 21,
        text: "Dalam kromatografi cair kinerja tinggi (HPLC), waktu retensi dipengaruhi oleh...",
        options: ["Suhu detektor", "Konsentrasi sampel", "Polaritas fase diam dan fase gerak", "Ketebalan sel aliran", "Tekanan pompa hampa gas"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 22,
        text: "Efek Tyndall merupakan karakteristik utama dari...",
        options: ["Larutan sejati", "Sistem koloid", "Suspensi kasar", "Emulsi padat", "Aerosol cair"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 23,
        text: "Pada reaksi eksotermik, nilai perubahan entalpi (ΔH) adalah...",
        options: ["Negatif", "Positif", "Nol", "Tak terhingga", "Bergantung katalis"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 24,
        text: "Polimer yang terbentuk dari monomer asam amino melalui ikatan peptida adalah...",
        options: ["Polisakarida", "DNA/RNA", "Lipid", "Protein", "Nilon"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 25,
        text: "Senyawa aromatik mematuhi aturan Hückel jika memiliki elektron pi sebanyak...",
        options: ["2n", "4n", "4n + 2", "4n - 2", "2n + 4"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 26,
        text: "Konfigurasi elektron keadaan dasar untuk ion Fe3+ (Z=26) adalah...",
        options: ["[Ar] 4s2 3d3", "[Ar] 3d5", "[Ar] 4s1 3d4", "[Ar] 3d6", "[Ar] 4s2 3d4"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 27,
        text: "Dalam termodinamika, entropi (S) adalah ukuran dari...",
        options: ["Kandungan panas total", "Energi bebas sistem", "Laju reaksi termal", "Ketidakteraturan atau keacakan sistem", "Kapasitas kalor sistem"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 28,
        text: "Prinsip Le Chatelier menyatakan bahwa...",
        options: ["Sistem kesetimbangan akan bergeser untuk meminimalkan gangguan", "Massa zat sebelum dan sesudah reaksi sama", "Energi tidak dapat diciptakan atau dimusnahkan", "Tekanan total sama dengan jumlah tekanan parsial", "Semua gas ideal berkelakuan sama"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 29,
        text: "Dalam reaksi redoks, zat yang mengalami penurunan bilangan oksidasi bertindak sebagai...",
        options: ["Reduktor", "Katalis", "Oksidator", "Indikator", "Intermediet"],
        keys: ['A', 'B', 'C', 'D', 'E']
    },
    {
        id: 30,
        text: "Metode titrasi Karl Fischer digunakan secara spesifik untuk menentukan kadar...",
        options: ["Asam", "Air", "Basa", "Klorida", "Logam berat"],
        keys: ['A', 'B', 'C', 'D', 'E']
    }
];

// Safe fullscreen wrapper function to prevent cross-browser crashes (Safari/iOS/Edge)
function safeEnterFullscreen() {
    try {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen().catch(err => {
                console.warn("Standard requestFullscreen rejected:", err);
            });
        } else if (elem.webkitRequestFullscreen) {
            try {
                const res = elem.webkitRequestFullscreen();
                if (res && typeof res.catch === 'function') {
                    res.catch(err => console.warn("Webkit requestFullscreen rejected:", err));
                }
            } catch (err) {
                console.warn("Webkit requestFullscreen synchronous error:", err);
            }
        } else if (elem.msRequestFullscreen) {
            try {
                const res = elem.msRequestFullscreen();
                if (res && typeof res.catch === 'function') {
                    res.catch(err => console.warn("MS requestFullscreen rejected:", err));
                }
            } catch (err) {
                console.warn("MS requestFullscreen synchronous error:", err);
            }
        }
    } catch (e) {
        console.error("Fullscreen API invocation failed completely:", e);
    }
}

// --- 2. LAYOUT LIFECYCLE ---
window.addEventListener('DOMContentLoaded', () => {
    const nim = sessionStorage.getItem('cbt_user_nim_v3');
    const nama = sessionStorage.getItem('cbt_user_nama_v3');
    if(!nim) {
        window.location.href = '/';
        return;
    }
    const displayName = nama ? `${nim} | ${nama}` : nim;
    document.getElementById('gated-nim').innerText = displayName;
    document.getElementById('display-nim').innerText = "Identitas: " + displayName;
    
    loadFaceModels(); // Load AI models in background
    
    initSecurityFeatures();
});

function initSecurityFeatures() {
    // Disable Right Click
    document.addEventListener('contextmenu', e => e.preventDefault());
    
    // Disable Copy, Paste, Cut
    document.addEventListener('copy', e => { e.preventDefault(); alert('Tindakan dilarang!'); });
    document.addEventListener('paste', e => { e.preventDefault(); alert('Tindakan dilarang!'); });
    document.addEventListener('cut', e => { e.preventDefault(); alert('Tindakan dilarang!'); });
    
    // Disable Keyboard Shortcuts (Ctrl+C, Ctrl+V, F12)
    document.addEventListener('keydown', e => {
        if (e.key === 'F12' || (e.ctrlKey && ['c', 'v', 'x', 'p', 's', 'u'].includes(e.key.toLowerCase()))) {
            e.preventDefault();
            monitorCheatViolation();
        }
    });
}

// Remove watermark initialization

function startWebcamProctor() {
    const video = document.getElementById('webcam-proctor');
    isCameraInitializing = true;
    
    // Stop any existing stream tracks to avoid hardware lock/resource leak
    if (video && video.srcObject) {
        try {
            video.srcObject.getTracks().forEach(track => track.stop());
        } catch (e) {
            console.error("Error stopping tracks", e);
        }
        video.srcObject = null;
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            isCameraInitializing = false;
            document.getElementById('camera-modal').classList.add('hidden');
            
            const btn = document.getElementById('btn-retry-camera');
            if (btn) {
                btn.disabled = false;
                btn.innerText = "Aktifkan & Coba Lagi";
            }
            
            // Re-request fullscreen if the browser kicked us out during the permission dialog
            const isCurrentlyFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
            if (!isCurrentlyFullscreen) {
                safeEnterFullscreen();
            }

            if (video) {
                video.srcObject = stream;
                // Explicitly play video to handle iOS and desktop Safari/Firefox autoplay policies
                video.play().catch(err => {
                    console.error("Error playing video stream:", err);
                });
                
                // Start Face Recognition Check when video plays
                video.removeEventListener('play', handleVideoPlayV3);
                video.addEventListener('play', handleVideoPlayV3);
            }
        })
        .catch(err => {
            isCameraInitializing = false;
            console.error("Webcam access denied or unavailable", err);
            showCameraErrorV3(err);
        });
    } else {
        isCameraInitializing = false;
        console.error("Webcam API not supported in this browser context (likely non-secure HTTP context).");
        showCameraErrorV3("SecurityError");
    }
}

async function handleVideoPlayV3() {
    const video = document.getElementById('webcam-proctor');
    if (!isFaceModelsLoaded) await loadFaceModels();
    
    console.log("Scanning baseline face...");
    // Wait 3 seconds for camera to stabilize
    setTimeout(async () => {
        if (!video.srcObject) return; // Terminated early
        const detection = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();
        if (detection) {
            baselineDescriptor = detection.descriptor;
            console.log("✅ Wajah Pemilik Akun terekam!");
            startContinuousFaceCheck(video);
        } else {
            console.log("⚠️ Wajah tidak terdeteksi saat inisiasi.");
            startContinuousFaceCheck(video); // Tetap mulai untuk mendeteksi nanti
        }
    }, 3000);
}

function showCameraErrorV3(error) {
    const btn = document.getElementById('btn-retry-camera');
    if (btn) {
        btn.disabled = false;
        btn.innerText = "Aktifkan & Coba Lagi";
    }

    const modal = document.getElementById('camera-modal');
    if (!modal) return;
    
    const titleEl = modal.querySelector('h2');
    const descEl = modal.querySelector('p');

    // Normalize error name or message across different browsers (Chrome, Firefox, Safari, Edge)
    let errorName = "";
    if (typeof error === 'string') {
        errorName = error;
    } else if (error && error.name) {
        errorName = error.name;
    } else if (error && error.message) {
        const msg = error.message.toLowerCase();
        if (msg.includes('permission') || msg.includes('allow') || msg.includes('denied')) {
            errorName = 'NotAllowedError';
        } else if (msg.includes('not found') || msg.includes('devices') || msg.includes('found') || msg.includes('source')) {
            errorName = 'NotFoundError';
        } else if (msg.includes('readable') || msg.includes('track') || msg.includes('use') || msg.includes('busy') || msg.includes('concurrent')) {
            errorName = 'NotReadableError';
        } else if (msg.includes('security') || msg.includes('https') || msg.includes('secure')) {
            errorName = 'SecurityError';
        }
    }

    let title = "Akses Kamera Dibutuhkan";
    let desc = "Aplikasi ini memerlukan akses ke kamera laptop/PC Anda untuk pengawasan ujian terstandarisasi.";

    if (errorName === 'NotAllowedError' || errorName === 'PermissionDeniedError') {
        title = "Izin Kamera Ditolak";
        desc = "Izin akses kamera diblokir atau ditolak. Silakan izinkan melalui menu perizinan browser Anda.";
    } else if (errorName === 'NotFoundError' || errorName === 'DevicesNotFoundError' || errorName === 'OverconstrainedError') {
        title = "Kamera Tidak Ditemukan";
        desc = "Sistem tidak mendeteksi adanya perangkat kamera (webcam) terhubung atau aktif.";
    } else if (errorName === 'NotReadableError' || errorName === 'TrackStartError' || errorName === 'AbortError') {
        title = "Kamera Sedang Digunakan";
        desc = "Kamera sedang dikunci oleh aplikasi lain (seperti Zoom, OBS, Meet, atau tab lain).";
    } else if (errorName === 'SecurityError') {
        title = "Koneksi Tidak Aman (HTTPS)";
        desc = "Akses kamera diblokir oleh keamanan browser karena halaman tidak diakses via HTTPS / localhost.";
    }

    if (titleEl) titleEl.innerText = title;
    if (descEl) descEl.innerText = desc;

    // Auto-switch troubleshooting tab based on browser and security context
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const isHttps = window.location.protocol === 'https:';
    
    if ((!isHttps && !isLocalhost) || errorName === 'SecurityError') {
        switchTroubleshootTab('lan');
    } else {
        const userAgent = navigator.userAgent.toLowerCase();
        if (userAgent.includes('safari') && !userAgent.includes('chrome') && !userAgent.includes('android')) {
            switchTroubleshootTab('safari');
        } else if (userAgent.includes('firefox')) {
            switchTroubleshootTab('firefox');
        } else {
            switchTroubleshootTab('chrome');
        }
    }

    modal.classList.remove('hidden');
}

function retryCameraAccessV3() {
    const btn = document.getElementById('btn-retry-camera');
    if (btn) {
        btn.disabled = true;
        btn.innerText = "Menghubungkan Kamera...";
    }

    // Attempt to re-enter fullscreen safely
    safeEnterFullscreen();

    // Hide modal and initialize camera with a short delay to prevent instant visual flashes
    setTimeout(() => {
        const modal = document.getElementById('camera-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        isCameraInitializing = true;
        startWebcamProctor();
    }, 600);
}

function startContinuousFaceCheck(video) {
    if (faceCheckInterval) clearInterval(faceCheckInterval);
    
    faceCheckInterval = setInterval(async () => {
        if (!isExamActive || isWarningOpen) return;
        
        const detection = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();
        
        if (!detection) {
            console.log("Wajah tidak terlihat di kamera.");
            return;
        }
        
        if (baselineDescriptor) {
            const distance = faceapi.euclideanDistance(baselineDescriptor, detection.descriptor);
            console.log("Face Distance:", distance);
            
            // Jarak > 0.55 biasanya berarti orang yang berbeda
            if (distance > 0.55) {
                alert("🚨 PERINGATAN SISTEM: Wajah orang lain terdeteksi! Mengganti joki saat ujian sangat dilarang.");
                monitorCheatViolation();
            }
        } else {
            // Jika sebelumnya gagal merekam baseline, rekam sekarang
            baselineDescriptor = detection.descriptor;
            console.log("Baseline face recorded on fallback.");
        }
    }, 4000); // Cek setiap 4 detik
}

function initGrid() {
    const grid = document.getElementById('grid-nav');
    grid.innerHTML = '';
    for(let i = 1; i <= totalQuestions; i++) {
        const btn = document.createElement('div');
        btn.className = 'nav-item';
        btn.innerText = i;
        btn.id = `nav-${i}`;
        btn.onclick = () => renderQuestion(i);
        grid.appendChild(btn);
    }
    updateGridColors();
}

function renderQuestion(qNum) {
    currentQuestion = qNum;
    const q = questionsData[qNum - 1];
    
    document.getElementById('q-num').innerText = qNum;
    document.getElementById('q-total').innerText = totalQuestions;
    document.getElementById('q-text').innerText = q.text;

    const optsContainer = document.getElementById('options-container');
    optsContainer.innerHTML = '';
    
    q.options.forEach((optText, index) => {
        const key = q.keys[index];
        const optDiv = document.createElement('div');
        optDiv.className = `option ${answers[qNum] === key ? 'selected' : ''}`;
        optDiv.onclick = () => selectOption(key);
        optDiv.innerHTML = `
            <span class="option-key">${key}</span>
            <span>${optText}</span>
        `;
        optsContainer.appendChild(optDiv);
    });

    updateGridColors();
}

function selectOption(key) {
    if(!isExamActive) return;
    answers[currentQuestion] = key;
    doubts[currentQuestion] = false; 
    renderQuestion(currentQuestion);
    updateProgressBar();
}

function toggleDoubt() {
    if(!isExamActive) return;
    doubts[currentQuestion] = !doubts[currentQuestion];
    updateGridColors();
}

function navQuestion(dir) {
    if(dir === 'prev' && currentQuestion > 1) renderQuestion(currentQuestion - 1);
    if(dir === 'next' && currentQuestion < totalQuestions) renderQuestion(currentQuestion + 1);
}

function updateGridColors() {
    for(let i = 1; i <= totalQuestions; i++) {
        const btn = document.getElementById(`nav-${i}`);
        if(!btn) continue;
        
        btn.className = 'nav-item'; 
        if (i === currentQuestion) btn.classList.add('active');
        
        if (doubts[i]) {
            btn.classList.add('doubt');
        } else if (answers[i]) {
            btn.classList.add('answered');
        }
    }
}

function updateProgressBar() {
    const answeredCount = Object.keys(answers).filter(qNum => answers[qNum]).length;
    const progressPercent = (answeredCount / totalQuestions) * 100;
    const pb = document.getElementById('exam-progress-bar');
    if (pb) {
        pb.style.width = `${progressPercent}%`;
    }
}

function switchTroubleshootTab(tabName) {
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(el => el.classList.remove('active'));
    
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(el => el.classList.remove('active'));
    
    const targetContent = document.getElementById(`content-${tabName}`);
    const targetButton = document.getElementById(`btn-tab-${tabName}`);
    if (targetContent) targetContent.classList.add('active');
    if (targetButton) targetButton.classList.add('active');
}

// --- 3. DUAL-INPUT KEYBOARD CAPTURE ---
document.addEventListener('keydown', (e) => {
    if(!isExamActive || isWarningOpen) return;
    const key = e.key.toUpperCase();
    
    if (['A', 'B', 'C', 'D', 'E'].includes(key)) {
        selectOption(key);
    } else if (e.key === 'ArrowRight') {
        navQuestion('next');
    } else if (e.key === 'ArrowLeft') {
        navQuestion('prev');
    }
});

// --- 4. SECURE TIMER ---
function startTimer() {
    timerInterval = setInterval(() => {
        timeRemaining--;
        let h = Math.floor(timeRemaining / 3600);
        let m = Math.floor((timeRemaining % 3600) / 60);
        let s = timeRemaining % 60;
        
        document.getElementById('timer').innerText = 
            `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        
        if(timeRemaining <= 0) {
            executeSubmitV3(true, "Waktu Durasi Ujian Telah Habis Secara Resmi!");
        }
    }, 1000);
}

// --- 5. STRICT PROCTORING / TAB-LOCK SENSORS ---
function triggerStartExamV3() {
    // Request fullscreen safely
    safeEnterFullscreen();
    
    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('topbar').classList.remove('hidden');
    document.getElementById('main-layout').classList.remove('hidden');
    
    isExamActive = true;
    startWebcamProctor();
    initGrid();
    renderQuestion(1);
    startTimer();
    updateProgressBar();
}

function monitorCheatViolation() {
    // Do NOT trigger strikes if camera is initializing, camera error modal is open, exam is inactive, or warning modal is already open.
    const cameraModal = document.getElementById('camera-modal');
    const isCameraModalOpen = cameraModal && !cameraModal.classList.contains('hidden');
    if(!isExamActive || isWarningOpen || isCameraInitializing || isCameraModalOpen) return;
    
    strikes++;
    isWarningOpen = true;
    const nim = sessionStorage.getItem('cbt_user_nim_v3') || 'Anonim';

    // Ping Real-Time ke REST Server Flask
    fetch('/api/log-strike', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nim: nim, strikes: strikes })
    }).catch(err => console.error("Logger API Error:", err));

    if(strikes >= 4) {
        executeSubmitV3(true, "DISKUALIFIKASI OTOMATIS: Anda melanggar aturan kunci jendela ujian sebanyak 4 kali.");
        return;
    }

    document.getElementById('strike-count').innerText = strikes;
    document.getElementById('warning-modal').classList.remove('hidden');
}

function closeWarningModalV3() {
    const isCurrentlyFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
    if (!isCurrentlyFullscreen) {
        safeEnterFullscreen();
    }
    document.getElementById('warning-modal').classList.add('hidden');
    setTimeout(() => { isWarningOpen = false; }, 500); 
}

// Subskripsi Window Event Listener
document.addEventListener('visibilitychange', () => {
    if (document.hidden) monitorCheatViolation();
});
window.addEventListener('blur', () => {
    monitorCheatViolation();
});

const handleFullscreenChange = () => {
    const isCurrentlyFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
    if (!isCurrentlyFullscreen && isExamActive) {
        monitorCheatViolation();
    }
};
document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('msfullscreenchange', handleFullscreenChange);

// --- 6. AGGREGATION & GRAPHICAL SCREEN ---
function triggerConfirmSubmitV3() {
    document.getElementById('confirm-modal').classList.remove('hidden');
}

function closeConfirmModalV3() {
    document.getElementById('confirm-modal').classList.add('hidden');
}

function executeSubmitV3(isForced = false, message = "") {
    isExamActive = false;
    clearInterval(timerInterval);
    
    // Stop Webcam Proctoring to respect user privacy and save battery/CPU resources once submitted
    const video = document.getElementById('webcam-proctor');
    if (video && video.srcObject) {
        try {
            video.srcObject.getTracks().forEach(track => track.stop());
        } catch (e) {
            console.error("Error stopping tracks on submit", e);
        }
        video.srcObject = null;
    }
    if (faceCheckInterval) {
        clearInterval(faceCheckInterval);
        faceCheckInterval = null;
    }
    
    document.getElementById('warning-modal').classList.add('hidden');
    document.getElementById('confirm-modal').classList.add('hidden');
    document.getElementById('camera-modal').classList.add('hidden'); // Ensure camera modal is hidden
    
    const nim = sessionStorage.getItem('cbt_user_nim_v3') || 'Anonim';
    let statusUjian = isForced ? "Disikualifikasi" : "Selesai Normal";

    const payload = {
        nim: nim,
        answers: answers,
        pelanggaran: strikes,
        sisaWaktu: timeRemaining,
        status_ujian: statusUjian
    };

    fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(async res => {
        const isJson = res.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await res.json() : null;
        if (!res.ok) {
            const errorMsg = (data && data.error) ? data.error : 'Terjadi kesalahan internal server';
            throw new Error(errorMsg);
        }
        return data;
    })
    .then(data => {
        renderResultDashboardV3(data, isForced, message);
    })
    .catch(err => {
        console.error("Submit Error:", err);
        alert("Gagal mengamankan lembar jawaban: " + (err.message || "Hubungi pengawas."));
    });
}

function renderResultDashboardV3(data, isForced, message) {
    document.getElementById('topbar').classList.add('hidden');
    document.getElementById('main-layout').classList.add('hidden');
    document.getElementById('result-screen').classList.remove('hidden');

    const msgStatus = document.getElementById('result-message-status');
    if(isForced) {
        msgStatus.innerHTML = `<strong style="color:var(--danger)">AKSES DIKUNCI SISTEM</strong><br>${message}`;
    } else {
        msgStatus.innerHTML = "Sesi ujian Anda telah terekam penuh di server akademik.";
    }

    // Tampilkan Predikat Kelulusan dari Server
    document.getElementById('predicate-display').innerText = "Predikat Kinerja: " + data.predicate;

    // Linear Counter Animation
    let finalScore = data.score;
    let scoreDisplay = 0;
    const scoreElement = document.getElementById('animated-score');
    
    if(finalScore > 0) {
        let animInterval = setInterval(() => {
            if(scoreDisplay >= finalScore) {
                clearInterval(animInterval);
                scoreElement.innerText = finalScore;
            } else {
                scoreDisplay++;
                scoreElement.innerText = scoreDisplay;
            }
        }, 15);
    } else {
        scoreElement.innerText = "0";
    }

    document.getElementById('stat-correct').innerText = data.correct;
    document.getElementById('stat-wrong').innerText = data.wrong;
    document.getElementById('stat-empty').innerText = data.empty;
}

function finishAndLogoutV3() {
    // Stop Webcam
    const video = document.getElementById('webcam-proctor');
    if(video && video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
    }
    if (faceCheckInterval) clearInterval(faceCheckInterval);
    
    sessionStorage.clear();
    window.location.href = '/';
}
