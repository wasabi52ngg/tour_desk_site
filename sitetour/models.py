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
    ACT = 'ACT'
    CAN = 'CAN'
    END = 'END'

    Status_choices = [
        (ACT, 'Активна'),
        (CAN, 'Отменена'),
        (END, 'Завершена'),
    ]

    title = models.CharField(verbose_name='Название', max_length=100, db_index=True,
                             validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.PROTECT, null=False, blank=False,
                                 related_name='tours')
    description = models.TextField(verbose_name='Описание', max_length=1500,
                                   validators=[MinLengthValidator(2, message='Минимум 2 символа')])
    duration = models.IntegerField(verbose_name='Длительность', null=True, blank=True,
                                   validators=[MinValueValidator(1, message='Минимум 1 час'),
                                               MaxValueValidator(100, message='максимум 100 часов')])
    price = models.FloatField(verbose_name='Цена',
                              validators=[MinValueValidator(1, message='Минимум 1 рубль'),
                                          MaxValueValidator(1000000, message='максимум 1000000')])
    max_participants = models.IntegerField(verbose_name='Максимальное число участников',
                                           validators=[MinValueValidator(1, message='Минимум 1 участник'),
                                                       MaxValueValidator(100, message='максимум 100 участников')])
    guide_id = models.ForeignKey(Guide, verbose_name='Гид', on_delete=models.PROTECT, null=False, blank=False,
                                 related_name='tours')
    location_id = models.ForeignKey(Location, verbose_name='Локация', on_delete=models.PROTECT, null=False, blank=False,
                                    related_name='tours')
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(verbose_name='Статус', choices=Status_choices, max_length=3, default=ACT)
    slug = models.SlugField(default='', null=False)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.title}", 'ru', reversed=True))
        if self.start_datetime and self.end_datetime:
            time_difference = self.end_datetime - self.start_datetime
            self.duration = int(time_difference.total_seconds() // 3600)
        super(Tour, self).save(*args, **kwargs)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)
        return 0

    def get_absolute_url(self):
        return reverse('detail_tour', args=(self.slug,))


class Booking(models.Model):
    WTPM = 'WTPM'
    PAID = 'PAID'
    CANC = 'CANC'

    Status_choices = [
        (WTPM, 'Ожидает оплаты'),
        (PAID, 'Оплачено'),
        (CANC, 'Отменено'),
    ]

    tour_id = models.ForeignKey(Tour, verbose_name='Тур', on_delete=models.PROTECT, null=False, blank=False,
                                related_name='bookings')
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

        if self.status == 'CANC':
            return

        tour = self.tour_id
        total_seats = tour.max_participants

        booked_seats = tour.bookings.exclude(pk=self.pk).exclude(status='CANC').aggregate(
            models.Sum('participants')
        )['participants__sum'] or 0

        free_seats = total_seats - booked_seats

        if self.participants > free_seats:
            raise ValidationError(
                f'Недостаточно свободных мест. Доступно: {free_seats}, запрошено: {self.participants}'
            )

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(f"{self.tour_id.pk}-{self.user_id.pk}", 'ru', reversed=True))

        if self.participants and self.tour_id:
            self.total_price = self.participants * self.tour_id.price
        self.full_clean()
        super(Booking, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('xxxx', args=(self.slug,))

    @staticmethod
    def get_free_seats(tour_id):
        tour = Tour.objects.get(pk=tour_id)
        total_seats = tour.max_participants
        booked_seats = Booking.objects.filter(tour_id=tour_id).exclude(status='CANC').aggregate(
            models.Sum('participants'))['participants__sum'] or 0
        return total_seats - booked_seats

    def __str__(self):
        return f"{self.user_id} | {self.tour_id} | {self.get_status_display()}"


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


