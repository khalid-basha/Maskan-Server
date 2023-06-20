from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, date_of_birth, phone_number, password=None):
        """
        Creates and saves a User with the given email, date of
        birth, phone_number and password.
        """
        if not username:
            raise ValueError('User must have a username')

        if not email:
            raise ValueError('User must have a email')

        if not email:
            raise ValueError('Users must have an email address')

        if not date_of_birth:
            raise ValueError('User must have a date of birth')

        if not phone_number:
            raise ValueError('User must have a phone number')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, date_of_birth, phone_number, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth, phone_number and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user
