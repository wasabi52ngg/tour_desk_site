from datetime import timedelta

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from .validators import validate_phone_number, validate_email
from django.urls import reverse
from transliterate import translit


# Create your models here


class Guide(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=100, null=False, blank=False,
                            validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    surname = models.CharField(verbose_name='Фамилия', max_length=100, null=False, blank=False,
                               validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    phone = models.CharField(verbose_name='Телефон', null=False, blank=False,
                             validators=[validate_phone_number])
    email = models.EmailField(verbose_name='Email', null=True, blank=True,
                              validators=[validate_email, ])
    bio = models.TextField(verbose_name='Описание', max_length=1000, null=True, blank=True,
                           validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    photo = models.ImageField(verbose_name='Фото', upload_to="guides", default=None,
                              blank=True, null=True)
    slug = models.SlugField(default='', null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'name', 'surname'])
        ]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.name}-{self.surname}", 'ru', reversed=True))
        super(Guide, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail_guide', args=(self.slug,))


class Location(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, null=False, blank=False,
                             db_index=True,
                            validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    address = models.CharField(verbose_name='Адрес', max_length=150, null=True, blank=True,
                               validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    description = models.TextField(verbose_name='Описание', max_length=1500, null=True, blank=True,
                                   validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    slug = models.SlugField(default='', null=False)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.name}", 'ru', reversed=True))
        super(Location, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail_location', args=(self.slug,))


class LocationPhoto(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(verbose_name='Фото', upload_to="locations", default=None,
                              blank=True, null=True)

    def __str__(self):
        return f"Фото для {self.location.name}"


class Category(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, null=False, blank=False,
                            unique=True, db_index=True,
                            validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    description = models.TextField(verbose_name='Описание', max_length=300, null=True, blank=True,
                                   validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    slug = models.SlugField(default='', null=False)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.name}", 'ru', reversed=True))
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('xxxx', args=(self.slug,))


class Tour(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100, db_index=True,
                             validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.PROTECT, null=False, blank=False,
                                 related_name='tours')
    description = models.TextField(verbose_name='Описание', max_length=1500,
                                   validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    duration = models.IntegerField(verbose_name='Длительность', null=True, blank=True,
                                   validators=[MinValueValidator(1, message='Минимум 1 час'),
                                               MaxValueValidator(100, message='максимум 100 часов')])
    max_participants = models.IntegerField(verbose_name='Максимальное число участников')
    price = models.FloatField(verbose_name='Цена',
                              validators=[MinValueValidator(1, message='Минимум 1 рубль'),
                                          MaxValueValidator(1000000, message='максимум 1000000')])
    guide_id = models.ForeignKey(Guide, verbose_name='Гид', on_delete=models.PROTECT, null=False, blank=False,
                                 related_name='tours')
    location_id = models.ForeignKey(Location, verbose_name='Локация', on_delete=models.PROTECT, null=False, blank=False,
                                    related_name='tours')
    base_max_participants = models.IntegerField(
        verbose_name='Базовое максимальное число участников',
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    default_duration_hours = models.IntegerField(
        verbose_name='Продолжительность по умолчанию (часов)',
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    slug = models.SlugField(default='', null=False)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.title}", 'ru', reversed=True))
        if not self.duration:
            self.duration = self.default_duration_hours
        if not self.max_participants:
            self.max_participants = self.base_max_participants
        super(Tour, self).save(*args, **kwargs)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)
        return 0

    def get_absolute_url(self):
        return reverse('detail_tour', args=(self.slug,))


class TourSession(models.Model):
    ACT = 'ACT'
    CAN = 'CAN'
    END = 'END'

    Status_choices = [
        (ACT, 'Активна'),
        (CAN, 'Отменена'),
        (END, 'Завершена'),
    ]

    tour = models.ForeignKey(Tour, verbose_name='Тур', on_delete=models.CASCADE, related_name='sessions')
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(verbose_name='Статус', choices=Status_choices, max_length=3, default=ACT)

    def __str__(self):
        return f"{self.tour.title} - {self.start_datetime.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'status']),
        ]

    def is_available(self, participants=1):
        return self.status == self.ACT and self.get_free_seats() >= participants

    def get_free_seats(self):
        return self.tour.max_participants - self.bookings.exclude(
            status=Booking.CANC
        ).aggregate(
            total=Coalesce(Sum('participants'), 0)
        )['total']

    def clean(self):
        super().clean()
        if self.start_datetime < timezone.now() + timedelta(hours=2):
            raise ValidationError("Сессия должна быть запланирована минимум за 2 часа до начала")

    def get_available_dates(self):
        now = timezone.now()
        return self.start_datetime.astimezone(timezone.get_current_timezone()).date()



class Booking(models.Model):
    WTPM = 'WTPM'
    PAID = 'PAID'
    CANC = 'CANC'

    Status_choices = [
        (WTPM, 'Ожидает оплаты'),
        (PAID, 'Оплачено'),
        (CANC, 'Отменено'),
    ]

    session = models.ForeignKey(TourSession, verbose_name='Сессия тура', on_delete=models.PROTECT, related_name='bookings')
    user_id = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.PROTECT, null=False,
                                blank=False, related_name='booking')
    participants = models.IntegerField(verbose_name='Число участников',
                                       validators=[MinValueValidator(1, message='Минимум 1 участник'), ])
    total_price = models.FloatField(verbose_name='Итоговая цена',
                                    validators=[MinValueValidator(2, message='Минимум 1 рубль'),
                                                MaxValueValidator(1000000, message='максимум 1000000')])
    status = models.CharField(verbose_name='Статус', choices=Status_choices, max_length=4, default=WTPM)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    slug = models.SlugField(default='', null=False)

    def clean(self):
        super().clean()

        if self.status == Booking.CANC:
            return

        # Добавляем проверку существования сессии
        if not hasattr(self, 'session') or not self.session:
            raise ValidationError("Сессия не указана")

        free_seats = self.session.get_free_seats()

        # Добавляем проверку на отрицательные значения
        if free_seats < 0:
            raise ValidationError("Некорректное количество свободных мест")

        if self.participants > free_seats:
            raise ValidationError(
                f'Недостаточно свободных мест. Доступно: {free_seats}, запрошено: {self.participants}'
            )

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.session.pk}-{self.user_id_id}", 'ru', reversed=True))
        if self.participants and self.session:
            self.total_price = self.participants * self.session.tour.price
        if not self.session_id:
            raise ValueError("Booking must be linked to a session")
        self.full_clean()
        super(Booking, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('xxxx', args=(self.slug,))

    @staticmethod
    def get_free_seats_for_session(session_id):
        """Возвращает свободные места для конкретной сессии"""
        session = TourSession.objects.get(pk=session_id)
        return session.get_free_seats()

    def __str__(self):
        return f"{self.user_id} | {self.session} | {self.get_status_display()}"


class Review(models.Model):
    tour_id = models.ForeignKey(Tour, verbose_name='Тур', on_delete=models.PROTECT, null=False, blank=False,
                                related_name='reviews')
    user_id = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.PROTECT, null=False,
                                blank=False, related_name='reviews')
    comment = models.TextField(verbose_name='Комментарий', max_length=1000,
                               validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    rating = models.PositiveIntegerField(verbose_name='Рейтинг', validators=[
        MinValueValidator(1, message='Минимум 1 звезда'),
        MaxValueValidator(5, message='Максимум 5 звезд')
    ])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    slug = models.SlugField(default='', null=False)

    def __str__(self):
        return f"{self.tour_id} {self.user_id}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.tour_id.pk}-{self.user_id.pk}", 'ru', reversed=True))
        super(Review, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('reviews', args=(self.slug,))


