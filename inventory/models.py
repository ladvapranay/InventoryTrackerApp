from django.contrib.auth.models import User
from django.db import models

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        db_table = 'inventory_item'

    #Meta class lets you define things about you model such as DB name, singular name etc

class InventoryRequest(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)  # Link to InventoryItem
    reason = models.TextField()
    priority = models.CharField(max_length=10, choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')])
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} requested by {self.requested_by}"

    class Meta:
        verbose_name = 'Inventory Request'
        verbose_name_plural = 'Inventory Requests'
        db_table = 'inventory_request'

class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'
        db_table = 'user_groups'


