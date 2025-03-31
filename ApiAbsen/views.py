# face_app/views.py
import base64
import json  
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Person, Kehadiran
import os
from django.conf import settings
from io import BytesIO
from PIL import Image
import face_recognition
import pickle
from django.utils import timezone
from datetime import datetime

def capture_page(request):
    return render(request, 'capture.html')

def absen_page(request):
    return render(request, 'absen.html')

def attendance_list_page(request):
    attendances = Kehadiran.objects.all().order_by('-waktu')
    persons = Person.objects.all().order_by('nama')
    return render(request, 'attendance_list.html', {
        'attendances': attendances,
        'persons': persons
    })
    
@csrf_exempt  # Matikan CSRF buat testing, nanti pake token kalau production
def save_face(request):
    if request.method == "POST":
        try:
            # Ambil data dari request
            data = request.POST if request.POST else request.body
            import json
            data = json.loads(data) if isinstance(data, bytes) else data

            nama = data.get('nama')
            alamat = data.get('alamat')
            jabatan = data.get('jabatan')
            image_data = data.get('image')  # Base64 string dari frontend

            # Decode base64 jadi gambar
            image_data = image_data.split(',')[1]  # Hilangin "data:image/jpeg;base64,"
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))

            # Simpan gambar ke directory
            file_name = f"{nama}_{jabatan}.jpg"
            file_path = os.path.join(settings.MEDIA_ROOT, 'faces', file_name)
            image.save(file_path, 'JPEG')

            # Simpan data ke database
            person = Person(
                nama=nama,
                alamat=alamat,
                jabatan=jabatan,
                gambar=f'faces/{file_name}'  # Path relatif buat ImageField
            )
            person.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Data dan gambar berhasil disimpan',
                'id': person.id,
                'code':200
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'code':400
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def train_faces_view(request):
    image_dir = os.path.join(settings.MEDIA_ROOT, 'faces')
    known_encodings = []
    known_names = []

    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(image_dir, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                encoding = face_encodings[0]
                name = filename.split('_')[0]
                known_encodings.append(encoding)
                known_names.append(name)

    data = {"encodings": known_encodings, "names": known_names}
    with open(os.path.join(settings.MEDIA_ROOT, 'face_encodings.pkl'), 'wb') as f:
        pickle.dump(data, f)    

    return JsonResponse({'status': 'success', 'message': 'Training selesai!','code':200})

@csrf_exempt
def recognize_and_attend(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Data diterima:", data)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'Image data tidak ada'}, status=400)

            # Decode gambar dari base64
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))

            # Konversi ke format RGB buat face_recognition
            image_array = face_recognition.load_image_file(BytesIO(image_bytes))

            # Load model training
            with open(os.path.join(settings.MEDIA_ROOT, 'face_encodings.pkl'), 'rb') as f:
                trained_data = pickle.load(f)
            known_encodings = trained_data['encodings']
            known_names = trained_data['names']

            # Deteksi dan recognisi wajah
            face_encodings = face_recognition.face_encodings(image_array)
            if len(face_encodings) == 0:
                return JsonResponse({'status': 'error', 'message': 'Wajah tidak Diketahui', 'code': 404}, status=404)

            unknown_encoding = face_encodings[0]
            results = face_recognition.compare_faces(known_encodings, unknown_encoding)
            name = "Unknown"
            for i, match in enumerate(results):
                if match:
                    name = known_names[i]
                    break

            # Cek apakah anggota udah absen hari ini
            today = timezone.now().date()
            if Kehadiran.objects.filter(
                namaAnggota=name,
                waktu__date=today
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'{name} sudah absen hari ini',
                    'code': 409
                }, status=409)

            # Simpan gambar kehadiran
            file_name = f"{name}_{int(__import__('time').time())}.jpg"
            file_path = os.path.join(settings.MEDIA_ROOT, 'kehadiran', file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            image.save(file_path, 'JPEG')

            # Simpan ke database
            kehadiran = Kehadiran(
                gambarKehadiran=f'kehadiran/{file_name}',
                namaAnggota=name
            )
            kehadiran.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Wajah dikenali sebagai {name}, absen tercatat',
                'nama': name,
                'waktu': kehadiran.waktu.isoformat(),
                'code': 200
            })
        except Exception as e:
            print("Error di recognize_and_attend:", str(e))  # Debug: cek error
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'code': 500
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def get_today_attendances(request):
    today = timezone.now().date()
    attendances = Kehadiran.objects.filter(waktu__date=today).order_by('-waktu')
    data = [
        {
            'nama': attendance.namaAnggota,
            'gambar': attendance.gambarKehadiran.url
        }
        for attendance in attendances
    ]
    return JsonResponse({'attendances': data})

@csrf_exempt
def delete_attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            attendance_id = data.get('id')
            attendance = Kehadiran.objects.get(id=attendance_id)
            
            # Hapus file gambar dari media
            image_path = os.path.join(settings.MEDIA_ROOT, attendance.gambarKehadiran.name)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Hapus data dari database
            attendance.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Data kehadiran berhasil dihapus'
            })
        except Kehadiran.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Data kehadiran tidak ditemukan'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_person(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            person_id = data.get('id')
            person = Person.objects.get(id=person_id)
            
            # Hapus file gambar dari media
            image_path = os.path.join(settings.MEDIA_ROOT, person.gambar.name)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Hapus data dari database
            person.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Data anggota berhasil dihapus'
            })
        except Person.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Data anggota tidak ditemukan'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def edit_person(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            person_id = data.get('id')
            nama = data.get('nama')
            alamat = data.get('alamat')
            jabatan = data.get('jabatan')

            person = Person.objects.get(id=person_id)
            person.nama = nama
            person.alamat = alamat
            person.jabatan = jabatan
            # Gambar tidak diubah di sini, hanya teks
            person.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Data anggota berhasil diperbarui'
            })
        except Person.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Data anggota tidak ditemukan'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)