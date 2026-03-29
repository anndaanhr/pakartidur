// Inisiasi Variabel State
let ALL_SYMPTOMS = [];
let CURRENT_QUESTION_INDEX = 0;
let USER_ANSWERS = [];

// DOM Elements
const viewHero = document.getElementById("view-hero");
const viewQuestion = document.getElementById("view-question");
const viewResult = document.getElementById("view-result");

const btnStart = document.getElementById("btn-start");
const btnYes = document.getElementById("btn-yes");
const btnNo = document.getElementById("btn-no");
const btnRestart = document.getElementById("btn-restart");

const questionText = document.getElementById("question-text");
const progressFill = document.getElementById("progress-fill");
const qCounter = document.getElementById("q-counter");
const diagnosesContainer = document.getElementById("diagnoses-container");

// Event Listener 
document.addEventListener("DOMContentLoaded", () => {
    btnStart.addEventListener("click", () => {
        fetchSymptoms();
    });

    btnYes.addEventListener("click", () => handleAnswer(true));
    btnNo.addEventListener("click", () => handleAnswer(false));

    btnRestart.addEventListener("click", resetApp);
});

// Fungsi-fungsi Logika UI
function switchView(hideEl, showEl) {
    hideEl.classList.remove("active");
    hideEl.classList.add("hidden");

    setTimeout(() => {
        showEl.classList.remove("hidden");
        showEl.classList.add("active");
    }, 100);
}

// Menjemput Pertanyaan dari API Python
async function fetchSymptoms() {
    btnStart.textContent = "Menghubungkan...";
    btnStart.disabled = true;

    try {
        const response = await fetch("/api/gejala");
        const data = await response.json();

        ALL_SYMPTOMS = data.symptoms;
        USER_ANSWERS = [];
        CURRENT_QUESTION_INDEX = 0;

        switchView(viewHero, viewQuestion);
        renderQuestion();

    } catch (error) {
        console.error("Gagal menjemput data API:", error);
        alert("Terjadi kesalahan teknis saat menghubungi sistem pakar (Server Python). Pastikan Backend sudah berjalan.");
        btnStart.textContent = "Mulai Diagnosa";
        btnStart.disabled = false;
    }
}

// Menampilkan pertanyaan sesuai State
function renderQuestion() {
    if (CURRENT_QUESTION_INDEX >= ALL_SYMPTOMS.length) {
        submitDiagnosis();
        return;
    }


    const currentSymptom = ALL_SYMPTOMS[CURRENT_QUESTION_INDEX];

    questionText.style.opacity = 0;
    setTimeout(() => {
        questionText.textContent = currentSymptom.text;
        questionText.style.opacity = 1;
    }, 300);

    // Update Progress Bar
    const total = ALL_SYMPTOMS.length;
    const answeredCount = CURRENT_QUESTION_INDEX + 1;
    const pct = (answeredCount / total) * 100;

    progressFill.style.width = pct + "%";
    qCounter.textContent = `${answeredCount} / ${total}`;
}

function handleAnswer(isYes) {
    const currentSymptom = ALL_SYMPTOMS[CURRENT_QUESTION_INDEX];

    if (isYes) {
        USER_ANSWERS.push(currentSymptom.id);
    }

    CURRENT_QUESTION_INDEX++;
    renderQuestion();
}

// Fungsi komunikasi API ke Python (Backend)
async function submitDiagnosis() {
    switchView(viewQuestion, viewResult);
    diagnosesContainer.innerHTML = "<p style='text-align:center;'>Memproses kalkulasi basis pengetahuan...</p>";

    try {
        const response = await fetch("/api/diagnosa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ answers: USER_ANSWERS })
        });

        const data = await response.json();
        if (data.status === "success") {
            renderDiagnoses(data.diagnosa_ditemukan);
        } else {
            throw new Error("Gagal memperoleh diagnosa");
        }

    } catch (error) {
        console.error(error);
        diagnosesContainer.innerHTML = "<p style='color:red;'>Terjadi kesalahan kritis pada Mesin Diagnosa.</p>";
    }
}

// Merender Card HTML berdasarkan data Array kembalian Backend
function renderDiagnoses(diagnosesArray) {
    diagnosesContainer.innerHTML = "";

    diagnosesArray.forEach(diag => {
        const card = document.createElement("div");
        card.className = "diagnosis-card fade-in";

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h3 class="diag-title font-outfit" style="margin-bottom: 0;">${diag.name}</h3>
                <span style="background: var(--success-grad); padding: 5px 12px; border-radius: 20px; font-weight: bold; font-family: Outfit;">
                    ${diag.percentage} % Certainty
                </span>
            </div>
            
            <div class="progress-track" style="margin-bottom: 1.5rem; height: 8px;">
                <div class="progress-fill" style="width: ${diag.percentage}%;"></div>
            </div>

            <p class="diag-desc font-inter">${diag.description}</p>
            <div class="diag-advice-title font-inter">💡 Rekomendasi/Tindakan:</div>
            <div class="diag-advice font-inter">
                ${diag.advice}
            </div>
        `;

        diagnosesContainer.appendChild(card);
    });
}

// Mengembalikan Aplikasi ke state awal
function resetApp() {
    btnStart.textContent = "Mulai Diagnosa";
    btnStart.disabled = false;

    switchView(viewResult, viewHero);
}
