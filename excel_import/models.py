from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='attributes')

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    name = models.CharField(max_length=255)
    # slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ProductBarcode(models.Model):
    name = models.CharField(max_length=255, unique=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='barcodes')


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    # image = models.ImageField(upload_to='products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    tags = models.ManyToManyField('ProductTag', blank=True)

    def __str__(self):
        return self.name
