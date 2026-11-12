from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError


class FileStorage:
    def __init__(self, upload_directory):
        self.upload_directory = Path(upload_directory)
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    def save_image(self, uploaded_file):
        if not uploaded_file or not uploaded_file.filename:
            raise ValueError("Choose an image file to search.")
        path = self.upload_directory / f"{uuid4().hex}.jpg"
        try:
            with Image.open(uploaded_file.stream) as source:
                if source.width * source.height > 40_000_000:
                    raise ValueError("The uploaded image is too large to process.")
                image = source.convert("RGB")
                image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                image.save(path, format="JPEG", quality=88, optimize=True)
        except ValueError:
            path.unlink(missing_ok=True)
            raise
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as exc:
            raise ValueError("The uploaded file is not a supported image.") from exc
        return path
