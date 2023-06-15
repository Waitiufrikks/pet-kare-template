from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response, Request, status
from pets.models import Pet, PetSexOptions
from groups.models import Group
from traits.models import Trait
from pets.serializers import PetSerializer
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        instance_group, _ = Group.objects.get_or_create(**group_data)

        instance_pet = Pet.objects.create(
            **serializer.validated_data, group=instance_group
        )

        for trait in traits_data:
            instance_traits = Trait.objects.filter(name__iexact=trait["name"]).first()

            if not instance_traits:
                instance_traits = Trait.objects.create(**trait)
            instance_pet.traits.add(instance_traits)

        pet_serializer = PetSerializer(instance_pet)
        return Response(pet_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()
        trait_name = request.query_params.get("trait")

        if trait_name:
            pets = pets.filter(traits__name__iexact=trait_name)

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializer(instance=result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetail(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet_found = get_object_or_404(Pet, id=pet_id)

        pet_serializer = PetSerializer(instance=pet_found)

        return Response(pet_serializer.data, status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        serializer = PetSerializer(data=request.data, partial=True)
        pet_found = get_object_or_404(Pet, id=pet_id)
        serializer.is_valid(raise_exception=True)
        choices = PetSexOptions.choices

        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        if group:
            group_obj = Group.objects.filter(
                scientific_name__iexact=group["scientific_name"]
            ).first()
            if not group_obj:
                group_obj = Group.objects.create(**group)
            pet_found.group = group_obj

        if traits:
            trait_list = []
            for trait in traits:
                trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()
                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait)
                trait_list.append(trait_obj)
            pet_found.traits.set(trait_list)

        for key, value in serializer.validated_data.items():
            setattr(pet_found, key, value)

        pet_found.save()

        serializer = PetSerializer(instance=pet_found)
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet_found = get_object_or_404(Pet, id=pet_id)
        pet_found.delete()
        return Response({}, status.HTTP_204_NO_CONTENT)
