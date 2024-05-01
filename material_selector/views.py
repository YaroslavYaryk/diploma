import json
from pprint import pprint

from django.db.models import F
from django.shortcuts import render
from django.http import JsonResponse

from django.views.generic import (
    View,
    TemplateView
)

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
                test_materials = materials.filter(strength_durability__gte=4, wear_resistance__gte=4, elasticity_modulus__lte=4)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Ходьба та повсякденна активність' in sports:
                test_materials = materials.filter(strength_durability__gte=3, wear_resistance__gte=3)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Екстремальні види спорту' in sports:
                test_materials = materials.filter(strength_durability__gte=5, wear_resistance__gte=4)
                self.add_rank_to_materials(materials_storage, test_materials)
            if 'Тяжка атлетика та силові тренування' in sports:
                test_materials = materials.filter(strength_durability__gte=5, wear_resistance__gte=5, elasticity_modulus__lte=4)
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
            test_materials = materials.filter(elasticity_modulus__lte=3)  
            self.add_rank_to_materials(materials_storage, test_materials)
        if weight > 100:
            test_materials = materials.filter(elasticity_modulus__lte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if weight > 120:
            test_materials = materials.filter(elasticity_modulus__lte=5)
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
            test_materials = materials.filter(elasticity_modulus__lte=2)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 180:
            test_materials = materials.filter(elasticity_modulus__lte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 190:
            test_materials = materials.filter(elasticity_modulus__lte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if height > 200:
            test_materials = materials.filter(elasticity_modulus__lte=5)
            self.add_rank_to_materials(materials_storage, test_materials)

        if age > 30:
            test_materials = materials.filter(elasticity_modulus__lte=3, wear_resistance__gte=3)
            self.add_rank_to_materials(materials_storage, test_materials)
        if age > 40:
            test_materials = materials.filter(elasticity_modulus__lte=4, wear_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
        if age > 60:
            test_materials = materials.filter(elasticity_modulus__lte=5, wear_resistance__gte=4)
            self.add_rank_to_materials(materials_storage, test_materials)
            

        # Вибір найкращого матеріалу з урахуванням вагомості кожного параметру
        best_materials = materials.annotate(
            total_weight=(
                F('bio_compatibility') + F('strength_durability') + F('wear_resistance') +
                F('elasticity_modulus') + F('corrosion_resistance')
            )
        ).order_by('-total_weight')
        
        print([(el.name, el.total_weight, el.material_type.name) for el in best_materials])
        

        return best_materials.first()


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
        
        print(outer_part, inner_part)
        
        # materials = self.get_filtered_materials_by_allergies(has_alergy, alergies)
        # materials = self.get_material_based_on_sport_and_activity_level(materials, sports, activity_level)
        
        
        
        return JsonResponse({'date': 'OK'})


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
