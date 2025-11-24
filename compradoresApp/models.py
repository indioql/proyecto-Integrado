# compradoresApp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# IMPORTAMOS Producto REAL desde el artesano
from proyectoApp.models import Producto


class Order(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pendiente'),
        ('C', 'Completado'),
        ('R', 'Rechazado'),
    )

    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, related_name='orders', on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"Pedido #{self.id} - {self.product.nombre}"


class Review(models.Model):
    product = models.ForeignKey(Producto, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    artisan_response = models.TextField(blank=True)
    response_created_at = models.DateTimeField(null=True, blank=True)

    def respond(self, text):
        self.artisan_response = text
        self.response_created_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.author.username} -> {self.product.nombre} ({self.rating})"


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, related_name='favorited_by', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.nombre}"


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notif {self.user.username}: {self.message[:40]}"
