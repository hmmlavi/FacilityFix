"""Verify and re-encode a single bounded image; never use supplied filenames."""
import io
import secrets
import warnings
from pathlib import Path

from flask import current_app
from PIL import Image, UnidentifiedImageError

from services.validation import ValidationError

MAX_PHOTO_BYTES = 2 * 1024 * 1024
MAX_PIXELS = 16_000_000


def save_photo(upload):
    if upload is None or not upload.filename:
        return None
    raw = upload.stream.read(MAX_PHOTO_BYTES + 1)
    if len(raw) > MAX_PHOTO_BYTES:
        raise ValidationError('Photo must be no larger than 2 MiB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as image:
                image_format = image.format
                if image_format not in ('JPEG', 'PNG'):
                    raise ValidationError('Photo must be a valid JPEG or PNG image.')
                if image.width * image.height > MAX_PIXELS:
                    raise ValidationError('Photo must contain no more than 16 million pixels.')
                if getattr(image, 'n_frames', 1) != 1:
                    raise ValidationError('Please attach a single still photo, not an animated image.')
                image.verify()
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                clean = image.convert('RGB' if image_format == 'JPEG' else 'RGBA')
                output = io.BytesIO()
                clean.save(output, format=image_format)
                encoded = output.getvalue()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError,
            Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError('Photo is invalid or cannot be safely decoded. Use a JPEG or PNG image.') from None
    name = secrets.token_hex(24) + ('.jpg' if image_format == 'JPEG' else '.png')
    path = Path(current_app.config['UPLOAD_FOLDER']) / name
    try:
        with path.open('xb') as file:
            file.write(encoded)
    except OSError:
        path.unlink(missing_ok=True)
        raise
    return name


def remove_photo(name):
    if name:
        (Path(current_app.config['UPLOAD_FOLDER']) / name).unlink(missing_ok=True)
