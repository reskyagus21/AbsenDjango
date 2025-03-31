# face_app/train_faces.py
import face_recognition
import os
import pickle
from django.conf import settings

def train_faces():
    # Direktori tempat gambar wajah disimpan
    image_dir = os.path.join(settings.MEDIA_ROOT, 'faces')
    known_encodings = []
    known_names = []

    # Loop semua file di direktori faces
    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Path lengkap ke gambar
            image_path = os.path.join(image_dir, filename)
            print(f"Memproses: {filename}")

            # Load gambar
            image = face_recognition.load_image_file(image_path)
            
            # Deteksi dan encode wajah
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                # Ambil encoding pertama (asumsi 1 wajah per gambar)
                encoding = face_encodings[0]
                # Nama dari filename (misalnya "nama_jabatan.jpg" -> "nama")
                name = filename.split('_')[0]
                
                known_encodings.append(encoding)
                known_names.append(name)
            else:
                print(f"Tidak ada wajah terdeteksi di {filename}")

    # Simpan hasil training ke file
    def save_face_encodings(known_encodings, known_names, filename="face_encodings.pkl"):
    save_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Jika file sudah ada, hapus terlebih dahulu
    if os.path.exists(save_path):
        os.remove(save_path)
        print(f"File lama {filename} dihapus.")

    # Pastikan direktori media ada
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    # Simpan model baru
    data = {"encodings": known_encodings, "names": known_names}
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)

    print(f"Training selesai! Data disimpan di {filename}")
    # data = {"encodings": known_encodings, "names": known_names}
    # with open(os.path.join(settings.MEDIA_ROOT, 'face_encodings.pkl'), 'wb') as f:
    #     pickle.dump(data, f)
    # print("Training selesai! Data disimpan di face_encodings.pkl")

if __name__ == "__main__":
    # Setup Django environment
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_capture_project.settings')
    django.setup()
    train_faces()