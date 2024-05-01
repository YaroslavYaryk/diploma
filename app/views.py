import pydicom
from PIL import Image
from io import BytesIO
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def index(request):
    return render(request, 'converter/index.html')

@csrf_exempt
def dicom_to_jpeg(request):
    if request.method == 'POST':
        # Assuming the DICOM file is sent as a file upload in the request.FILES
        dicom_file = request.FILES.get('input-file')
        if not dicom_file:
            return HttpResponse('No DICOM file provided.', status=400)

        try:
            # Read the DICOM file
            ds = pydicom.dcmread(dicom_file)

            # Convert the DICOM image data to a PIL Image object
            # This example assumes the image is in the Pixel Data field and is uncompressed
            arr = ds.pixel_array
            image = Image.fromarray(arr)

            # Convert the PIL Image to JPEG
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            # Return the JPEG image as a response
            return HttpResponse(buffer, content_type="image/jpeg")
        except Exception as e:
            return HttpResponse(f'Error converting DICOM to JPEG: {str(e)}', status=500)
    else:
        return HttpResponse('Invalid request method. Please use POST.', status=405)
