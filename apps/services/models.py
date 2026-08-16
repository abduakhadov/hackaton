from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Masalan: scissors, razor, comb (ixtiyoriy)"
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='services',
        verbose_name="Kategoriya"
    )
    name = models.CharField(max_length=150, verbose_name="Xizmat nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi (so'm)")
    duration_minutes = models.PositiveIntegerField(
        verbose_name="Davomiyligi (daqiqa)", default=30
    )
    image = models.ImageField(upload_to='services/', null=True, blank=True, verbose_name="Rasm")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} — {self.price} so'm"

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'pk': self.pk})
