sarva-motor
===========

Proyek sarva-motor adalah koleksi skrip Python yang dirancang untuk mengontrol motor, khususnya motor stepper, pada perangkat Raspberry Pi. Proyek ini juga mencakup fungsionalitas untuk komunikasi serial dan server socket, memungkinkan interaksi dan kontrol jarak jauh terhadap sistem motor.

Fitur Utama
-----------

*   **Kontrol Motor Stepper:** Mengendalikan motor stepper dengan presisi.
    
*   **Komunikasi Serial:** Menangani komunikasi data melalui port serial.
    
*   **Server Socket:** Memungkinkan kontrol dan monitoring jarak jauh melalui koneksi jaringan.
    
*   **Integrasi Raspberry Pi:** Dirancang khusus untuk berjalan mulus di lingkungan Raspberry Pi.
    

Struktur Proyeka
----------------

Berikut adalah gambaran singkat struktur direktori utama:

*   sarva/: Direktori yang kemungkinan berisi lingkungan virtual Python (pyvenv.cfg) dan pustaka terkait.
    
*   serial\_control\_pi.py: Skrip untuk mengelola komunikasi serial di Raspberry Pi.
    
*   socket\_server\_pi.py: Skrip yang mengimplementasikan server socket untuk menerima perintah atau mengirim data.
    
*   stepper\_control\_pi.py: Skrip inti untuk mengendalikan operasi motor stepper.
    
*   test\_stepper.py: Skrip untuk pengujian fungsionalitas motor stepper.
    
*   requirements.txt: Daftar semua dependensi Python yang dibutuhkan proyek.
    

Memulai Proyek
--------------

Untuk menjalankan proyek ini di Raspberry Pi Anda, ikuti langkah-langkah di bawah ini:

### Prasyarat

Pastikan Anda memiliki hal-hal berikut:

*   Raspberry Pi (model apa pun yang kompatibel)
    
*   Koneksi internet (untuk menginstal dependensi)
    
*   Motor stepper dan driver yang sesuai, terhubung ke GPIO Raspberry Pi
    
*   Pengetahuan dasar tentang Linux command line
    

### Instalasi

1.  git clone https://github.com/adrianramadhan/sarva-motor.gitcd sarva-motor
    
2.  python3 -m venv sarvasource sarva/bin/activate_(Jika Anda menggunakan Windows, gunakan sarva\\Scripts\\activate)_
    
3.  pip install -r requirements.txt
    

### Penggunaan

Setelah instalasi, Anda bisa menjalankan skrip-skrip individual.

*   python3 test\_stepper.pyPastikan Anda telah mengkonfigurasi pin GPIO dengan benar di dalam skrip stepper\_control\_pi.py dan test\_stepper.py agar sesuai dengan koneksi hardware Anda.
    
*   python3 socket\_server\_pi.pyAnda mungkin perlu menyesuaikan alamat IP dan port dalam skrip ini sesuai kebutuhan Anda.
    
*   python3 serial\_control\_pi.pyPastikan untuk mengkonfigurasi port serial yang benar di dalam skrip ini.
    

Kontribusi
----------

Kontribusi disambut baik! Jika Anda memiliki saran atau perbaikan, silakan:

1.  Fork repositori ini.
    
2.  Buat branch baru (git checkout -b fitur/nama-fitur).
    
3.  Lakukan perubahan Anda.
    
4.  Commit perubahan Anda (git commit -m 'Tambahkan fitur baru').
    
5.  Push ke branch (git push origin fitur/nama-fitur).
    
6.  Buka Pull Request.
    

Lisensi
-------

\[TBD: Tambahkan informasi lisensi di sini, misal MIT, GPL, dll.\]
