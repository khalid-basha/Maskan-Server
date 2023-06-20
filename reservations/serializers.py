from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from properties.models import Home
from reservations.models import TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(required=False, queryset=Home.objects.all())
    reserved_by = serializers.PrimaryKeyRelatedField(required=False, queryset=get_user_model().objects.all())

    class Meta:
        model = TimeSlot
        fields = '__all__'
        Read_only_fields = ('id', 'user')

    def create(self, validated_data):
        user = validated_data['user']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        date = validated_data['date']
        previous = TimeSlot.objects.filter(user=user, start_time=start_time, end_time=end_time, date=date)
        if previous.count() == 0:
            time_slot = TimeSlot.objects.create(**validated_data)
            return time_slot
        return previous.first()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_obj = datetime.strptime(representation['date'], '%Y-%m-%d').date()
        representation['year'] = date_obj.year
        representation['month'] = date_obj.month
        representation['day'] = date_obj.day
        user_id = representation['reserved_by']
        if user_id:
            user = get_user_model().objects.get(pk=user_id)
            representation['phone_number'] = user.phone_number.as_rfc3966
            representation['username'] = user.username
            representation['email'] = user.email
        else:
            representation['phone_number'] = "555-555-555"
            representation['username'] = "Not a User"
            representation['email'] = "Not a user"
        return representation


class TimeSlotSerializerWithDay(TimeSlotSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_obj = datetime.strptime(representation['date'], '%Y-%m-%d').date()
        day_name = date_obj.strftime('%a').upper()
        representation['day'] = day_name
        representation['dayNum'] = date_obj.day
        return representation
