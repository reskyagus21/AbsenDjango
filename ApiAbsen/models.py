# Create your models here.
# face_app/models.py
from django.db import models

class Person(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    jabatan = models.CharField(max_length=100)
    gambar = models.ImageField(upload_to='faces/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama

class Kehadiran(models.Model):
    waktu = models.DateTimeField(auto_now_add=True)  # Waktu absen otomatis
    gambarKehadiran = models.ImageField(upload_to='attendance/')  # Gambar saat absen
    namaAnggota = models.CharField(max_length=100)  # Nama dari recognisi

    def __str__(self):
        return f"{self.namaAnggota} - {self.waktu}"
