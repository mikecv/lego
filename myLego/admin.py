from django.contrib import admin

from .models import Colour, PartType, MyPart, Set, SetPart

admin.site.register(Colour)
admin.site.register(PartType)
admin.site.register(MyPart)
admin.site.register(Set)
admin.site.register(SetPart)