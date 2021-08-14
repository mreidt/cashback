from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address.')
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Revendedor(models.Model):
    """Extends user to add cpf"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    cpf = models.CharField(max_length=14, unique=True)
    name = models.CharField(max_length=255, blank=False)

    def __str__(self) -> str:
        return self.name


class Compra(models.Model):
    """Compra model that stores purchases informations"""

    class Status(models.IntegerChoices):
        EM_VALIDACAO = 1
        APROVADO = 2
        NAO_APROVADO = 3

    code = models.IntegerField(unique=True)
    value = models.FloatField(blank=False)
    date = models.DateField(blank=False)
    revendedor = models.ForeignKey(Revendedor, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices, default=1)

    @property
    def month_total(self):
        return sum([c.value for c in Compra.objects.filter(
            revendedor=self.revendedor,
            date__year=self.date.year,
            date__month=self.date.month
        )])

    @property
    def cashback_percent(self):
        if self.month_total > 1500:
            return 20
        elif self.month_total > 1000:
            return 15
        else:
            return 10

    @property
    def cashback_value(self):
        return round(self.value * (self.cashback_percent / 100), 2)

    @property
    def status_str(self):
        if self.status == 1:
            return 'Em validação'
        elif self.status == 2:
            return 'Aprovado'
        else:
            return 'Não aprovado'

    def __str__(self) -> str:
        return str(self.code)
