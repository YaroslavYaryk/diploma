import base64
import os
import time
import traceback
from io import BytesIO
import json
from io import StringIO
import gdcm
from PIL import Image

from helper.client import get_client_ip
from helper import image_classification
import imageio
import matplotlib.pyplot as plt
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from termcolor import colored
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile

from Diploma import settings
from .models import Collection


@csrf_exempt
def ajax_server(request):
    start = time.time()
    d = dict()
    generic = dict()
    medinfo = dict()
    
    try:
        if request.method == 'POST' and ('imgInp' in request.FILES) and request.FILES['imgInp']:
            files = request.FILES.getlist('imgInp')
            
            for file in files:
                extention = request.POST.get('file-extention')
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                full_path_file = os.path.join(settings.MEDIA_ROOT, filename)
                print(colored('path->', 'red'), full_path_file)
                
                generic['name'] = filename
                generic['size'] = os.path.getsize(full_path_file)
                try:
                    
                    if full_path_file[-3:].upper() == 'DCM':
                        dcpimg = imageio.imread(full_path_file)
                        for keys in dcpimg.meta:
                            medinfo[keys] = str(dcpimg.meta[keys])

                        if len(dcpimg.shape) == 4:
                            dcpimg = dcpimg[0, 0]
                        elif len(dcpimg.shape) == 3:
                            dcpimg = dcpimg[0]

                        
                    if full_path_file[-3:].upper() == 'PNG':
                        dcpimg = plt.imread(full_path_file)  # Read the PNG image using matplotlib
                        medinfo = {}  # Initialize metadata dictionary for PNG images (if needed)
                       
                    # medinfo.update(dcpimg.meta)
                    fig = plt.gcf()
                    fig.set_size_inches(18.5, 10.5)
                    plt.imshow(dcpimg, cmap='gray')
                    plt.colorbar()
                    figure = BytesIO()
                    if extention == 'jpeg':
                        plt.savefig(figure, format='jpeg', dpi=300)
                    elif extention == 'png':
                        plt.savefig(figure, format='png', dpi=300)
                    else:
                        plt.savefig(figure, format='jpg', dpi=300)
                    plt.close()
                    image_link = 'data:image/png;base64,' + base64.b64encode(figure.getvalue()).decode()
                    d['url'] = {'base64': image_link}
                    d['fileFormat'] = extention
                    # create image asociated with user
                    ip = get_client_ip(request)
                    Collection.objects.create(user_ip=ip, image_base64=image_link)
                except Exception as e:

                    traceback.print_tb(e)

                fs.delete(filename)
    except Exception as e:
        traceback.print_tb(e)

    generic['process time'] = time.time() - start
    d['generic'] = generic

    d['med'] = medinfo
    

    return JsonResponse(d)


def app_render(request):
    print(settings.BASE_DIR)
    d = {'title': 'DICOM viewer', 'info': 'DICOM SERVER SIDE RENDER'}
    return render(request, "converter/main_template.html", d)


def converter_history(request):
    ip = get_client_ip(request)

    numbers_on_page = 24

    page = int(request.GET.get('page', 1))

    left_border = numbers_on_page*(page-1)
    client_images_objects = Collection.objects.filter(user_ip=ip).order_by('-created_at')[left_border: left_border + numbers_on_page]

    client_images = [{
        'id': el.id,
        'created_at': str(el.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        'image_base64': el.image_base64,
        'image': el.image
    } for el in client_images_objects]

    context = {
        'client_images': client_images
    }

    return render(request, "converter/converter_history.html", context)


def get_images_by_ids(request):
   
    image_ids = list(range(1330, 1368))
    
    client_images_objects = Collection.objects.filter(id__in=image_ids)

    client_images = [el.image_base64 for el in client_images_objects]
    context = {
        'client_images': json.dumps(client_images)
    }

    return render(request, "converter/custom_downloader.html", context)


@csrf_exempt
def get_image_classification(request):
    
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    image_types = {
        'side': 'Вид збоку',
        'top': 'Вид зверху',
        'distant_top': 'Вид зверху з ногою'
    }
    
    image_clasification = {
        'healthy': 'Здоровий',
        'sick': 'Хворий'
    }
    
    sickness_classification = {
        'artritus': 'Артрит',
        'bursitus': 'Бурсит',
        'necroz': 'Некроз',
        'oasteoartritus': 'Остеоартрит',
        'phz': 'Розриви передньої хрестоподібної зв`язки',
        'revma_arthritus': 'Ревматоїдний артрит',
        'rozryv_meniska': 'Розриви меніску',
        'tenditit': 'Тендиніт'
    }
    
    base64 = body.get('base64')
    
    if not base64:
        return JsonResponse({'error': 'Image cannot be empty'})
    
    # get image type (side, top, distant_top)
    first_layer_result = image_classification.get_image_type(base64)
    
    
    # get image classification (healthy, sick) 
    second_layer_result = image_classification.get_image_classification(first_layer_result, base64)
    
    third_layer = None
    
    if second_layer_result == "sick":
        third_layer = image_classification.get_sickness_classification(first_layer_result, base64)
        
    return JsonResponse(
        {
            'image_type': image_types.get(first_layer_result), 
            'image_classification': image_clasification.get(second_layer_result), 
            'success': True,
            'sickness': sickness_classification.get(third_layer)
        }
    )