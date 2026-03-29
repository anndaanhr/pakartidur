from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Data Gejala dan Penyakit
SYMPTOMS = [
    {"id": "G01", "text": "Apakah Anda merasa sulit jatuh tertidur pada malam hari?"},
    {"id": "G02", "text": "Apakah Anda sering terbangun di tengah malam dan sulit tidur kembali?"},
    {"id": "G03", "text": "Apakah Anda sering bangun terlalu awal di pagi hari dan tidak bisa tidur lagi?"},
    {"id": "G04", "text": "Apakah pada siang hari Anda merasa sangat kelelahan walau sudah merasa tidur cukup di malam hari?"},
    {"id": "G05", "text": "Apakah Anda pernah diberitahu orang lain bahwa Anda mendengkur dengan sangat keras?"},
    {"id": "G06", "text": "Apakah Anda pernah berhenti bernapas sesaat, mendengus, atau tersedak saat sedang tidur?"},
    {"id": "G07", "text": "Apakah Anda sering terbangun dengan keadaan mulut sangat kering atau sakit tenggorokan?"},
    {"id": "G08", "text": "Apakah Anda merasa sangat amat mengantuk di siang hari hingga rasanya tidak tertahankan?"},
    {"id": "G09", "text": "Apakah Anda pernah tiba-tiba jatuh tertidur di siang hari, bahkan saat sedang beraktivitas santai?"},
    {"id": "G10", "text": "Apakah otot-otot Anda sering tiba-tiba terasa lemas (mengulai) sesaat setelah tertawa kaget, atau merasa emosional?"},
    {"id": "G11", "text": "Apakah Anda pernah merasa tidak bisa bergerak sama sekali (ketindihan) sesaat setelah bangun tidur atau mau tidur?"},
    {"id": "G12", "text": "Apakah Anda merasakan dorongan yang sangat kuat dan gelisah untuk menggerakan kaki saat berbaring/santai?"},
    {"id": "G13", "text": "Apakah ada rasa tidak nyaman (seperti kesemutan/menjalar) di dalam kaki Anda terutama pada malam hari?"},
    {"id": "G14", "text": "Apakah jam biologis Anda bergeser sehingga biasanya baru bisa tidur jauh larut malam (misal setelah jam 2 pagi)?"},
    {"id": "G15", "text": "Apakah Anda sangat amat kesulitan untuk bisa bangun pagi di jam produktif yang umum?"}
]

DIAGNOSES = {
    "P01": {
        "name": "Insomnia Klinis", 
        "description": "Kondisi di mana Anda mengalami kesulitan yang signifikan untuk memulai atau mempertahankan tidur secara memadai.",
        "advice": "Terapkan 'Sleep Hygiene' (hindari kafein sore, batasi cahaya layar). Jika berlangsung lama, konsultasikan spesialis untuk CBT-I."
    },
    "P02": {
        "name": "Sleep Apnea (Henti Napas Obstruktif)", 
        "description": "Dinding tenggorokan menyempit saat tidur hingga jalan napas tersumbat. Anda berhenti bernapas sesaat dan terbangun kaget tanpa sadar.",
        "advice": "Kondisi ini memerlukan pengawasan karena membebani jantung. Dianjurkan menemui dokter THT (Uji Polysomnography) dan terapi tekanan (CPAP)."
    },
    "P03": {
        "name": "Narkolepsi", 
        "description": "Kelainan sistem saraf otak terhadap siklus bangun-tidur. Menimbulkan serangan tidur ekstrem di siang hari dan kelumpuhan otot tiba-tiba.",
        "advice": "Tidur siang singkat terencana bisa membantu, tangani secara terpadu melalui dokter syaraf (Neurolog) menggunakan intervensi medis khusus."
    },
    "P04": {
        "name": "Restless Legs Syndrome (Sindrom Kaki Gelisah)", 
        "description": "Kelainan saraf sensorik yang menimbulkan dorongan dominan untuk selalu menggerakkan kaki akibat sensasi aneh di dalam saraf kaki saat diam.",
        "advice": "Kurangi kafein & rokok. Sering terkait defisiensi zat besi, sehingga pastikan Anda memeriksa profil darah dasar (Feritin) di rumah sakit."
    },
    "P05": {
        "name": "Delayed Sleep Phase Syndrome (DSPS)", 
        "description": "Sistem pengaturan jam sirkadian alami Anda bergeser tertunda ekstrim layaknya burung hantu, sehingga jadwal tidur-bangun tidak singkron dengan dunia luar.",
        "advice": "Dapatkan paparan cahaya mentari cerah di pagi hari sesegera mungkin saat Anda terbangun. Suplemen melatonin resep dokter juga akan sangat membantu pergeseran bertahap."
    }
}

# Aturan CF (Certainty Factor)
# Bobot CF dari pakar (0.0 - 1.0)
KNOWLEDGE_RULES = {
    "P01": [
        {"symptom_id": "G01", "cf_pakar": 0.8}, # Susah jatuh tertidur sangat indikatif Insomnia
        {"symptom_id": "G02", "cf_pakar": 0.7}, # Terbangun tengah malam indikatif Insomnia
        {"symptom_id": "G03", "cf_pakar": 0.6}, # Bangun terlalu awal
        {"symptom_id": "G04", "cf_pakar": 0.4}  # Merasa amat kelelahan
    ],
    "P02": [
        {"symptom_id": "G05", "cf_pakar": 0.8}, # Mendengkur keras sangat sentral dlm Sleep Apnea
        {"symptom_id": "G06", "cf_pakar": 0.9}, # Henti napas adalah identitas mutlak Sleep Apnea!
        {"symptom_id": "G07", "cf_pakar": 0.5}, # Mulut kering merupakan efek samping
        {"symptom_id": "G04", "cf_pakar": 0.3}  # Kelelahan sebagai efek kurang kualitas tidur
    ],
    "P03": [
        {"symptom_id": "G08", "cf_pakar": 0.7}, # EDS mengantuk parah di siang hari
        {"symptom_id": "G09", "cf_pakar": 0.85},# Tertidur mendadak (Serangan tidur / Narkolepsi)
        {"symptom_id": "G10", "cf_pakar": 0.9}, # Katapleksi sangat mutlak mengindikasikan Narkolepsi
        {"symptom_id": "G11", "cf_pakar": 0.6}  # Kelumpuhan tidur 
    ],
    "P04": [
        {"symptom_id": "G12", "cf_pakar": 0.85},# Dorongan kuat menggerakan kaki (RLS)
        {"symptom_id": "G13", "cf_pakar": 0.75} # Rasa tidak nyaman di malam hari
    ],
    "P05": [
        {"symptom_id": "G14", "cf_pakar": 0.9}, # Siklus tertunda ke jam 2-3 pagi adalah Inti DSPS
        {"symptom_id": "G15", "cf_pakar": 0.8}  # Akibatnya susah bangun normal
    ]
}

# Fungsi Perhitungan Mesin Inferensi
def calculate_certainty_factors(user_answers):
    # Rumus CF: CF_Combine = CF_Lama + CF_Baru * (1 - CF_Lama)
    
    cf_results = {}
    
    for diagnosis_id, rules in KNOWLEDGE_RULES.items():
        cf_combine = 0.0 # CF awal untuk sebuah penyakit
        
        for rule in rules:
            symptom = rule["symptom_id"]
            cf_pakar = rule["cf_pakar"]
            
            # Jika user menjawab "Ya", maka CF dari User = 1.0 (Kita asumsikan kepastian User adalah 1)
            # Maka CF Rule = CF Pakar * CF User (1.0)
            if symptom in user_answers:
                cf_current_rule = cf_pakar * 1.0
                
                # Kalkulasi Gabungan Paralel Kombinatorial (Myster Algorithm Certainty Factor)
                if cf_combine == 0.0:
                    cf_combine = cf_current_rule
                else:
                    cf_combine = cf_combine + cf_current_rule * (1.0 - cf_combine)
                    
        # Simpan persentase hasil matematika CF tiap penyakit
        if cf_combine > 0:
            cf_results[diagnosis_id] = round(cf_combine * 100, 2) # Mengubah jadi persentase
            
    # Mengurutkan nilai probabilitas tertinggi ke terendah
    sorted_diagnoses = sorted(cf_results.items(), key=lambda item: item[1], reverse=True)
    return sorted_diagnoses


# Routing Flask (Web APP)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/gejala", methods=["GET"])
def get_symptoms():
    return jsonify({"symptoms": SYMPTOMS})

@app.route("/api/diagnosa", methods=["POST"])
def process_diagnosis():
    req_body = request.get_json()
    user_answers = req_body.get("answers", [])
    
    # Eksekusi Mesin Inferensi yang Kompleks
    diagnosed_percentages = calculate_certainty_factors(user_answers)
    
    hasil_detail = []
    
    if not diagnosed_percentages:
        # Jika sama sekali CF = 0 (Normal)
        hasil_detail.append({
            "name": "Pola Tidur Sehat/Normal",
            "percentage": 100,
            "description": "Tidak ada satupun indikator gangguan klinis tidur spesifik yang terdeteksi dari perhitungan (Kesimpulan persentase penyakit 0%). Anda terpantau aman.",
            "advice": "Fokus pada menjaga ritme sirkadian dengan berolahraga reguler dan memastikan kamar tetap hening & gelap saat malam."
        })
    else:
        # Gabungkan data untuk Client UI
        for diag_id, prob_percent in diagnosed_percentages:
            if prob_percent > 10: # Mengeliminasi noise kalkulasi matematis di bawah 10%
                data = DIAGNOSES[diag_id].copy()
                data["percentage"] = prob_percent
                hasil_detail.append(data)

    return jsonify({
        "status": "success",
        "diagnosa_ditemukan": hasil_detail
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
