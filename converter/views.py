import base64
import os
import time
import traceback
from io import BytesIO
import json
from io import StringIO
import gdcm
from PIL import Image
import math

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
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator

from Diploma import settings
from .models import Collection, CollectionStats

total_score = {
    'jpeg': 0,
    'png': 0,
    'bmp': 0,
}

def evaluate_parameters(params, total_score):
    for param in params:
        if param < 33:
            total_score['jpeg'] += 1
        elif 33 <= param <= 66:
            total_score['png'] += 1
        else:
            total_score['bmp'] += 1

@csrf_exempt
def ajax_server(request):
    start = time.time()
    d = {'url': {}}
    generic = dict()
    medinfo = dict()
    
    try:
        if request.method == 'POST' and ('imgInp' in request.FILES) and request.FILES['imgInp']:
            files = request.FILES.getlist('imgInp')
            
            for file in files:
                
                prefferences = json.loads(request.POST.get('prefferences'))
                
                
                extention = request.POST.get('file-extention')
                quality = prefferences.get('quality')
                taken_space = prefferences.get('takenSpace')
                saveMetadata = prefferences.get('saveMetadata')
                systemCompability = prefferences.get('systemCompability')
                deepGrey = prefferences.get('deepGrey')
                convertationSpeed = prefferences.get('convertationSpeed')
                parameters = [quality, taken_space, saveMetadata, systemCompability, deepGrey, convertationSpeed]
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                full_path_file = os.path.join(settings.MEDIA_ROOT, filename)
                print(colored('path->', 'red'), full_path_file)
                
                generic['Quality'] = quality
                generic['Taken space'] = taken_space
                generic['Save matadata'] = saveMetadata
                generic['System compability'] = systemCompability
                generic['Deep Grey'] = deepGrey
                generic['Convertation Speed'] = convertationSpeed

                
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

                    if full_path_file[-4:].upper() == 'JPEG':
                        dcpimg = plt.imread(full_path_file)  # Read the PNG image using matplotlib
                        medinfo = {}  # Initialize metadata dictionary for PNG images (if needed)

                    # medinfo.update(dcpimg.meta)
                    fig = plt.gcf()
                    fig.set_size_inches(18.5, 10.5)
                    plt.imshow(dcpimg, cmap='gray')
                    plt.colorbar()
                    figure = BytesIO()

                    evaluate_parameters(parameters, total_score)
                    if all(value == 0 for value in total_score.values()):
                        extention = "png"
                    else:
                        extention = max(total_score, key=total_score.get)
                        print(total_score, '++SD_SA_D)_SA()FD(ASF(ASF))')
                        print(extention)
                        
                    
                    if extention == 'jpeg':
                        plt.savefig(figure, format='jpeg', dpi=300)
                    elif extention == 'png':
                        plt.savefig(figure, format='png', dpi=300)
                    else:
                        plt.savefig(figure, format='png', dpi=300)
                    

                    # if extention == 'jpeg':
                    #     plt.savefig(figure, format='jpeg', dpi=300)
                    # elif extention == 'png':
                    #     plt.savefig(figure, format='png', dpi=300)
                    # else:
                    #     plt.savefig(figure, format='jpg', dpi=300)
                    plt.close()
                    image_link = 'data:image/png;base64,' + base64.b64encode(figure.getvalue()).decode()
                    d['url'] = {'base64': image_link}
                    
                    d['fileFormat'] = extention
                    # create image asociated with user
                    ip = get_client_ip(request)
                    collection = Collection(user_ip=ip, image_base64=image_link)
                    collection.save()
                except Exception as e:

                    traceback.print_tb(e)

                fs.delete(filename)
    except Exception as e:
        traceback.print_tb(e)

    generic['process time'] = time.time() - start
    d['generic'] = generic
    
    d['med'] = medinfo
    
    return render(request, "converter/main_template.html", d)


def app_render(request):
    d = {'title': 'DICOM viewer', 'info': 'DICOM SERVER SIDE RENDER', 'generic': {}, 'url': {}, 'fileFormat': ''}
    return render(request, "converter/main_template.html", d)


def converter_history(request):
    
    # with transaction.atomic():
    #     collections = Collection.objects.all()
    
    #     collection_stats = []
        
    #     for collection in collections:
    #         image = collection.image_base64
            
    #         try:
    #             # get image type (side, top, distant_top)
    #             first_layer_result = image_classification.get_image_type(image)
                
    #             # get image classification (healthy, sick) 
    #             second_layer_result = image_classification.get_image_classification(first_layer_result, image)
                
    #             third_layer = None
                
    #             if second_layer_result == "sick":
    #                 third_layer = image_classification.get_sickness_classification(first_layer_result, image)
                    
                
    #             stats = CollectionStats(
    #                 collection=collection,
    #                 image_type=first_layer_result,
    #                 health_status=second_layer_result,
    #                 sickness=third_layer
    #             )
    #         except:
    #             continue
            
    #         collection_stats.append(stats)
            
        
    #     CollectionStats.objects.bulk_create(collection_stats)
        
    
    # return JsonResponse({"message": "ok"})
    
    
    ip = get_client_ip(request)

    numbers_on_page = 24

    page = int(request.GET.get('page', 1))

    paginator = Paginator(Collection.objects.filter(user_ip=ip).order_by('-created_at'), numbers_on_page)

    count_pages = math.ceil(len(Collection.objects.filter(user_ip=ip).order_by('-created_at'))/numbers_on_page)

    page_obj = paginator.get_page(page)

    client_images = [{
        'id': el.id,
        'created_at': str(el.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        'image_base64': el.image_base64,
        'image': el.image
    } for el in page_obj]

    context = {
        'client_images': client_images,
        'page_obj': page_obj,
        'page': page,
        'max_count': count_pages
    }

    return render(request, "converter/converter_history.html", context)


def client_statistics(request):
    
    collection_stats = CollectionStats.objects.all()
    
    collection_stats_type = collection_stats.values('image_type').annotate(count=Count('image_type'))
    
    image_types = [el for el in collection_stats_type if el['image_type'] != 'distant_top']
    
    collection_stats_health_status = collection_stats.values('health_status').annotate(count=Count('health_status'))
    
    filtered_collection_stats_sickness = [
        el for el in collection_stats.values('sickness').annotate(count=Count('sickness')) if el['sickness']
    ]
    
    context = {
        'image_types': json.dumps(image_types),
        'health_status': json.dumps(list(collection_stats_health_status)),
        'sickness': json.dumps(filtered_collection_stats_sickness)
    }
    
    return render(request, "converter/stats.html", context)


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

    sickness_heal = {
        "artritus": {
            "termin": "Артрити – це велика група захворювань суглобів запального характеру, що має різне походження. У перекладі з латинської термін означає – «артр» – суглоб, «іт» – запалення. Причина запалення може бути пов'язана з інфекцією, травмами, метаболічними розладами та ін. Артрит вражає людей різного віку, нерідко призводить до втрати працездатності та інвалідизації.",
            "symptoms": ["припухлість і почервоніння шкіри над ураженими суглобами;", "наявність більше ніж 3 запалених суглобів;", "ураження міжфалангових і/або п'ястково-фалангових суглобів;", "ранкова скутість протягом 30 і більше хвилин;", "порушення функцій суглобів;", "травма суглоба."],
            "heal_method": 
            {
                "main": "Основна мета лікування артриту — позбавлення від запальних процесів і хворобливих відчуттів, досягнення і підтримання клінічного поліпшення, стійкої ремісії, запобігання розвитку деформацій суглобів і їх подальшого руйнування.\nМетоди лікування артриту можна умовно розділити на хірургічні та нехірургічні.",
                "surgical": "Операція при артриті показана при виражених деформаціях суглобів, зниженні їх функцій і значному обмеженні руху.\n<b>Під час операції хірург застосовує в зазначеному порядку</b>:\nсіновектомію — видалення запаленої синовіальної оболонки суглоба;\nартродез — штучне закриття суглоба в найбільш вигідному фізіологічному положенні;\nартропластику — створення нового суглоба на основі зруйнованого з використанням біологічних або алопластичних прокладок;\nрезекцію ураженого суглоба з подальшим ендопротезуванням.\nПротипоказаннями до оперативного лікування є захворювання в гострій стадії, наявність осередків гнійної інфекції, амілоїдоз, важкі вісцерити.",
                "non-surgical": "До таких методів відносять наступний комплекс заходів:\nфармакотерапію (протизапальні, знеболюючі, антибактеріальні препарати);\nімуносупресивну терапію;\nмісцеву терапію (внутрішньосуглобове введення лікарських препаратів, лікувальні аплікації);\nфізіотерапію (УФО суглобів, фонофорез гідрокортизону, електромагнітотерапію, магнітолазерну терапію, лікування парафіном та озокеритом);\nлікувальну фізкультуру і гімнастику;\nспеціальну дієту;\nсанаторно-курортне лікування.\nУ комплексному лікуванні артритів важливе значення має дієтичне харчування. На консультації дієтолог для кожного хворого підбирає індивідуальну дієту. Як правило, до поліпшення самопочуття і зниження активності захворювання призводить розвантажувальна, вегетаріанська і рослинно-молочна дієта.\nУ комплексній терапії тяжких варіантів перебігу артритів застосовують методи екстракорпоральної детоксикації: гемосорбцію, плазмаферез, кріоплазмасорбцію та ін.",
            }, 
        },
        'bursitus': {
            'termin': 'Бурсит — запалення навколосуглобової сумки суглоба, виникає при надмірному динамічному навантаженні на суглоб або якщо суглоб тривалий час знаходиться у стані напруги.\n\nНайбільш часто бурсит розвивається в ділянці плечових, ліктьових і колінних суглобів, рідше стегнових і ділянці ахілового сухожилля.',
            "symptoms": ["біль, запалення, набряк в ділянці суглоба;", "обмежений обсяг рухів у суглобі, що супроводжується різким болем, або без нього.", "почервоніння шкіри і локальне підвищення температури над ділянкою суглоба."],
            'heal_method': {
                'main': "Бурсит — захворювання, яке добре піддається лікуванню. Симптоми зазвичай проходять через 7–14 днів при правильному лікуванні. Після закінчення курсу необхідно зробити контрольне інструментальне дослідження. У разі зникнення симптомів і ознак спостереження у лікаря не потрібно. Після оперативного втручання контроль виліковності здійснюється за планом лікаря-травматолога.",
                'non-surgical': 'Лікування включає в себе спокій ураженого суглоба, захист від подальшої травматизації і перевантаження.\nУ більшості випадків бурсит проходить протягом декількох тижнів при правильному лікуванні і профілактиці рецидиву бурситу.\nПризначаються нестероїдні протизапальні препарати, які зменшують запалення і больовий синдром для прийому всередину і місцево у вигляді мазей або гелів.\nАнтибактеріальна терапія призначається тільки при виявленні інфекційного агента в посіві синовіальної рідини.\nПри відсутності протипоказів можливе використання фізіотерапевтичного лікування (ультразвук з глюкокортикоїдами, фонофорез та ін.).\nРекомендовано використання спеціальних ортопедичних пристроїв (налокітники, наколінники та ін.) Для уникнення подальшої травматизації і профілактики рецидивів бурситу.\nДо немедикаментозних методів лікування відноситься і кінезіотейпування, яке допомагає зменшити больовий синдром і подальшу травматизацію навколосуглобових сумок.\nДля швидкого купірування бурситу проводиться пункція бурси з видаленням надлишкової кількості рідини і введенням глюкокортикоїдів. У рідкісних випадках проводиться хірургічне лікування – видалення навколосуглобової сумки (бурси).\nПри встановленні специфічного запалення (ревматоїдного артриту, подагри та ін.) – спостереження у ревматолога для визначення подальшої тактики лікування.',
                'surgical': 'В деяких випадках вдаються до оперативного втручання – видалення уражених суглобових сумок малоінвазивним хірургічним методом. '
            } 
        },
        'necroz': {
            'termin': 'Остеонекроз колінного суглоба (також його ще називають аваскулярний або асептичний некроз) – це стан, що виникає при порушенні кровопостачання ділянки кісткової тканини стегнової або великогомілкової кістки. Оскільки кісткові клітини для нормальної своєї роботи потребують постійного кровопостачання, остеонекроз, що супроводжується загибеллю цих клітин, може в кінцевому підсумку призвести до деструктивних змін колінного суглоба і вираженого остеоартрозу. ',
            'syptoms': ["Перша ознака — біль. При асептичному некрозі головки стегнової кістки локалізація болю в паху і сідницях. Біль має схильність до широкої іррадіації на внутрішню поверхню стегна, а особливо часто — в ділянку колінного суглоба.", "Поява «стартового» болю при початку руху, підйомі з ліжка. При прогресуючому некрозі кісток кульшового або колінного суглоба може відбуватися вкорочення кінцівки і з’являтися кульгавість. Нижня кінцівка втрачає свою рухливість: її важко зігнути або відвести в сторону. На ній досить швидко атрофуються м’язи, що створює ефект схуднення кінцівки відносно всього тіла."],
            'heal_method': {
                'main': 'У рандомізованих клінічних дослідженнях показано, що ефективність консервативного лікування вкрай мала!',
                'surgical': 'дотримання оптимального ортопедичного режиму з розвантаженням протягом 4-8 тижнів за допомогою милиць або тростини;\nлікувальна гімнастика знеболювальна терапія;\nвнутрішньосуглобова ін’єкційна терапія;\nкорекція ходьби;\nвазодилятатори;\nаналоги простацикліну;\nпрепарати кальцію і вітаміну Д;\nбісфосфонати;\nстатини;\nелектроміостимуляція;\nфізіотерапія (КВЧ терапія, лазеротерапія, магнітотерапія).',
                'non-surgical': 'в початковому періоді потрібно прагнути до призупинення розвитку змін — кращі результати досягаються шляхом видалення некротичного фрагмента кістки, але такі втручання не завжди ефективні. В деяких випадках імплантується ендопротез ураженого суглоба.'
            } 
        },
        'oasteoartritus': {
            'termin': 'Остеоартрит – це запалення у хрящі та синовії, що призводить до дегенеративних процесів і поступової втрати суглобової структури. Це найпоширеніший вид артриту.',
            "symptoms": ['біль у суглобах, який зумовлюють інтенсивні фізичні навантаження;', 'обмежений рух;', 'хрускіт;', 'скутість суглобів навіть під час відпочинку;', 'припухлість і набряк в зоні ураженого суглоба;', 'ниючий біль;', 'місцеве збільшення температури, почервоніння.'],
            'heal_method': {
                'main': 'Остеоартрит – це захворювання, яке лікують із ціллю зменшення больових відчуттів та відновлення функціональності ураженого суглоба.',
                'surgical': 'Показано на пізніх стадіях остеоартриту, направлено на повне відновлення функції суглоба.\n\nПри нормалізації надмірної ваги, занятті лікувальною гімнастикою в поєднанні з медикаментозним лікуванням хондропротекторами і препаратами гіалуронової кислоти, можна уповільнити прогресування хвороби, поліпшити функцію суглобів і зменшити біль, відстрочити ендопротезування суглобів.',
                'non-surgical': 'Фізичні вправи, які допомагають знизити біль – фізіотерапія, електромагнітна імпульсна терапія.\nКорекція харчування, щоб зменшити вагу.\nФармакологічні засоби – ліки від болю та ті, що зменшують запальний процес (антибіотики, протизапальні, протинабрякові препарати).',
            } 
        },
        'phz': {
            'termin': 'Розрив передньої хрестоподібної зв\'язки (ПХЗ) – це ушкодження однієї з основних зв\'язок колінного суглобу. Передня хрестоподібна зв\'язка є одним із стабілізаторів колінного суглобу, і її ушкодження, навіть часткові, призводять до нестабільності колінного суглобу.',
            'symptoms': ['різкий біль;', 'хрускіт у суглобі;', 'коліно швидко набрякає;', 'з’являється відчуття нестабільності через зсув кісткових структур і розпирання, викликане кровотечею в суглобову порожнину'],
            'heal_method': {
                'main': 'Розрив зв’язок у колінному суглобі часто супроводжується запальними процесами, утворенням мікротріщин і переломом кісткових пластин у місці кріплення волокон. Виходячи зі складності ушкоджень і призначається консервативне або хірургічне лікування.',
                'surgical': 'Накладення холодних компресів на місце травми, застосування лікарських препаратів для зняття запальних процесів, зменшення набряклості; відновлення пошкоджених суглобів, іммобілізацію (знерухомлення) кінцівки за допомогою накладання шин на 4 – 6 тижнів;використання наколінників, бандажів, супортів і ортезів для стабілізації та компенсації порушених функцій коліна; відсмоктування рідини, яка накопичується при гемартрозі; зниження функціонального навантаження на кінцівку; реабілітаційні процедури',
                'non-surgical': 'Роблять три невеликих проколи для отримання доступу до суглоба; через проколи в порожнину вводиться артроскоп з міні-відеокамерою, що дозволяє контролювати хід операції, трансплантат і хірургічні інструменти; трансплантат фіксується на великогомілковій кістці матеріалом, який саморозсмоктується; надалі зв’язка приживається і заповнює простір суглобової порожнини.'
            } 
        },
        
        'revma_arthritus': {
            'termin': 'Ревмато́їдний артри́т — системне захворювання сполучної тканини з переважним ураженням дрібних суглобів за типом ерозивно-деструктивного поліартриту неясної етіології зі складним автоімунним патогенезом.',
            'symptoms': ['симетричний біль і набряк;', 'ранкова ригідність різної тривалості, зазвичай >1 год;', 'субфебрилітет;', 'міалгія;', 'втомлюваність;', 'відсутність апетиту;', 'втрата маси тіла'],
            'heal_method': {
                'main': 'Метою лікування є клінічна ремісія згідно з визначенням ACR і EULAR або принаймні низька активність хвороби, якщо досягнення ремісії є малоймовірним. Цю мету потрібно досягнути протягом 6 міс., при умові, що лікування слід змодифікувати або цілком змінити, якщо немає покращення через 3 місяці його застосування.',
                'surgical': 'Розгляньте у разі:\n1) сильного болю, незважаючи на максимальну консервативну терапію;\n2) зруйнування суглобу, яке настільки обмежує об\'єм рухів, що призводить до тяжкого порушення мобільності. Види оперативних втручань: синовіектомія, реконструкційні або корекційні операції, артродез, алопластика.',
                'non-surgical': 'Потрібна модифікація способу життя. Основними препаратами в лікуванні вважаються хвороба-модифікуючі антиревматичні препарати: метотрексат, гідроксихлорохін, сульфасалазин, лефлуномід, інгібітори TNF-альфа (цертолізумаб, інфліксимаб та етанерцепт), абатацепт та анакінра. Ритуксимаб і тоцилізумаб є моноклональними антитілами. Застосування тоцилізумабу пов\'язане з ризиком підвищення рівня холестерину. Застосовуються також протизапальні та анальгетики. Проводиться фізіотерапія. У тяжких випадках застосовується корегуюче ортопедичне лікування.'
            } 
        },
        'rozryv_meniska': {
            'termin': 'Розрив меніска колінного суглоба – це пошкодження хрящових прошарків. Одна з найпоширеніших травм у спортсменів — досить одного сильного або різкого руху і навантаження, що створюється, пошкоджує меніск.\nСам по собі меніск – це хрящовий прошарок між кістками колінного суглоба (товщина 3-4 мм, довжина 6-8). І незважаючи на свої невеликі габарити, цей маленький хрящ має великий запас міцності. Але при значних фізичних навантаженнях або специфічних рухах травми меніска неминучі.',
            'symptoms': ['біль у коліні;', 'обмеження руху;', 'блокування суглоба;', 'набряк, припухлість (без змін кольору шкіри);', 'скупчення рідини;', 'клацання при згині ноги;'],
            'heal_method': {
                'main': 'Рішення про необхідність операції в разі розриву меніска колінного суглоба ухвалює лікар на підставі низки чинників, включно з характером і ступенем пошкодження меніска, віком пацієнта, його загальним станом здоров’я, наявністю інших захворювань та іншими факторами.',
                'surgical': 'Операція на меніск колінного суглоба може проводитися методом артроскопії – мінімально інвазивним методом, під час якого проводять невеликий розріз у ділянці коліна, через який вводять артроскопічний інструментарій.',
                'non-surgical': 'Носіння ортопедичного взуття або тейпування колінного суглоба, фізіотерапію, медикаментозну терапію та інші методи.'
            } 
        },
        'tenditit': {
            'termin': 'Тендиніт - це запалення товстих фіброзних ниток, які прикріплюють м\'яз до кістки. Ці тяжі називаються сухожиллями. Захворювання викликає біль і чутливість поза межами суглоба. Тендиніт може виникнути в будь-якому сухожиллі. Але найчастіше це відбувається навколо плечей, ліктів, зап’ясть, колін і п’ят.',
            'symptoms': ['біль, який часто описують як тупий біль, особливо під час руху ураженої кінцівки або суглоба;', 'легкий набряк;'],
            'heal_method': {
                'main': 'Лікування призначене для зменшення болю та чутливості, які виникають поза межами суглоба через захворювання.',
                'surgical': 'Це рідко потрібно і лише для серйозних симптомів, які не піддаються іншим методам лікування.',
                'non-surgical': 'Більшість тендинітів можна лікувати за допомогою відпочинку, фізіотерапії та ліків для зменшення болю. Тривале запалення сухожилля може призвести до розриву сухожилля. Розірване сухожилля може потребувати операції.'
            } 
        }
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
            'sickness': sickness_classification.get(third_layer),
            'sickness_heal': json.dumps(sickness_heal.get(third_layer)),
        }
    )