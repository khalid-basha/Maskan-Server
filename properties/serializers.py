from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.db import transaction
from rest_framework import serializers

from properties.models import Home, Location, LivingSpace, Features, Apartment, House, Image, Ownership
from properties.utils.price_prediction import predict_property_price


class LivingSpaceSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = LivingSpace
        fields = '__all__'
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, validated_data):
        instance = LivingSpace.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.bedrooms = validated_data.get('bedrooms', instance.bedrooms)
        instance.bathrooms = validated_data.get('bathrooms', instance.bathrooms)
        instance.kitchens = validated_data.get('kitchens', instance.kitchens)
        instance.balconies = validated_data.get('balconies', instance.balconies)
        instance.halls = validated_data.get('halls', instance.halls)
        instance.living_rooms = validated_data.get('living_rooms', instance.living_rooms)
        instance.save()
        return instance


class FeaturesSerializer(serializers.ModelSerializer):
    data = serializers.ListField(child=serializers.DictField())
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = Features
        fields = ['data', 'home', 'id']
        read_only_fields = ['id', ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        data = representation['data']
        data_list = []
        for obj in data:
            data_list.append({"key": obj['key'].lower()})

        representation['data'] = data_list
        return representation


class LocationSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = Location
        fields = ('id', 'home', 'coordinates', 'address', 'city')
        read_only_fields = ['id', ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        data = representation['coordinates']
        point_str = data.split(";")[1].strip()[6:]  # Extract the "POINT (33.2 15.2)" substring
        latitude, longitude = point_str.strip(
            '()').split()  # Extract latitude and longitude values and remove parentheses
        new_data = {'lat': float(latitude), 'lng': float(longitude)}  # Fixed syntax for dictionary creation
        representation['data'] = new_data
        return representation

    def validate_coordinates(self, value):
        x = value['x']
        y = value['y']
        value = Point(x, y)
        return value

    def create(self, validated_data):
        location = Location.objects.create(**validated_data)
        return location

    def update(self, instance, validated_data):
        instance.coordinates = validated_data.get('coordinates', instance.coordinates)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.save()
        return instance


class ImageSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)
    image = serializers.ImageField()

    class Meta:
        model = Image
        fields = ('id', 'home', 'image')
        read_only_fields = ['id', ]

    def create(self, validated_data):
        image = Image.objects.create(**validated_data)
        return image

    def update(self, instance, validated_data):
        instance.home = validated_data.get('home', instance.home)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class OwnershipSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = Ownership
        fields = '__all__'
        read_only_fields = ['id', ]

    def validate_record(self, value):
        # Ensure that the uploaded file is an image
        if not value.content_type.startswith('image'):
            raise serializers.ValidationError("Uploaded file must be an image.")

        # Ensure that the uploaded image is not too large
        if value.size > 10 * 1024 * 1024:  # 10 MB
            raise serializers.ValidationError("Uploaded image must be less than 10 MB.")

        return value

    def create(self, validated_data):
        ownership = Ownership.objects.create(**validated_data)
        return ownership

    def update(self, instance, validated_data):
        instance.record = validated_data.get('record', instance.record)
        instance.is_accepted = validated_data.get('is_accepted', instance.is_accepted)
        instance.is_viewable = validated_data.get('is_viewable', instance.is_viewable)
        instance.save()
        return instance


class ApartmentSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = Apartment
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, attrs):
        floor = attrs.get('floor')
        if floor is not None:
            out_of_floors = attrs.get('out_of_floors')
            if out_of_floors is not None:
                if floor > out_of_floors:
                    serializers.ValidationError('\'floor\' value should be less than or equal \'out_of_floors\' value')

        return attrs

    def update(self, instance, validated_data):

        instance.floor = validated_data.get('floor', instance.floor)
        instance.out_of_floors = validated_data.get('out_of_floors', instance.out_of_floors)
        if instance.floor > instance.out_of_floors:
            raise serializers.ValidationError('\'floor\' value should be less than or equal \'out_of_floors\' value')
        instance.save()
        return instance

    def create(self, validated_data):
        apartment = Apartment.objects.create(**validated_data)
        return apartment


class HouseSerializer(serializers.ModelSerializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all(), required=False)

    class Meta:
        model = House
        fields = '__all__'
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        instance.number_of_floors = validated_data.get('number_of_floors', instance.number_of_floors)
        instance.land_area = validated_data.get('land_area', instance.land_area)
        instance.save()
        return instance

    def create(self, validated_data):
        home = validated_data.pop('home')
        if home.type == 'HO':
            house = House.objects.create(**validated_data)
            house.save()
            return house
        else:
            raise serializers.ValidationError(f'Invalid home type: {home.type}, should be HO:HOUSE')


class HomeSerializer(serializers.ModelSerializer):
    features = FeaturesSerializer()
    living_space = LivingSpaceSerializer()
    location = LocationSerializer()
    apartment = ApartmentSerializer(required=False)
    house = HouseSerializer(required=False)

    class Meta:
        model = Home
        fields = ('id', 'price', 'area', 'description', 'built_year', 'features', 'living_space', 'location', 'house',
                  'type', 'state', 'views', 'add_date', 'owner', 'apartment', 'is_pending')
        read_only_fields = ('id', 'views', 'add_date', 'is_pending')

    def validate_built_year(self, value):
        """
        Validate the built_year field to ensure that it is between 1900 and the current year.
        """
        current_year = datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError('The built year should be between 1900 and the current year.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        features_data = validated_data.pop('features')
        location_data = validated_data.pop('location')
        living_space_data = validated_data.pop('living_space')
        apartment_date = validated_data.pop('apartment', None)
        house_date = validated_data.pop('house', None)

        # Create the Home object
        home = Home.objects.create(**validated_data)

        # Create the related objects with the home instance as foreign key
        location = Location.objects.create(home=home, **location_data)
        living_space = LivingSpace.objects.create(home=home, **living_space_data)
        try:
            data_list = [{'key': obj['key']} for obj in features_data['data']]
            result = {'data': data_list}
            features = Features.objects.create(home=home, data=data_list)
            home.features = features
        except Exception as e:
            print(e)
        # Set the related objects as attributes of the Home instance

        home.location = location
        home.living_space = living_space
        if home.type == 'AP':
            apartment = Apartment.objects.create(home=home, **apartment_date)
            home.apartment = apartment
        elif home.type == 'HO':
            house = House.objects.create(home=home, **house_date)
            home.house = house
        return home

    def update(self, instance, validated_data):
        instance.price = validated_data.get('price', instance.price)
        instance.area = validated_data.get('area', instance.area)
        instance.description = validated_data.get('description', instance.description)
        instance.built_year = validated_data.get('built_year', instance.built_year)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance


class HomeCardsSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    living_space = LivingSpaceSerializer(fields=['bathrooms', 'bedrooms'])
    features = FeaturesSerializer()
    location = LocationSerializer()

    class Meta:
        model = Home
        fields = ['id', 'price', 'living_space', 'views', 'is_pending', 'add_date', 'area', 'first_image', 'state',
                  'features', 'location']

    def get_first_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return ImageSerializer(first_image).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # data['location'] = {'address': 'Rafidea Street bla bla', 'city': 'Nablus'}  # include static data
        return data


class HomeImageAndOwnershipUploadSerializer(serializers.ModelSerializer):
    record = serializers.ImageField(required=False)
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    def validate_images(self, value):
        validated_images = []
        for img in value:
            validated_images.append({'image': img})
        return validated_images

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = Image.objects.filter(home_id=instance.id)
        return data

    class Meta:
        model = Home
        fields = ['images', 'record']

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        if images_data:
            for img_data in images_data:
                Image.objects.create(home=instance, **img_data)

        record_image = validated_data.pop('record', None)
        if record_image:
            if Ownership.objects.filter(home=instance).exists():
                Ownership.objects.filter(home=instance).delete()
            Ownership.objects.create(home=instance, record=record_image)
        return instance


class HomeRepresentationSerializer(serializers.ModelSerializer):
    living_space = LivingSpaceSerializer(read_only=True)
    features = FeaturesSerializer(read_only=True)
    ownership = OwnershipSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    apartment = ApartmentSerializer(read_only=True)
    house = HouseSerializer(read_only=True)
    location = LocationSerializer()

    class Meta:
        model = Home
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        p_type = ''
        if data['type'] == 'HO':
            p_type = 'HOUSE'
        else:
            p_type = 'Apartment'.upper()
        record = {
            "bedrooms": data['living_space']['bedrooms'],
            "bathrooms": data['living_space']['bathrooms'],
            "area": data['area'],
            "type": p_type,
            "city": data['location']['city']
        }
        print(record)
        prediction = predict_property_price(record)
        data['prediction'] = int(prediction['predicted_price'])
        if data['owner'] and data['owner'] != '':
            data['owner_name'] = get_user_model().objects.get(id=data['owner']).username
        return data
