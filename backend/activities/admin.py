from django.contrib import admin
from .models import Activity, ActivitySlot, ActivityBlockedDate

admin.site.register(Activity)
admin.site.register(ActivitySlot)
admin.site.register(ActivityBlockedDate)