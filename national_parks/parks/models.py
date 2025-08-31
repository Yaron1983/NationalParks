from django.db import models
from django.conf import settings

class Park(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    official_website = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='parks/', blank=True, null=True)
    flag = models.ImageField(upload_to='flags/', blank=True, null=True)

    def __str__(self):
        return self.name

class ParkIdentifier(models.Model):
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name="identifiers")
    source_name = models.CharField(max_length=100)
    source_id = models.CharField(max_length=100)
    class Meta:
        unique_together = ("source_name", "source_id")


class Rating(models.Model):
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('park', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.park.name} as {self.score}"

