from django.db import models


# Create your models here.
class PetSexOptions(models.TextChoices):
    FEMALE = "Female"
    MALE = "Male"
    OTHER = "Not Informed"


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    weight = models.FloatField(null=True)
    sex = models.CharField(
        max_length=20,
        choices=PetSexOptions.choices, 
        default=PetSexOptions.OTHER
    )
    
    group = models.ForeignKey(
        "groups.Group", on_delete=models.PROTECT, related_name="pets"
    )
