from django.contrib import admin
from .models import Order, Review, Favorite, Notification

admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(Notification)
