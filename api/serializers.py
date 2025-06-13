from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User, Group
from .models import *
from .permissions import user_in_group


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = UserSerializer(self.user).data
        data.update(user_data)
        return data


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ["id", "village_name"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'area_name', 'area_type', 'village']

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = [
            'id', 'requirement', 'labor', 'tractor',
            'description', 'hourly', 'lump_sump', 'per_bigha', 'per_day', 'per_weight',
            'male_labors', 'female_labors', 'date',
            'is_accepted_by_farmer', 'is_accepted_by_labor'
        ]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id","skill_name","skill_type","hourly",
            "lump_sump","per_bigha","per_day","per_weight",
        ]



class RequirementSerializer(serializers.ModelSerializer):
    area_name = serializers.SerializerMethodField()
    skill_name = serializers.SerializerMethodField()
    requirement_type = serializers.SerializerMethodField()
    can_update = serializers.SerializerMethodField() 
    farmer_rating = serializers.SerializerMethodField()

    hired_labor_id = serializers.IntegerField(source='hire_labor.id', read_only=True)
    hired_labor_name = serializers.SerializerMethodField()
    hired_tractor_id = serializers.IntegerField(source='hire_tractor.id', read_only=True)
    hired_tractor_name = serializers.SerializerMethodField()

    class Meta:
        model = Requirement
        fields = [
            'id', 'title', 'description', 'area', 'skill',
            'area_name', 'skill_name', 'land_size',
            'from_date', 'to_date', 'shift',
            'number_of_labors', 'has_pickup', 'snacks_facility',
            'is_open', 'requirement_type', 'can_update',
            'hired_labor_id', 'hired_labor_name',
            'hired_tractor_id', 'hired_tractor_name',
            'farmer_rating'
        ]

    def get_farmer_rating(self, obj):
        if not obj.farmer or not obj.skill:
            return None
        skill_type = obj.skill.skill_type
        ratings = Requirement.objects.filter(
            farmer=obj.farmer,
            skill__skill_type=skill_type,
            farmer_rating__isnull=False
        ).values_list('farmer_rating', flat=True)
        ratings = list(ratings)
        return round(sum(ratings) / len(ratings), 2) if ratings else None

    def get_area_name(self, obj):
        return obj.area.area_name if obj.area else None

    def get_skill_name(self, obj):
        return obj.skill.skill_name if obj.skill else None

    def get_requirement_type(self, obj):
        if obj.skill:
            return obj.skill.skill_type
        return "unknown"

    def get_can_update(self, obj):
        return obj.is_open and not Bid.objects.filter(requirement=obj).exists()

    def get_hired_labor_name(self, obj):
        return f"{obj.hire_labor.user.first_name} {obj.hire_labor.user.last_name}" if obj.hire_labor else None

    def get_hired_tractor_name(self, obj):
        return f"{obj.hire_tractor.user.first_name} {obj.hire_tractor.user.last_name}" if obj.hire_tractor else None



class LaborRequirementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'title', 'description', 'area', 'skill', 'land_size',
            'from_date', 'to_date', 'shift',
            'number_of_labors', 'has_pickup', 'snacks_facility', 'is_open'
        ]

class TractorRequirementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'title', 'description', 'area', 'skill', 'land_size',
            'from_date', 'to_date', 'shift', 'is_open'
        ]

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    village_ids = serializers.SerializerMethodField()
    areas_with_villages = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()  # ✅ new

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
            'village_ids',
            'areas_with_villages',
            'average_rating'  # ✅ include in output
        ]

    def get_role(self, obj):
        if user_in_group(obj, 'farmer'):
            return 'farmer'
        elif user_in_group(obj, 'labor'):
            return 'labor'
        elif user_in_group(obj, 'tractor'):
            return 'tractor'
        return 'unknown'

    def get_village_ids(self, obj):
        if user_in_group(obj, 'farmer'):
            return list(obj.farmer.villages.values_list('id', flat=True))
        elif user_in_group(obj, 'labor'):
            return [obj.labor.village_id]
        elif user_in_group(obj, 'tractor'):
            return list(obj.tractor.villages.values_list('id', flat=True))
        return []

    def get_areas_with_villages(self, obj):
        if not user_in_group(obj, 'farmer'):
            return []

        farmer = getattr(obj, 'farmer', None)
        if not farmer:
            return []

        areas = farmer.areas.select_related('village').all()
        village_map = {}

        for area in areas:
            village = area.village
            if village.id not in village_map:
                village_map[village.id] = {
                    "village_id": village.id,
                    "label": village.village_name,
                    "options": []
                }

            village_map[village.id]["options"].append({
                "value": area.id,
                "label": area.area_name
            })

        return list(village_map.values())

    def get_average_rating(self, obj):
        if user_in_group(obj, 'farmer') and hasattr(obj, 'farmer'):
            ratings = Requirement.objects.filter(
                farmer=obj.farmer,
                farmer_rating__isnull=False
            ).values_list('farmer_rating', flat=True)        

        else:
            return None

        ratings = list(ratings)
        if not ratings:
            return None

        avg = sum(ratings) / len(ratings)
        return round(avg, 2)


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["farmer", "labor", "tractor"])

    # Farmer and Tractor - multiple
    village_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    area_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    # Labor - single
    village_id = serializers.IntegerField(required=False)
    area_id = serializers.IntegerField(required=False)

    # Labor-specific fields
    gender = serializers.ChoiceField(choices=["male", "female"], required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    # Tractor-specific fields
    skill_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    def validate(self, data):
        role = data["role"]

        if role == "labor":
            missing = [field for field in ["village_id", "area_id", "gender", "hourly_rate"] if not data.get(field)]
            if missing:
                raise serializers.ValidationError(f"Missing fields for labor registration: {', '.join(missing)}")

        elif role == "farmer":
            if not data.get("village_ids"):
                raise serializers.ValidationError({"village_ids": ["This field is required."]})

        elif role == "tractor":
            if not data.get("village_ids"):
                raise serializers.ValidationError({"village_ids": ["This field is required."]})
            if not data.get("skill_ids"):
                raise serializers.ValidationError({"skill_ids": ["This field is required."]})

            # Optional validation for tractor skills
            invalid_skills = Skill.objects.filter(id__in=data["skill_ids"]).exclude(skill_type="tractor")
            if invalid_skills.exists():
                raise serializers.ValidationError({"skill_ids": "Contains non-tractor skills."})

        return data

    def create(self, validated_data):
        role = validated_data.pop("role")
        full_name = validated_data.pop("full_name")
        first_name, *last_name = full_name.split(" ", 1)
        last_name = last_name[0] if last_name else ""

        phone_number = validated_data.pop("phone_number")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        group = Group.objects.get(name=role)
        user.groups.add(group)

        if role == "farmer":
            farmer = Farmer.objects.create(user=user, contact_number=phone_number)
            village_ids = validated_data.get("village_ids", [])
            area_ids = validated_data.get("area_ids", [])
            if village_ids:
                farmer.villages.set(village_ids)
            if area_ids:
                farmer.areas.set(area_ids)

        elif role == "labor":
            Labor.objects.create(
                user=user,
                contact_number=phone_number,
                village_id=validated_data["village_id"],
                area_id=validated_data["area_id"],
                gender=validated_data["gender"],
                hourly_rate=validated_data["hourly_rate"],
            )

        elif role == "tractor":
            tractor = Tractor.objects.create(user=user, contact_number=phone_number)
            village_ids = validated_data.get("village_ids", [])
            if village_ids:
                tractor.villages.set(village_ids)
            skill_ids = validated_data.get("skill_ids", [])
            for skill_id in skill_ids:
                TractorSkill.objects.create(tractor=tractor, skill_id=skill_id)

        return user
    