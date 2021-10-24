from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    show_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Gift(models.Model):
    category = models.ForeignKey('category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=25)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    weight = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    rating = models.ValueRange(start=1, end=5)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField()

    def __str__(self):
        return self.name
