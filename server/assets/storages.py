import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

storage_dirs = ["audio", "video", "image", "text"]

for d in storage_dirs:
    os.makedirs(f"/media/{d}", exist_ok=True)


def get_dir(dir_name):
    return os.path.join(settings.BASE_DIR, dir_name)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name


audio_storage = OverwriteStorage(location=get_dir('/media/audio'))
video_storage = OverwriteStorage(location=get_dir('/media/video'))
image_storage = OverwriteStorage(location=get_dir('/media/image'))
text_storage = OverwriteStorage(location=get_dir('/media/text'))
