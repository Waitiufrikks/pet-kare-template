from django.db import models


class PetSexOptions(models.TextChoices):
    FEMALE = "Female"
    MALE = "Male"
    OTHER = "Not Informed"


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(
        max_length=20,
        blank=True,
        choices=PetSexOptions.choices,
        default=PetSexOptions.OTHER,
    )
    traits = models.ManyToManyField("traits.Trait", related_name="pet")
    group = models.ForeignKey(
        "groups.Group", on_delete=models.PROTECT, related_name="pets"
    )
