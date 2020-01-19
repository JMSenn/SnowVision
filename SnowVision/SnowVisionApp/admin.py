from django.contrib import admin
from SnowVisionApp.models import *
from django import forms

class SiteAdmin(admin.ModelAdmin):
    exclude=("lat","lng")
    readonly_fields=("number",)
    list_display = ('name', 'number',)
    list_filter = ('number',)
    search_fields = ('number','name')

class EcoRegionFourInline(admin.TabularInline):
    model = EcoRegionFour
    readonly_fields = ["region_type",]
    show_change_link = True

class EcoRegionThreeAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)
    inlines = [
        EcoRegionFourInline,
    ]

class EcoRegionFourAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name","excavator")
    search_fields = ("name",)
    filter_horizontal = ('site',)
    readonly_fields=("pk",)

class ContextAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)
    search_fields = ("site",)
    list_display=("name","site", "project",
    "recovery_method", "screen_type",
    "northing", "easting")

class RecoveryMethodAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class SherdAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at','pk')

class MatchPercentageAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class SymmetryAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class DesignAdmin(admin.ModelAdmin):
    filter_horizontal =('elements','design_reference')
    list_display = ("number","artist",)
    readonly_fields=("number",)
    search_fields = ("number",)

class DesignElementAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class ReferenceAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)
    list_display = ("title","journal","author_last_name","year",
                    "volume","page_numbers")

class JournalAdmin(admin.ModelAdmin):
    readonly_fields=("pk",)

class Sherd_CollectionInline(admin.TabularInline):
    model = Sherd_Collection
    readonly_fields = ["name",]
    show_change_link = True

class ProfileAdmin(admin.ModelAdmin):
    inlines =[
        Sherd_CollectionInline
    ]

class SherdInline(admin.TabularInline):
    model = Sherd
    exclude = ["profile"]
    readonly_fields = ["pk","context","overstamped","design","rgb_image","dimensional_data","private"]
    show_change_link = True
    def has_add_permission(self,request):
        return False

    def has_delete_permission(self,request,obj = None):
        return True

class Sherd_CollectionAdmin(admin.ModelAdmin):
    inlines = [
        SherdInline,
    ]

class ProfileInline(admin.TabularInline):
    model = Profile
    readonly_fields = ["affiliation","bio","user"]
    show_change_link = True

    def has_add_permission(self,request):
        return False

class AffiliationAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline,
    ]


admin.site.register(Site,SiteAdmin)
admin.site.register(EcoRegionThree,EcoRegionThreeAdmin)
admin.site.register(EcoRegionFour,EcoRegionFourAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Context,ContextAdmin)
admin.site.register(RecoveryMethod,RecoveryMethodAdmin)
admin.site.register(Sherd, SherdAdmin)
admin.site.register(MatchPercentage,MatchPercentageAdmin)
admin.site.register(Symmetry,SymmetryAdmin)
admin.site.register(Design,DesignAdmin)
admin.site.register(DesignElement, DesignElementAdmin)
admin.site.register(Reference,ReferenceAdmin)
admin.site.register(Journal,JournalAdmin)
admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(Sherd_Collection,Sherd_CollectionAdmin)
admin.site.register(Profile,ProfileAdmin)
