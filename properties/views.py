from functools import reduce
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from notifications.models import home_favourite
from properties.models import Home, Features
from properties.serializers import HomeCardsSerializer, HomeSerializer, \
    HomeImageAndOwnershipUploadSerializer, HomeRepresentationSerializer
from properties.utils.price_prediction import predict_property_price


# Create your views here.
@api_view(['GET'])
def homes_cards_filtration(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 100))
        type_filter = request.GET.get('type')  # AP or HO
        city_filter = request.GET.get('city')
        state_filter = request.GET.get('state')  # S or R
        min_price = int(request.GET.get('min_price', 0))
        max_price = int(request.GET.get('max_price', 1000000000))
        min_area = int(request.GET.get('min_area', 0))
        max_area = int(request.GET.get('max_area', 1000000))
        bedrooms = int(request.GET.get('bedrooms', '0'))
        bathrooms = int(request.GET.get('bathrooms', '0'))

        queryset = Home.objects.filter(is_pending=False).order_by('-views')
        if type_filter and type_filter != '':
            queryset = queryset.filter(type__iexact=type_filter)
        if city_filter and city_filter != '':
            queryset = queryset.filter(location__city__icontains=city_filter)
        if state_filter and state_filter != '':
            queryset = queryset.filter(state__iexact=state_filter.upper()[0:1])
        queryset = queryset.filter(price__range=(min_price, max_price))
        queryset = queryset.filter(area__range=(min_area, max_area))
        if bedrooms and bedrooms != 0:
            if bedrooms >= 5:
                queryset = queryset.filter(living_space__bedrooms__gte=bedrooms)
            else:
                queryset = queryset.filter(living_space__bedrooms__exact=bedrooms)

        if bathrooms and bathrooms != 0:
            if bathrooms >= 5:
                queryset = queryset.filter(living_space__bathrooms__gte=bathrooms)
            else:
                queryset = queryset.filter(living_space__bathrooms__exact=bathrooms)
        keys = request.GET.get('features', None)
        if keys:
            keys = keys.split(',')
            if len(keys) > 0:
                queries = [Q(data__icontains=f'{{"key": "{key.lower()}"}}') for key in keys]
                query = reduce(lambda q1, q2: q1 | q2, queries)
                queryset2 = Features.objects.filter(query)
                # queries = [Q(data={'key': f'{key.lower()}'}) for key in keys]
                # query = reduce(lambda q1, q2: q1 | q2, queries)
                # queryset2 = Features.objects.filter(query)
                feature_ids = [f.home_id for f in queryset2]
                queryset = queryset.filter(pk__in=feature_ids)
        if (len(queryset)) > 0:
            serializer = HomeCardsSerializer(queryset[:limit], many=True)
        else:
            return JsonResponse({"No Content": "No homes."}, status=204)
        return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def homes_cards_filtration_api(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 30))
        type_filter = request.GET.get('type')  # AP or HO
        city_filter = request.GET.get('city')
        state_filter = request.GET.get('state')  # S or R
        min_price = int(request.GET.get('min_price', 0))
        max_price = int(request.GET.get('max_price', 1000000000))
        min_area = int(request.GET.get('min_area', 0))
        max_area = int(request.GET.get('max_area', 1000000))
        bedrooms = int(request.GET.get('bedrooms', '0'))
        bathrooms = int(request.GET.get('bathrooms', '0'))

        queryset = Home.objects.filter(is_pending=False).order_by('-views')
        if type_filter and type_filter != '':
            queryset = queryset.filter(type__iexact=type_filter)
        if city_filter and city_filter != '':
            queryset = queryset.filter(location__city__icontains=city_filter)
        if state_filter and state_filter != '':
            queryset = queryset.filter(state__iexact=state_filter.upper()[0:1])
        queryset = queryset.filter(price__range=(min_price, max_price))
        queryset = queryset.filter(area__range=(min_area, max_area))
        if bedrooms and bedrooms != 0:
            if bedrooms >= 5:
                queryset = queryset.filter(living_space__bedrooms__gte=bedrooms)
            else:
                queryset = queryset.filter(living_space__bedrooms__exact=bedrooms)

        if bathrooms and bathrooms != 0:
            if bathrooms >= 5:
                queryset = queryset.filter(living_space__bathrooms__gte=bathrooms)
            else:
                queryset = queryset.filter(living_space__bathrooms__exact=bathrooms)
        keys = request.GET.get('features', None)
        if keys:
            keys = keys.split(',')
            if len(keys) > 0:
                queries = [Q(data__icontains=f'{{"key": "{key.lower()}"}}') for key in keys]
                query = reduce(lambda q1, q2: q1 | q2, queries)
                queryset2 = Features.objects.filter(query)
                feature_ids = [f.home_id for f in queryset2]
                queryset = queryset.filter(pk__in=feature_ids)
        serializer = HomeCardsSerializer(queryset[:limit], many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
def home_images_upload(request, pk):
    try:
        home = Home.objects.get(pk=pk)
        if request.method == "PATCH":
            serializer = HomeImageAndOwnershipUploadSerializer(home, data=request.data)
            if serializer.is_valid():
                serializer.save()
                # return JsonResponse(serializer.data, status=200)
                return JsonResponse({'massage': 'updated'}, status=200)
            return JsonResponse(serializer.errors, status=400)
    except Home.DoesNotExist:
        return JsonResponse({"error": f"Home with id={pk} does not exist"}, status=404)


@csrf_exempt
@api_view(['POST'])
@transaction.atomic
def home_list(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = request.data['PropertyData']
            data['state'] = data['state'].upper()[0:1]
            data['owner'] = request.user.id
            serializer = HomeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def home_details(request, pk):
    try:
        home = Home.objects.get(pk=pk)
        home.views = home.views + 1
        if request.user.is_authenticated:
            if home.owner != request.user:
                home.visited_by.add(request.user)
        home.save()
        serializer = HomeRepresentationSerializer(home)
        return JsonResponse(serializer.data, status=200)
    except Home.DoesNotExist:
        return JsonResponse({"error": "Home does not exist"}, status=404)


@api_view(['GET'])
def favourite_home_list(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_object_or_404(get_user_model(), pk=request.user.id)
                favourites = user.favourites.exclude(owner=user)
                if len(favourites) > 0:
                    serializer = HomeCardsSerializer(favourites, many=True)
                    return JsonResponse(serializer.data, safe=False, status=200)
                else:
                    return JsonResponse({"No Content": "the user has no favorite homes."}, status=204)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def visited_home_list(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_object_or_404(get_user_model(), pk=request.user.id)
                visited = user.visited.exclude(owner=user)
                if len(visited) > 0:
                    serializer = HomeCardsSerializer(visited, many=True)
                    return JsonResponse(serializer.data, safe=False, status=200)
                else:
                    return JsonResponse({"No Content": "the user has no visited homes."}, status=204)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
# @login_required
def pending_home_list(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_user_model().objects.get(pk=request.user.id)
                pending = user.properties.filter(is_pending=True)
                if len(pending) > 0:
                    serializer = HomeCardsSerializer(pending, many=True)
                    return JsonResponse(serializer.data, safe=False, status=200)
                else:
                    return JsonResponse({"No Content": "the user has no pending homes."}, status=204)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def favourite_home_list_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_object_or_404(get_user_model(), pk=request.user.id)
                favourites = user.favourites.exclude(owner=user)
                serializer = HomeCardsSerializer(favourites, many=True)
                return JsonResponse(serializer.data, safe=False, status=200)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def visited_home_list_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_object_or_404(get_user_model(), pk=request.user.id)
                visited = user.visited.exclude(owner=user)
                serializer = HomeCardsSerializer(visited, many=True)
                return JsonResponse(serializer.data, safe=False, status=200)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
# @login_required
def pending_home_list_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_user_model().objects.get(pk=request.user.id)
                pending = user.properties.filter(is_pending=True)
                serializer = HomeCardsSerializer(pending, many=True)
                return JsonResponse(serializer.data, safe=False, status=200)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def posted_home_list(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_user_model().objects.get(pk=request.user.id)
                posted = user.properties.filter(is_pending=False)
                if len(posted) > 0:
                    serializer = HomeCardsSerializer(posted, many=True)
                    return JsonResponse(serializer.data, safe=False, status=200)
                else:
                    return JsonResponse({"No Content": "the user has no pending homes."}, status=204)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


@api_view(['GET'])
def posted_home_list_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                user = get_user_model().objects.get(pk=request.user.id)
                posted = user.properties.filter(is_pending=False)
                serializer = HomeCardsSerializer(posted, many=True)
                return JsonResponse(serializer.data, safe=False, status=200)
            except get_user_model().DoesNotExist:
                return JsonResponse({"Not Found": "the user with the given ID does not exist"}, status=404)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


def home_not_found(request):
    data = {'error': 'Home not found.'}
    return JsonResponse(data, status=404)


# @login_required
@api_view(['POST', 'GET'])
def toggle_favorite(request, pk):
    try:
        home = get_object_or_404(Home, pk=pk)
    except Home.DoesNotExist:
        return redirect('home_not_found')

    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            if home.favourite_by.filter(id=user.id).exists():
                home.favourite_by.remove(user)
                is_favorite = False
            else:
                home.favourite_by.add(user)
                is_favorite = True
                home_favourite.send(sender=Home, owner_id=home.owner, user=user)
            data = {'is_favorite': is_favorite}
            return JsonResponse(data)
        elif request.method == "GET":
            is_favorite = home.favourite_by.filter(id=user.id).exists()
            data = {'is_favorite': is_favorite}
            return JsonResponse(data)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)


def predict_property_price_api(request):
    if request.method == 'POST':
        record = request.POST.get('record')
        # Assuming you receive the record data as a JSON string in the 'record' parameter

        # Perform validation and error handling if necessary

        # Call the predict_house_price function
        prediction = predict_property_price(record)

        # Return the prediction as a JSON response
        return JsonResponse(prediction)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
