from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from rest_framework import serializers

from Maskan.settings import DATE_INPUT_FORMATS
from users.models import Profile

User = get_user_model()


class UserLoginSerializer(serializers.ModelSerializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ('username_or_email', 'password')

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        if username_or_email and password:
            user = authenticate(username=username_or_email, password=password)
            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "username" or "email" and "password".'
            raise serializers.ValidationError(msg)
        return user


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(input_formats=DATE_INPUT_FORMATS, format='%Y-%m-%d')

    class Meta:
        model = User
        fields = ('id', 'username', 'date_joined', 'last_login', 'email', 'phone_number', 'date_of_birth', 'password',
                  'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already in use.")
        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError("username already in use.")
        return data

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.pop('password'))
        user.is_active = False
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update the user instance with validated data
        instance.set_password(validated_data.pop('password', None))
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    ID_card = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ('id', 'user', 'profile_picture', 'ID_card')
        read_only_fields = ('id', 'user')

    def validate(self, data):

        profile_picture = data.get('profile_picture')
        if profile_picture is not None:
            # Ensure that the file is an image
            if not profile_picture.content_type.startswith('image'):
                raise serializers.ValidationError("Profile picture must be an image")
            # Ensure that the image is not too big
            if profile_picture.size > 25 * 1024 * 1024:
                raise serializers.ValidationError("Profile picture is too large (maximum size is 25MB)")
            # Ensure that the image dimensions are reasonable
            width, height = get_image_dimensions(profile_picture)
            if width > 4096 or height > 4096:
                raise serializers.ValidationError("Profile picture dimensions are too "
                                                  "large (maximum dimensions are 4096x4096)")

        id_card = data.get('ID_card')
        if id_card is not None:
            # Ensure that the file is an image
            if not id_card.content_type.startswith('image'):
                raise serializers.ValidationError("ID Card must be an image")
            # Ensure that the image is not too big
            if id_card.size > 25 * 1024 * 1024:
                raise serializers.ValidationError("ID Card is too large (maximum size is 25MB)")
            # Ensure that the image dimensions are reasonable
            width, height = get_image_dimensions(id_card)
            if width > 4096 or height > 4096:
                raise serializers.ValidationError("ID Card dimensions are too large (maximum dimensions are 4096x4096)")

        return data

    def create(self, validated_data):
        profile = Profile.objects.create(**validated_data)
        return profile

    def update(self, instance, validated_data):
        # Update the profile fields
        # If a new ID card was provided, replace the old one
        id_card = validated_data.get('ID_card')
        if id_card is not None:
            var = id_card.name
            extension = var.split('.')[-1]
            name = f'{instance.user.username}_id_card.{extension}'
            id_card.name = name
            instance.ID_card = id_card

        # If a new profile picture was provided, replace the old one
        profile_picture = validated_data.get('profile_picture')
        if profile_picture is not None:
            var = profile_picture.name
            extension = var.split('.')[-1]
            name = f'{instance.user.username}_profile_picture.{extension}'
            profile_picture.name = name
            instance.profile_picture = profile_picture

        instance.save()
        return instance


class UserAndProfileUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False, partial=True)
    password = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False)
    date_of_birth = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_of_birth', 'password', 'phone_number', 'first_name', 'last_name',
                  'profile', 'is_active', 'is_staff', 'is_superuser')
        read_only_fields = ['id', 'username', 'is_active', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        profile_p = data.get('profile')
        if profile_p is not None:
            profile_picture = profile_p.get('profile_picture')
            if profile_picture is not None:
                # Ensure that the file is an image
                if not profile_picture.content_type.startswith('image'):
                    raise serializers.ValidationError("Profile picture must be an image")
                # Ensure that the image is not too big
                if profile_picture.size > 25 * 1024 * 1024:
                    raise serializers.ValidationError("Profile picture is too large (maximum size is 25MB)")
                # Ensure that the image dimensions are reasonable
                width, height = get_image_dimensions(profile_picture)
                if width > 4096 or height > 4096:
                    raise serializers.ValidationError("Profile picture dimensions are too "
                                                      "large (maximum dimensions are 4096x4096)")

            id_card = profile_p.get('id_card')
            if id_card is not None:
                # Ensure that the file is an image
                if not id_card.content_type.startswith('image'):
                    raise serializers.ValidationError("ID Card must be an image")
                # Ensure that the image is not too big
                if id_card.size > 25 * 1024 * 1024:
                    raise serializers.ValidationError("ID Card is too large (maximum size is 25MB)")
                # Ensure that the image dimensions are reasonable
                width, height = get_image_dimensions(id_card)
                if width > 4096 or height > 4096:
                    raise serializers.ValidationError(
                        "ID Card dimensions are too large (maximum dimensions are 4096x4096)")

        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already in use.")

        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError("username already in use.")

        return data

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        user_profile = instance.profile
        # Update user instance with validated data
        password = validated_data.pop('password')
        if password is not None:
            instance.set_password(password)
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()

        # Update profile instance with profile data
        for key, value in profile_data.items():
            if hasattr(user_profile, key):
                setattr(user_profile, key, value)
        user_profile.save()
        return instance

