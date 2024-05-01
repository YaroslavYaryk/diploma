import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import base64
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

import os
from django.conf import settings


def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """

    
    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
    return 'data:image/%s;base64,%s' % (format, encoded_string)


def base64_to_image(image_string):
    print(type(image_string))
    
    if ';base64,' in image_string:
        header, base64_string = image_string.split(';base64,')
    
    decoded_file = base64.b64decode(base64_string)
    # Convert binary data to an image
    image = Image.open(BytesIO(decoded_file))
    
    # Resize image if required
    image = image.resize([150,150])
    
    return image

def convert_image_to_array(image_data):
    if isinstance(image_data, ContentFile):
        image_data = image_data.read()  # Read bytes from ContentFile
    with BytesIO(image_data) as buffer:
        img = Image.open(buffer)  # Open image using Pillow
        img = img.convert('RGB')  # Ensure RGB channels (if applicable)
        # Preprocess the image as needed (resize, normalization, etc.)
        img_array = np.asarray(img)
        return img_array
    

def get_image_type(base64):
    model = load_model(os.path.join(settings.BASE_DIR, 'knee_joint_type_classifier_model.h5'))
    
    image = base64_to_image(base64)
    
    # Convert image to array
    img_array = img_to_array(image)

    # Нормалізуйте зображення
    img_array /= 255.0

    # Перетворіть масив в пакет, додавши один додатковий розмір
    img_batch = np.expand_dims(img_array, axis=0)
    
    # Робіть прогнозування
    predictions = model.predict(img_batch)

    # Визначте індекс максимального значення, що є передбачуваним класом
    predicted_class = np.argmax(predictions[0])
    class_labels = ['distant_top', 'side', 'top']

    # Виведіть передбачений клас
    return class_labels[predicted_class]


def get_base_model_result(link, image_string):
    model = load_model(os.path.join(settings.BASE_DIR, link))

    # Завантажте зображення
    image = base64_to_image(image_string)

    # Конвертуйте зображення в масив numpy
    img_array = img_to_array(image)

    # Нормалізуйте зображення
    img_array /= 255.0

    # Перетворіть масив в пакет, додавши один додатковий розмір
    img_batch = np.expand_dims(img_array, axis=0)

    # Робіть прогнозування
    predictions = model.predict(img_batch)

    # Визначте індекс максимального значення, що є передбачуваним класом
    predicted_class = np.argmax(predictions[0])
    class_labels = ['sick', 'healthy']

    # Виведіть передбачений клас
    return class_labels[predicted_class]


def get_sickness_base_model_result(link, image_string):
    model = load_model(os.path.join(settings.BASE_DIR, link))

    # Завантажте зображення
    image = base64_to_image(image_string)

    # Конвертуйте зображення в масив numpy
    img_array = img_to_array(image)

    # Нормалізуйте зображення
    img_array /= 255.0

    # Перетворіть масив в пакет, додавши один додатковий розмір
    img_batch = np.expand_dims(img_array, axis=0)

    # Робіть прогнозування
    predictions = model.predict(img_batch)

    # Визначте індекс максимального значення, що є передбачуваним класом
    predicted_class = np.argmax(predictions[0])
    class_labels = ['artritus', 'bursitus', 'necroz', 'oasteoartritus', 'phz', 'revma_arthritus', 'rozryv_meniska', 'tenditit']

    # Виведіть передбачений клас
    return class_labels[predicted_class]



def get_image_classification(image_type:str, image_string:str) -> str:
    
    if image_type == 'side':
        return get_base_model_result('sick_healty_knee_side_model.h5', image_string)
    
    elif image_type == 'top':
        return get_base_model_result('sick_healty_knee_top_model.h5', image_string)
    
    else:
        # distant top
        return 'healthy'
    
    
    
    
def get_sickness_classification(image_type:str, image_string:str) -> str:
    
    if image_type == 'side':
        return get_sickness_base_model_result('knee_sick_side_model.h5', image_string)
    
    elif image_type == 'top':
        return get_sickness_base_model_result('knee_sick_top_model.h5', image_string)