from django.db import models
# from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser, BaseUserManager ## A new class is imported. ##
from django.db import models
from django.utils.translation import ugettext_lazy as _

from PIL import Image


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# Create your models here.
class Usuario(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(verbose_name = 'Nombre', max_length = 50, default='')
    last_name = models.CharField(verbose_name = 'Apellido', max_length = 50, default='')
    image = models.ImageField(default='socio_default.png', upload_to='profile_pics')
    es_admin = models.BooleanField(verbose_name='Es socio', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    objects = UserManager()

    @property
    def get_short_name(self):
        pass

    @property
    def get_full_name(self):
        pass

    # def save(self, *args, **kwargs):

    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300:
    #         out_size = (300, 300)
    #         img.thumbnail(out_size)
    #         img.save(self.image.path)