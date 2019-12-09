import StringIO
import logging
from PIL import Image
from datetime import datetime
from google.appengine.api import urlfetch, images
from google.appengine.api.app_identity import app_identity
from google.appengine.api.blobstore import blobstore
import cloudstorage
from methods.mapping import timestamp

MAX_SIZE = 960.0
_BUCKET = app_identity.get_default_gcs_bucket_name()


def _resize(image, size):
    width, height = image.size
    logging.info("image size is %sx%s", width, height)
    if width > size or height > size:
        ratio = min(size / width, size / height)
        new_size = int(width * ratio), int(height * ratio)
        logging.info("resizing to %sx%s", *new_size)
        image = image.resize(new_size, Image.ANTIALIAS)
    return image


def _save(image, filename):
    image_file = cloudstorage.open(filename, "w", 'image/png')
    try:
        image.save(image_file, 'PNG')
    except:
        logging.warning('can not save PNG')
        image_file.close()
        return False
    image_file.close()
    return True


def _get_serving_url(image, filename):
    blob_key = blobstore.create_gs_key("/gs" + filename)
    serving_url = images.get_serving_url(blob_key, size=max(image.size))
    logging.info(serving_url)
    return serving_url


def _get_filename(model_name, model_id):
    return '/%s/%s/%s/%s' % (_BUCKET, model_name, model_id, timestamp(datetime.utcnow()))


def get_image_url(model_name, model_id, image_data=None, url=None, size=MAX_SIZE):
    if url:
        image_data = urlfetch.fetch(url, deadline=30).content

    if image_data:
        image = Image.open(StringIO.StringIO(image_data))
        if image.mode == 'CMYK':
            image = image.convert('RGB')
    else:
        return
    image = _resize(image, size)

    filename = _get_filename(model_name, model_id)
    success = _save(image, filename)
    if success:
        return _get_serving_url(image, filename)
    else:
        return None
