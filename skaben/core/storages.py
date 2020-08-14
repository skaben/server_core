import os
from django.core.files.storage import FileSystemStorage

dirs = ["audio", "video", "image"]

for d in dirs:
    os.makedirs(f"/media/{d}", exist_ok=True)

audio_storage = FileSystemStorage(location='/media/audio')
video_storage = FileSystemStorage(location='/media/video')
image_storage = FileSystemStorage(location='/media/image')
