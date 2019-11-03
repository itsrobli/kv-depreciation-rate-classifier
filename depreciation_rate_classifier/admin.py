from django.contrib import admin

# Register your models here.
from .models import UserInput, MlLog, UserConfirmation

admin.site.register(UserInput)
admin.site.register(MlLog)
admin.site.register(UserConfirmation)
