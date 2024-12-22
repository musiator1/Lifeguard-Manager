from django.contrib import admin

from .models import Pool, Lifeguard, Shift, Application, Incident

admin.site.register(Pool)
admin.site.register(Lifeguard)
admin.site.register(Shift)
admin.site.register(Application)
admin.site.register(Incident)
