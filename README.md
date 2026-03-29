# Dokumentasi Proyek: Sistem Pakar Diagnosa Pola Tidur

Dokumen ini berisi tata letak arsitektur, landasan teori, dan penjabaran basis pengetahuan dari aplikasi Sistem Pakar Diagnosa Pola Tidur. Aplikasi ini bertugas untuk mensimulasikan kepakaran seorang dokter tidur (*Sleep Specialist*) dalam mendiagnosis masalah tidur seseorang melalui algoritma terstruktur.

---

## 1. Arsitektur dan Teknologi
Proyek ini dibangun menggunakan konsep **Aplikasi Berbasis Web** dengan pembagian kerja sebagai berikut:
- **Backend (Otak Sistem):** Bahasa Pemrograman **Python** menggunakan *framework* web ringan **Flask**. Backend bertugas memegang basis pengetahuan (aturan pakar) dan mengeksekusi perhitungan matematis *Certainty Factor*.
- **Frontend (Tampilan Skrining):** Menggunakan **HTML, CSS Vanilla, dan JavaScript**. Dibuat murni (tanpa Bootstrap/Tailwind) dengan implementasi tren *Glassmorphism* dan mode gelap untuk tema yang elegan dan rapi.
- **Komunikasi Data:** Frontend menampilkan pertanyaan, dan JS mengemas jawaban pengguna dalam format JSON lalu mem-POST nya ke endpoint API `/api/diagnosa` di Python. Python mereturn daftar penyakit beserta nilai kepastiannya ke *browser*.

---

## 2. Landasan Teori Kecerdasan Buatan
Aplikasi tidak menggunakan algoritma bercabang yang biasa (seperti if/else tebak-tebakan), melainkan menggunakan model pembentuk Sistem Pakar sesungguhnya, yaitu:

### A. Metode *Forward Chaining* (Runut Maju)
Sistem menanyakan dan mengumpulkan fakta (gejala-gejala) dari pengguna terlebih dahulu untuk dimasukkan ke dalam **Working Memory**, sebelum akhirnya ditarik sebuah konklusi/hipotesis di bagian akhir.

### B. Algoritma *Certainty Factor* (Faktor Kepastian)
Untuk mengakomodasi ketidakpastian dunia medis, sistem didukung hitungan probabilitas paralel. Pakar medis dalam sistem ini menentukan bobot atau derajat kepastian (**Measure of Belief / CF Pakar**) untuk tiap gejala dengan rentang angka 0.0 s/d 1.0.

Formula kombinasi paralel jika 2 Gejala merujuk ke probabilitas 1 Penyakit yang sama:
```text
CF_Combine = CF_1 + CF_2 * (1 - CF_1)
```
Hasil akhirnya akan memberikan angka persentase diagnostik (Contoh: "Anda diindikasikan mengalami Insomnia dengan tingkat kepastian 88%").

---

## 3. Basis Pengetahuan (Knowledge Base)

### Daftar Gejala / Fakta
1. **G01**: Sukar jatuh tertidur.
2. **G02**: Sering terbangun dan sukar tidur kembali.
3. **G03**: Bangun terlalu pagi/awal dan tak bisa tidur lagi.
4. **G04**: Kelelahan di siang hari.
5. **G05**: Mendengkur teramat keras.
6. **G06**: Tersedak/Henti napas sesaat di malam hari.
7. **G07**: Mulut sangat kering bangun tidur.
8. **G08**: Kantuk di siang hari yang tak tertahankan (EDS).
9. **G09**: Jatuh tertidur mendadak (Serangan Tidur).
10. **G10**: Otot lemas mendadak saat tertawa/kaget (Katapleksi).
11. **G11**: Tubuh kaku tak bisa bangun (Kelumpuhan Tidur/Ketindihan).
12. **G12**: Dorongan amat gelisah menggerakkan kaki.
13. **G13**: Kaki kesemutan secara kronis di malam hari.
14. **G14**: Siklus biologis jam tidur bergeser ke dini hari (>2 pagi).
15. **G15**: Sukar terbangun dan berfungsi normal di pagi hari.

### Daftar Penyakit (Hipotesis) & Aturan Pakarnya
Setiap gejala yang di-*input* memberikan kontribusi nilai CF kepada hipotesis terkait.

* **P01: Insomnia Klinis**
  * Didukung: G01 (Bobot: 0.8), G02 (Bobot: 0.7), G03 (Bobot: 0.6), G04 (Bobot: 0.4)
* **P02: Sleep Apnea (Henti Napas Obstruktif)**
  * Didukung: G05 (Bobot: 0.8), G06 (Bobot: 0.9), G07 (Bobot: 0.5), G04 (Bobot: 0.3)
* **P03: Narkolepsi**
  * Didukung: G08 (Bobot: 0.7), G09 (Bobot: 0.85), G10 (Bobot: 0.9), G11 (Bobot: 0.6)
* **P04: Restless Legs Syndrome (RLS)**
  * Didukung: G12 (Bobot: 0.85), G13 (Bobot: 0.75)
* **P05: Delayed Sleep Phase Syndrome (DSPS)**
  * Didukung: G14 (Bobot: 0.9), G15 (Bobot: 0.8)

Jika setelah pengguna dites sistem tak menemukan 1 pun aturan di atas yang CF-nya melebihi 10%, mesin secara otomatis mengkategorikan pasien masuk ke profil **P06: Pola Tidur Normal/Terpantau Aman.**
