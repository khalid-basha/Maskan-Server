import datetime
import calendar
from datetime import date, timedelta
from django.views.decorators.csrf import csrf_exempt

from notifications.models import reserve_schedule
from properties.models import Home
from reservations.models import TimeSlot
from reservations.serializers import TimeSlotSerializer, TimeSlotSerializerWithDay
from rest_framework.decorators import api_view
from django.http import JsonResponse


# Create your views here.
def convert_to_slots_list(slots_list, user):
    converted_slots = []
    current_date = date.today()
    current_weekday = current_date.weekday()
    for slot in slots_list:
        start_time = slot['start']
        end_time = slot['end']
        if end_time <= start_time or start_time < 0 or end_time > 24:
            raise ValueError("start time should be greater than or equal 0 and end time should be less than or equal 24"
                             "and start time less than end time")
        day = slot['day']
        try:
            weekday = list(calendar.day_name).index(day.title())
        except ValueError:
            raise ValueError(f"Invalid day name: {day}")
        delta_days = (weekday - current_weekday) % 7
        next_date = current_date + timedelta(days=delta_days)
        while next_date.month == current_date.month:
            for hour in range(start_time, end_time):
                converted_slots.append({'start_time': hour, 'end_time': hour + 1, 'date': next_date, 'user': user.id})
            next_date += timedelta(days=7)
    return converted_slots


@csrf_exempt
@api_view(['POST', 'GET'])
def time_slot_list(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                data = convert_to_slots_list(request.data['list'], user=request.user)  # change it to request.user
            except Exception as e:
                return JsonResponse({"Error": str(e)}, status=400)
            TimeSlot.objects.filter(user=request.user, reserved_by__isnull=False).delete()  # delete all the old slots
            # except the slots reserved by any user
            serializer = TimeSlotSerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201, safe=False)
            return JsonResponse(serializer.errors, status=400)
        elif request.method == 'GET':
            slots = TimeSlot.objects.filter(user=request.user, reserved_by__isnull=False)  # user
            serializer = TimeSlotSerializer(slots, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)
    else:
        return JsonResponse({"Forbidden": "you have to login"}, status=403)


@csrf_exempt
@api_view(['GET'])
def time_slots_list_short(request):
    if request.method == 'GET':
        owner = int(request.GET.get('property_owner_id', 0))
        today = date.today()
        hour = datetime.datetime.utcnow().hour
        slots = TimeSlot.objects.filter(date__gte=today, user_id=owner).order_by("date", 'start_time').exclude(
            date=today, start_time__lte=hour)

        serializer = TimeSlotSerializerWithDay(slots, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)


@csrf_exempt
@api_view(['PATCH'])
def reserve_time_slot(request, pk):
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            data = request.data
            try:
                time_slot = TimeSlot.objects.get(pk=pk)
            except TimeSlot.DoesNotExist:
                return JsonResponse({"error": f"Time slot with id={pk} does not exist"}, status=404)
            home_id = data['home']
            try:
                home = Home.objects.get(pk=home_id)
            except Home.DoesNotExist:
                return JsonResponse({"error": f"Home with id={home_id} does not exist"}, status=404)
            if time_slot.reserved_by:
                return JsonResponse({"error": f"Time slot with id={pk} already reserved"}, status=404)
            data['reserved_by'] = request.user.id
            data['home'] = home.id
            if TimeSlot.objects.filter(home_id=home_id, reserved_by=request.user).count() != 0:
                return JsonResponse({"error": f"The user already have a reserved time in Home with id={home_id}"},
                                    status=406)

            if home.owner == request.user:
                return JsonResponse({"error": f"The user is the owner of the Home with id={home_id}"},
                                    status=406)
            serializer = TimeSlotSerializer(time_slot, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                reserve_schedule.send(sender=None, owner_id=home.owner)
                return JsonResponse(serializer.data, status=202)
            return JsonResponse(serializer.errors, status=400)
        else:
            return JsonResponse({"Unauthorized": "the user is not authenticated"}, status=401)
