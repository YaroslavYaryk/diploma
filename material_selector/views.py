import json

from django.db.models import F
from django.http import JsonResponse

from django.views.generic import (
    View,
    TemplateView
)

ADDITIONAL_WEIGHT = 5

from .models import MaterialComponent, Material

class MaterialSelection:
    
    @staticmethod
    def add_rank_to_materials(storage, materials):
        for material in materials:
            storage[material.name] += 1
            
    def get_queryset(self, has_allergy, alergies):
        materials = Material.objects.all()
        if has_allergy:
            materials = materials.exclude(material_component__name__in=alergies)
            
        return materials
            
        
    def select_plastic(self, body):
        has_allergy = body.get('has_alergy')
        allergies = body.get('alergies')
        sports = body.get('sports')
        activity_level = body.get('activity_level')
        
        materials = self.get_queryset(has_allergy, allergies).filter(material_type__name__in=["Пластик", "Еластомер"])
        
        materials_storage = {
            'Пластик': 0,
            'Еластомер': 0
        }


        if sports:
            if 'Водні види спорту' in sports or 'Біг або активний спорт' in sports or 'Ходьба та повсякденна активність' in sports:
                materials_storage['Еластомер'] += 1
            if 'Екстремальні види спорту' in sports or 'Тяжка атлетика та силові тренування' in sports:
                materials_storage['Пластик'] += 1
        
        if activity_level == 'Висока' or activity_level == 'Середня':
            materials_storage['Пластик'] += 1
        elif activity_level == 'Низька':
            materials_storage['Еластомер'] += 1

            
        
        best_material_type = sorted(materials_storage.items(), key=lambda x:x[1])[-1]
        
        best_material_type_name = best_material_type[0]
        
        best_material = materials.filter(material_type__name=best_material_type_name).annotate(
            total_weight=(
                F('bio_compatibility') + F('strength_durability') + F('wear_resistance') +
                F('elasticity_modulus') + F('corrosion_resistance')
            )
        ).order_by('-total_weight').first()
        
        return best_material
            
    @staticmethod
    def material_combination_info():
        return {
            "Метал__Метал": {
                "Переваги": ["Чудово підходить для пацієнтів з великою вагою", "Дуже міцні, відносно інших комбінацій", "Зазвичай дешевші, ніж керамічні"],
                "Недоліки": ["Менша біосумісність", "Сильніше зноситься, ніж його аналоги", "Більший ризик виникнення ускладнень в процесі зношення", "Зазвичай, потребують більшої кількості ревізійних операцій, за інші"]
            },
            "Кераміка__Кераміка": {
                "Переваги": ["Керамічні імплантати цінуються за гладку поверхню, яка зменшує зношування навколишніх тканин і потенційно знижує ризик розхитання імплантату з часом",
                             "Керамічні протези продемонстрували багатообіцяючі результати щодо мінімізації зносу імплантату та протилежної поверхні суглоба",
                             "Керамічні імпланти, будучи біологічно інертними, рідше викликають алергічні реакції",
                             "Стійкіші до зламу і зношення відносно аналогів",
                             "Гладка поверхня керамічних протезів може сприяти кращій стабільності та зменшити ризик розхитування або поломки протезу з часом",
                             "Потребують меншої кількості ревізійних операцій, ніж металеві"
                            ],
                "Недоліки": ["Можуть видавати скрип під час ходьби з часом, проте це можна виправити хірургічним втручанням",
                             "У рідкісних випадках вони можуть розколотися під сильним тиском на частини, які необхідно видалити хірургічним шляхом",
                             "Найдорожчі з усіх типів"]
            },
            "Кераміка__Пластик": {
                "Переваги": ["Відсутність нікелю, тому може бути використаний для людей, які мають алергічну реакцію на металеві імпланти.",
                             "Дешевший від цілковито керамічного",
                            ],
                "Недоліки": ["Імунна реакція через стирання пластмасових частин."]
            },
            "Метал__Пластик": {
                "Переваги": ["Найбільш доступний тип імпланту, оскільки він є найдешевшим",
                             "Має найдовший історічний досвід безпеки та тривалості експлуатації",
                             "Використовуються метали, які мають високу стійкість до зношування"],
                "Недоліки": ["Можливість виникнення імунної реакції через стирання часток пластику, що може призвести до руйнування кістки та відшарування імпланту",
                             "Полімерні частки можуть також спричинити імунну реакцію"]
            }
        }
    
    def select_materials(self, body):
        has_allergy = body.get('has_alergy')
        allergies = body.get('alergies')
        sports = body.get('sports')
        activity_level = body.get('activity_level')
        weight = int(body.get('weight'))
        height = int(body.get('heigh'))
        age = int(body.get('age'))
        skin_type = body.get('skin_type')
        skin_moisture = body.get('skin_moisture')
        

        # Фільтруємо матеріали за алергіями
        materials = self.get_queryset(has_allergy, allergies)
        
        materials_storage = {
            material.name: 0 for material in materials
        }

        # Додаткові фільтри на основі параметрів
        if sports:
            if 'Водні види спорту' in sports:
                test_materials = materials.filter(strength_durability__gte=3, wear_resistance__gte=3, corrosion_resistance__gte=4)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Біг або активний спорт' in sports:
                test_materials = materials.filter(strength_durability__gte=4, wear_resistance__gte=4, elasticity_modulus__gte=4)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Ходьба та повсякденна активність' in sports:
                test_materials = materials.filter(strength_durability__gte=3, wear_resistance__gte=3)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Екстремальні види спорту' in sports:
                test_materials = materials.filter(strength_durability__gte=5, wear_resistance__gte=4)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Тяжка атлетика та силові тренування' in sports:
                test_materials = materials.filter(strength_durability__gte=5, wear_resistance__gte=5, elasticity_modulus__gte=4)
                self.add_rank_to_materials(materials_storage, test_materials)


        if activity_level == 'Висока':
            test_materials = materials.filter(strength_durability__gte=4, wear_resistance__gte=5)
            self.add_rank_to_materials(materials_storage, test_materials)
        if activity_level == 'Середня':
            test_materials = materials.filter(strength_durability__gte=3, wear_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if activity_level == 'Низька':
            test_materials = materials.filter(strength_durability__gte=2, wear_resistance__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)

        if weight > 80:
            test_materials = materials.filter(elasticity_modulus__gte=3)  
            self.add_rank_to_materials(materials_storage, test_materials)
        if weight > 100:
            test_materials = materials.filter(elasticity_modulus__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if weight > 120:
            test_materials = materials.filter(elasticity_modulus__gte=5)
            self.add_rank_to_materials(materials_storage, test_materials)
            
        if skin_type == 'Нормальна':
            test_materials = materials.filter(bio_compatibility__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if skin_type == 'Чутлива':
            test_materials = materials.filter(bio_compatibility__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if skin_type == 'Проблемна':
            test_materials = materials.filter(bio_compatibility__gte=5)
            self.add_rank_to_materials(materials_storage, test_materials)

        if skin_moisture == 'Суха':
            test_materials = materials.filter(corrosion_resistance__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if skin_moisture == 'Нормальна волога':
            test_materials = materials.filter(corrosion_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if skin_moisture == 'Жирна':
            test_materials = materials.filter(corrosion_resistance__gte=5)
            self.add_rank_to_materials(materials_storage, test_materials)

        if height > 170:
            test_materials = materials.filter(elasticity_modulus__gte=2)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 180:
            test_materials = materials.filter(elasticity_modulus__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 190:
            test_materials = materials.filter(elasticity_modulus__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 200:
            test_materials = materials.filter(elasticity_modulus__gte=5)
            self.add_rank_to_materials(materials_storage, test_materials)

        if age > 30:
            test_materials = materials.filter(elasticity_modulus__gte=3, wear_resistance__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if age > 40:
            test_materials = materials.filter(elasticity_modulus__gte=4, wear_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if age > 60:
            test_materials = materials.filter(elasticity_modulus__gte=5, wear_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
            

        # Вибір найкращого матеріалу з урахуванням вагомості кожного параметру
        sorted_materials = materials.annotate(
            total_weight=(
                F('bio_compatibility') + F('strength_durability') + F('wear_resistance') +
                F('elasticity_modulus') + F('corrosion_resistance')
            )
        ).order_by('-total_weight')

        print([(el.name, el.total_weight) for el in sorted_materials])
        print(materials_storage)

        elem_by_materials = self.elem_by_materials_calc(sorted_materials)
        prosthesis_by_materials = self.prosthesis_by_materials_calc(elem_by_materials)
        prosthesis_by_materials = self.get_classified_materials(prosthesis_by_materials, age, weight, height, sports, None)
        prosthesis_by_materials = self.get_calculated_material_combination(materials_storage, prosthesis_by_materials)

        for i in prosthesis_by_materials.keys():
            print(f"{i} :{prosthesis_by_materials.get(i)}\n")

        best_materials = self.get_best_materials(prosthesis_by_materials)
        knee_fixation = self.get_knee_fixation_type(age, weight, height, activity_level, None)

        best_knee_fixation = sorted(knee_fixation.items(), key=lambda x: x[1], reverse=True)[0]

        return best_materials, best_knee_fixation

    @staticmethod
    def serialize_material(material): 
        return {
            'id': material.id,
            'name': material.name
        }
    
    @staticmethod
    def serialize_manterial_and_type_connection(material__and_type_connection): 
        return {
            'materials': material__and_type_connection[0],
            'connection': material__and_type_connection[1]
        }
    
    def get_calculated_material_combination(self, materials_storage, prosthesis_by_materials):
        
        for combination, elements in prosthesis_by_materials.items():
            for elem in elements:
                material1, material2 = elem.get('name', '__').split('__')
                material1_score = materials_storage.get(material1, 0)
                material2_score = materials_storage.get(material2, 0)
                elem['total_weight'] += material1_score + material2_score

        return prosthesis_by_materials

    def get_knee_fixation_type(self, age, weight, heigh, activity, ilness=None):
        storage = {
            'Цементований': 0,
            'Безцементований': 0,
            'Гібридний': 0
        }

        HYBRID = 8

        BMI = self.get_bmi(weight, heigh)

        # by age
        if age < 50:
            storage['Безцементований'] += 10
            storage['Гібридний'] += HYBRID

        elif age >= 50:
            storage['Цементований'] += 10
            storage['Гібридний'] += HYBRID


        # by activity
        if activity == "Низька":
            storage['Цементований'] += 10
            storage['Гібридний'] += HYBRID
        elif activity in ("Середня", "Висока"):
            storage['Безцементований'] += 15
            storage['Гібридний'] += HYBRID


        # by ilness        
        if ilness == "oasteoartritus":
            storage['Цементований'] += 30


        # by mbi
        elif BMI >= 25:
            storage['Цементований'] += 21
        
        else:
            storage['Гібридний'] += HYBRID + 2  # 10
            storage['Безцементований'] += HYBRID + 2  # 10

        return storage



    @staticmethod
    def get_bmi(weight, heigh):
        return weight / ((heigh / 100) ** 2)
    
    def get_classified_materials(self, prosthesis_by_materials, age, weight, heigh, sports, price):

        BMI = self.get_bmi(weight, heigh) 

        # add additional weights by age
        if age < 20:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 5

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 5
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 3
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 1

        elif age < 35:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 3

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 3
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 1
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 5
                
        elif age < 60:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 3

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 3
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 1
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 4
                
        else:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 5

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 5
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 3
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 1


        if weight >= 100:
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 5
   
            

        if BMI > 40:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] -= 1

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] -= 1
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 5
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] -= 1

        elif BMI > 30:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 2

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 1
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 5
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 4

        elif BMI > 25:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 4

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 2
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 1
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 4
        else:
            elems = prosthesis_by_materials.get('Метал__Пластик', [])
            for el in elems:
                el['total_weight'] += 2

            elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
            for el in elems:
                el['total_weight'] += 4
                
            elems = prosthesis_by_materials.get('Метал__Метал', [])
            for el in elems:
                el['total_weight'] += 1
                
            elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
            for el in elems:
                el['total_weight'] += 4

        if sports:
            if 'Водні види спорту' in sports:
                elems = prosthesis_by_materials.get('Метал__Пластик', [])
                for el in elems:
                    el['total_weight'] += 3

                elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
                for el in elems:
                    el['total_weight'] += 3

                elems = prosthesis_by_materials.get('Метал__Метал', [])
                for el in elems:
                    el['total_weight'] += 1

                elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
                for el in elems:
                    el['total_weight'] += 5
            if 'Біг або активний спорт' in sports:
                elems = prosthesis_by_materials.get('Метал__Пластик', [])
                for el in elems:
                    el['total_weight'] += 3

                elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
                for el in elems:
                    el['total_weight'] += 3

                elems = prosthesis_by_materials.get('Метал__Метал', [])
                for el in elems:
                    el['total_weight'] -= 1

                elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
                for el in elems:
                    el['total_weight'] += 5
            if 'Ходьба та повсякденна активність' in sports:
                elems = prosthesis_by_materials.get('Метал__Пластик', [])
                for el in elems:
                    el['total_weight'] += 5

                elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
                for el in elems:
                    el['total_weight'] += 5

                elems = prosthesis_by_materials.get('Метал__Метал', [])
                for el in elems:
                    el['total_weight'] -= 1

                elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
                for el in elems:
                    el['total_weight'] += 5
                
            if 'Тяжка атлетика та силові тренування' in sports:
                elems = prosthesis_by_materials.get('Метал__Пластик', [])
                for el in elems:
                    el['total_weight'] += 2

                elems = prosthesis_by_materials.get('Кераміка__Пластик', [])
                for el in elems:
                    el['total_weight'] += 1

                elems = prosthesis_by_materials.get('Метал__Метал', [])
                for el in elems:
                    el['total_weight'] += 12

                elems = prosthesis_by_materials.get('Кераміка__Кераміка', [])
                for el in elems:
                    el['total_weight'] += 3


        return prosthesis_by_materials

    def get_best_materials(self, prosthesis_by_materials):

        materials = list(prosthesis_by_materials.values())
        materials_list = [item for sublist in materials for item in sublist]    

        print(materials, '__--___---__---__--__--__--___-__--___----')
        sorted_materials = sorted(materials_list, key=lambda x: x['total_weight'], reverse=True)
        if len(sorted_materials) >= 4:
            return sorted_materials[0:4]
        return sorted_materials
    
    def elem_by_materials_calc(self, best_materials):
        elem_by_materials = {
            "Метал": [],
            "Пластик": [],
            "Кераміка": [],
        }
        for el in best_materials:
            material_name = el.material_type.name
            elem_by_materials.setdefault(material_name, []).append({"name": el.name, "total_weight": el.total_weight})
        
        return elem_by_materials

    def prosthesis_by_materials_calc(self, elem_by_materials):
        material_combinations = [('Метал', 'Метал'), ('Метал', 'Пластик'), ('Кераміка', 'Кераміка'), ('Кераміка', 'Пластик')]
        prosthesis_by_materials = {}
        
        for material1, material2 in material_combinations:
            prosthesis_name = f"{material1}__{material2}"
            prosthesis_list = []

            for elem1 in elem_by_materials[material1]:
                for elem2 in elem_by_materials[material2]:
                    name = f"{elem1['name']}__{elem2['name']}"


                    if elem1['name'] == elem2['name'] and prosthesis_name in ["Метал__Метал", "Кераміка__Кераміка"]: 
                        total_weight = elem1["total_weight"] + elem2["total_weight"]
                        prosthesis_list.append({"name": name, "total_weight": total_weight, "type": prosthesis_name})
                    elif prosthesis_name in ["Метал__Пластик", "Кераміка__Пластик"]:
                        reverse_name = f"{elem2['name']}__{elem1['name']}"
                        if any(item['name'] == reverse_name for item in prosthesis_list):
                            continue

                        total_weight = elem1["total_weight"] + elem2["total_weight"]
                        prosthesis_list.append({"name": name, "total_weight": total_weight, "type": prosthesis_name})

            prosthesis_by_materials[prosthesis_name] = prosthesis_list

        return prosthesis_by_materials


class SelectMaterialForCustomer(View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    def get_filtered_materials_by_allergies(self, has_alergy, allergies):
        qs = Material.objects.all()
        if has_alergy:
            qs = qs.exclude(material_component__name__in=allergies)
        
        return qs
    
    def get_material_based_on_sport_and_activity_level(self, materials,  sports, activity_level):
        
        result_materials = materials
        if 'Водні види спорту' in sports:
            result_materials = result_materials.filter(corrosion_resistance__gte=4)
        

    def post(self, request, *args, **kwargs):
        
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        has_alergy = body.get('has_alergy')
        alergies = body.get('alergies')
        sports = body.get('sports')
        activity_level = body.get('activity_level')
        weight = body.get('weight')
        heigh = body.get('heigh')
        age = body.get('age')
        skin_type = body.get('skin_type')
        skin_moisture = body.get('skin_moisture')
        # price = body.get('price')
        
        
        material_selection = MaterialSelection()
        
        outer_part = material_selection.select_materials(body)
        
        inner_part = material_selection.select_plastic(body)

        material_combination_info = material_selection.material_combination_info()
        
        
        return JsonResponse({
            'inner_part': json.dumps(material_selection.serialize_material(inner_part)),
            'outer_part': json.dumps(material_selection.serialize_manterial_and_type_connection(outer_part)),
            'material_combination_info': json.dumps(material_combination_info),
        })


# Create your views here.
class MaterialSelectorView(TemplateView):
    template_name = "material_selector/main.html"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def serialize_component(self, component):
        return {
            "id": component.id,
            "name": component.name,
        }
        


    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        
        material_components = MaterialComponent.objects.all()
        serialized_components = [self.serialize_component(component) for component in material_components]
            
        cd['checkbox_values'] = json.dumps([{'name': 'Jake', 'selected': True}, {'name': 'Jacob', 'selected': False}, {'name': 'Jane', 'selected': True}])
        cd['components'] = json.dumps(serialized_components)
        cd['activity_values'] = json.dumps(['Ходьба та повсякденна активність', 'Біг або активний спорт', 'Водні види спорту', 'Екстремальні види спорту', 'Тяжка атлетика та силові тренування'])
        cd['activity_levels'] = json.dumps(['Низька', 'Середня', 'Висока'])
        # cd['muscles_type'] = json.dumps(['Слабкі', 'Середні', 'Сильні'])
        cd['skin_types'] = json.dumps(['Нормальна', 'Чутлива', 'Проблемна'])
        cd['skin_moistures'] = json.dumps(['Суха', 'Нормальна волога', 'Жирна'])

        return cd


