from rest_framework.views import APIView, Response, Request, status
from pets.models import Pet
from groups.models import Group
from traits.models import Trait
from pets.serializers import PetSerializer
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")
        
        instance_group, _ = Group.objects.get_or_create(**group_data)
        
        # adiciona o pet no grupo
        instance_pet = Pet.objects.create(**serializer.validated_data, group=instance_group)
        
        for trait in traits_data:
            instance_traits = Trait.objects.filter(name__iexact=trait['name']).first()

            if not  instance_traits:
                instance_traits = Trait.objects.create(**trait)
            instance_pet.traits.add(instance_traits)
            
        pet_serializer = PetSerializer(instance_pet)
        return Response(pet_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets,request)

        serializer = PetSerializer(instance=result_page, many=True)
        return self.get_paginated_response(serializer.data)
