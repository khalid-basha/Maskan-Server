from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from notifications.models import UserDevicesToken


# Create your views here.
@api_view(['POST'])
def create_or_update_token(request, pk):
    if 'token_id' not in request.data:
        return JsonResponse({'error': 'Token ID is required.'}, 400)

    token_id = request.data['token_id']
    try:
        token, created = UserDevicesToken.objects.get_or_create(user_id=pk, defaults={'token': token_id})

        if created:
            return JsonResponse({'message': 'Token created successfully.'}, status=201)
        else:
            token.token = token_id
            token.save()
            return JsonResponse({'message': f'Token with ID {token_id} updated successfully.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
