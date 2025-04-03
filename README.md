# Face Attendance System

A face recognition-based attendance system built with Django and the `face_recognition` library. This project allows users to register members, record attendance using a webcam, and manage member and attendance data through a modern interface.

## Features
- **Member Registration**: Add member details (name, address, position) along with a face photo.
- **Automatic Attendance**: Detect faces to record attendance with timestamps and proof images.
- **Data Management**: View, edit, and delete member and attendance records.
- **Print Attendance List**: Export attendance data to a printable format with images.

## Prerequisites
- Python 3.8 or higher
- Webcam for face recognition
- Python dependencies (see `requirements.txt`)

## Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/reskyagus21/AbsenDjango.git

## How To use Attendance System
1. Go to "Capture" to add a new member (fill in details and take a photo)
2. Click "Train Faces" after adding members to update the recognition model.
3. Use "Attendance" to record attendance via webcam.
4. In "List", edit/delete members, delete attendance records, or print the attendance list.

## Directory Structure
- ApiAbsen/
- ├── Absen/
- │   ├── migrations/    # Database migrations
- │   ├── static/       # Static CSS, JS, and image files
- │   ├── templates/    # HTML templates (capture.html, absen.html, attendance_list.html)
- │   ├── models.py     # Person and Attendance models
- │   ├── urls.py       # Application routing
- │   └── views.py      # Backend logic
- ├── media/            # Face images and attendance proof
- ├── manage.py         # Django management script
- └── requirements.txt  # List of dependencies

## How To Run Project
1. pip install -r requirements.txt
2. Set up database
   - python manage.py makemigrations
   - python manage.py migrate
3. Configure Media in settings
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [BASE_DIR / "face_app/static"]
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"
4. Add Media in your url
   urlpatterns = [ path('', include('ApiAbsen.urls')), ]
      + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
5. Run the server
   python manage.py runserver

## 
        
