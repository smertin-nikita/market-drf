from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    Django docs:
    https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.email}'


class UserProfile(models.Model):

    class Meta:
        verbose_name = _('User profile')

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Owner'),
        related_name='profile',
        on_delete=models.CASCADE
    )

    middle_name = models.CharField(_('middle name'), max_length=150, blank=True)
    is_supplier = models.BooleanField(
        _('supplier status'),
        default=False,
        help_text=_('Designates whether the user is a supplier. Allows the user to manual a shop'),
    )


class Contact(models.Model):
    """ Пользовательские контакты """

    class Meta:
        verbose_name = _("User's contacts")

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name=_("User"),
        related_name='contacts',
        blank=True,
        on_delete=models.CASCADE
    )

    city = models.CharField(max_length=50, verbose_name='Город', blank=True)
    street = models.CharField(max_length=100, verbose_name='Улица', blank=True)
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)

    def __str__(self):
        return f'{_("Contacts for")} {self.owner}'
