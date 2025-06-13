from django.contrib import admin
from .models import (
    Village, Area, Farmer, Labor, Tractor, Skill,
    TractorSkill, Requirement, Bid, BidComment
)


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('id', 'village_name')


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_name', 'area_type', 'village')
    list_filter = ('area_type', 'village')


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact_number')
    filter_horizontal = ('villages', 'areas')


@admin.register(Labor)
class LaborAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact_number', 'village', 'area', 'hourly_rate', 'gender')
    list_filter = ('village', 'area', 'gender')


@admin.register(Tractor)
class TractorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact_number')
    filter_horizontal = ('villages',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'skill_name', 'skill_type',
        'hourly', 'lump_sump', 'per_bigha', 'per_day', 'per_weight'
    )
    list_filter = ('skill_type',)


@admin.register(TractorSkill)
class TractorSkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'tractor', 'skill')
    list_filter = ('skill',)


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'area', 'skill', 'from_date', 'to_date', 'shift', 'is_open')
    list_filter = ('shift', 'is_open', 'from_date', 'to_date')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'requirement', 'labor', 'tractor',
        'hourly', 'lump_sump', 'per_bigha', 'per_day', 'per_weight',
        'male_labors', 'female_labors',
        'is_accepted_by_farmer', 'is_accepted_by_labor'
    )
    list_filter = ('is_accepted_by_farmer', 'is_accepted_by_labor')


@admin.register(BidComment)
class BidCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'bid', 'posted_by', 'created_at')
    list_filter = ('posted_by', 'created_at')
