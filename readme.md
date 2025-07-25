sarva-motor
Proyek sarva-motor adalah koleksi skrip Python yang dirancang untuk mengontrol motor, khususnya motor stepper, pada perangkat Raspberry Pi. Proyek ini juga mencakup fungsionalitas untuk komunikasi serial dan server socket, memungkinkan interaksi dan kontrol jarak jauh terhadap sistem motor.

Fitur Utama
Kontrol Motor Stepper: Mengendalikan motor stepper dengan presisi.

Komunikasi Serial: Menangani komunikasi data melalui port serial.

Server Socket: Memungkinkan kontrol dan monitoring jarak jauh melalui koneksi jaringan.

Integrasi Raspberry Pi: Dirancang khusus untuk berjalan mulus di lingkungan Raspberry Pi.

Struktur Proyek
Berikut adalah gambaran singkat struktur direktori utama:

sarva/: Direktori yang kemungkinan berisi lingkungan virtual Python (pyvenv.cfg) dan pustaka terkait.

serial_control_pi.py: Skrip untuk mengelola komunikasi serial di Raspberry Pi.

socket_server_pi.py: Skrip yang mengimplementasikan server socket untuk menerima perintah atau mengirim data.

stepper_control_pi.py: Skrip inti untuk mengendalikan operasi motor stepper.

test_stepper.py: Skrip untuk pengujian fungsionalitas motor stepper.

requirements.txt: Daftar semua dependensi Python yang dibutuhkan proyek.

Memulai Proyek
Untuk menjalankan proyek ini di Raspberry Pi Anda, ikuti langkah-langkah di bawah ini:

Prasyarat
Pastikan Anda memiliki hal-hal berikut:

Raspberry Pi (model apa pun yang kompatibel)

Koneksi internet (untuk menginstal dependensi)

Motor stepper dan driver yang sesuai, terhubung ke GPIO Raspberry Pi

Pengetahuan dasar tentang Linux command line

Instalasi
Kloning Repositori:
Buka terminal di Raspberry Pi Anda dan kloning repositori ini:

git clone https://github.com/adrianramadhan/sarva-motor.git
cd sarva-motor

Buat dan Aktifkan Lingkungan Virtual (Direkomendasikan):
Ini adalah praktik terbaik untuk mengisolasi dependensi proyek.

python3 -m venv sarva
source sarva/bin/activate

(Jika Anda menggunakan Windows, gunakan sarva\Scripts\activate)

Instal Dependensi:
Setelah lingkungan virtual aktif, instal semua pustaka Python yang diperlukan dari requirements.txt:

pip install -r requirements.txt

Penggunaan
Setelah instalasi, Anda bisa menjalankan skrip-skrip individual.

Untuk menguji motor stepper:

python3 test_stepper.py

Pastikan Anda telah mengkonfigurasi pin GPIO dengan benar di dalam skrip stepper_control_pi.py dan test_stepper.py agar sesuai dengan koneksi hardware Anda.

Untuk menjalankan server socket (contoh):

python3 socket_server_pi.py

Anda mungkin perlu menyesuaikan alamat IP dan port dalam skrip ini sesuai kebutuhan Anda.

Untuk menjalankan kontrol serial (contoh):

python3 serial_control_pi.py

Pastikan untuk mengkonfigurasi port serial yang benar di dalam skrip ini.

Kontribusi
Kontribusi disambut baik! Jika Anda memiliki saran atau perbaikan, silakan:

Fork repositori ini.

Buat branch baru (git checkout -b fitur/nama-fitur).

Lakukan perubahan Anda.

Commit perubahan Anda (git commit -m 'Tambahkan fitur baru').

Push ke branch (git push origin fitur/nama-fitur).

Buka Pull Request.

Lisensi
[TBD: Tambahkan informasi lisensi di sini, misal MIT, GPL, dll.]
