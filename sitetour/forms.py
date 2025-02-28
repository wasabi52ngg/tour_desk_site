from cProfile import label

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe

from .models import Tour, Booking, Guide, Location, Category, Review, LocationPhoto, TourSession


class TourForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        label='Дата и время начала',
        widget=forms.TextInput(attrs={'class': 'datetime-picker'})
    )
    end_datetime = forms.DateTimeField(
        label='Дата и время окончания',
        widget=forms.TextInput(attrs={'class': 'datetime-picker'})
    )

    class Meta:
        model = Tour
        exclude = ['duration', 'status', 'slug']


class UpdateTourForm(forms.ModelForm):
    tour_choice = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        label='Выберите тур',
        empty_label="Выберите тур для обновления",
        required=False,
        widget=forms.Select(attrs={'class': 'tour-select'})
    )

    start_datetime = forms.DateTimeField(
        label='Дата и время начала',
        widget=forms.TextInput(attrs={'class': 'datetime-picker'})
    )
    end_datetime = forms.DateTimeField(
        label='Дата и время окончания',
        widget=forms.TextInput(attrs={'class': 'datetime-picker'})
    )

    class Meta:
        model = Tour
        exclude = ['duration', 'status', 'slug']


class TourDeleteForm(forms.Form):
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        label='Выберите тур для удаления',
        empty_label="Выберите тур",
        widget=forms.Select(attrs={'class': 'tour-select'}),
        required=False,
    )


class BookingForm(forms.ModelForm):
    session = forms.ModelChoiceField(
        queryset=TourSession.objects.none(),  # Динамически заполняется
        label="Дата и время",
        empty_label="Выберите дату"
    )
    participants = forms.IntegerField(
        min_value=1,
        label="Количество участников",
        widget=forms.HiddenInput(),
    )
    tour_id = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        label="Тур",
        empty_label="Выберите тур"
    )

    class Meta:
        model = Booking
        fields = ['tour_id','session', 'participants']
        widgets = {
            'tour_id': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tour_id' in self.data:
            # Фильтруем сессии по выбранному туру
            self.fields['session'].queryset = TourSession.objects.filter(
                tour_id=self.data['tour_id'],
                status=TourSession.ACT
            ).annotate(
                free_seats=F('tour__max_participants') - Coalesce(
                    Sum('bookings__participants', filter=~Q(bookings__status=Booking.CANC)),
                    0
                )
            ).filter(free_seats__gt=0)


class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        exclude = ['slug']


class UpdateGuideForm(forms.ModelForm):
    guide_choice = forms.ModelChoiceField(
        queryset=Guide.objects.all(),
        label='Выберите гида',
        empty_label="Выберите гида для обновления",
        widget=forms.Select(attrs={'class': 'tour-select'}),
        required=False,

    )

    class Meta:
        model = Guide
        exclude = ['slug']


class GuideDeleteForm(forms.Form):
    tour = forms.ModelChoiceField(
        queryset=Guide.objects.all(),
        label='Выберите гида для удаления',
        empty_label="Выберите гида",
        widget=forms.Select(attrs={'class': 'tour-select'})
    )


class AddLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ['slug']


class UpdateLocationForm(forms.ModelForm):
    location_choice = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label='Выберите локацию',
        empty_label="Выберите локацию для обновления",
        widget=forms.Select(attrs={'class': 'tour-select'}),
        required=False,
    )

    class Meta:
        model = Location
        exclude = ['slug']


class LocationDeleteForm(forms.Form):
    tour = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label='Выберите локацию для удаления',
        empty_label="Выберите локацию",
        widget=forms.Select(attrs={'class': 'tour-select'})
    )


class LocationChoiceForm(forms.Form):
    location_choice = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Выберите локацию",
        required=True,
        empty_label="--- Выберите локацию ---"
    )

PhotoFormSet = inlineformset_factory(
    Location,
    LocationPhoto,
    fields=('photo',),
    extra=1,
    max_num=3,
    can_delete=False,
    widgets={
        'photo': forms.ClearableFileInput()
    }
)

AddLocationPhotoFormSet = inlineformset_factory(
    Location, LocationPhoto,
    form=AddLocationForm,
    extra=3,
    can_delete=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['slug']


class UpdateReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden-radio'}),
        label='Оценка'
    )
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'hidden-radio'}),
            'comment': forms.Textarea(attrs={
                'rows': 5,
                'maxlength': 1000,
                'placeholder': 'Оставьте ваш комментарий...'
            }),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий'
        }

class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReviewForm, self).__init__(*args, **kwargs)
        if user is not None:
            paid_bookings = Booking.objects.filter(Q(user_id=user, status=Booking.PAID))
            tours = Tour.objects.filter(bookings__in=paid_bookings).distinct()
            self.fields['tour_id'].queryset = tours

    tour_id = forms.ModelChoiceField(queryset=Tour.objects.none(), label="Тур", empty_label='Выберите тур')
    rating = forms.ChoiceField(
        label="Рейтинг",
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'add-review-rating'})
    )

    class Meta:
        model = Review
        fields = ['tour_id', 'rating', 'comment']




class TourFilterForm(forms.Form):
    PRICE_CHOICE = [("False", "Любая"), ("1", "Подешевле: меньше 1000"), ("2", "Средние: от 1000 до 5000"),
                    ("3", "Подороже: больше 5000")]
    DURATION_CHOICE = [("False", "Любая"),(1,"Побыстрее: меньше 3ч"),(2,"Средние: от 3ч до 6ч"),(3,"Подольше: больше 6ч")]
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория",empty_label="Любая")
    price = forms.ChoiceField(choices=PRICE_CHOICE,required=False, label="Цена")
    duration = forms.ChoiceField(choices=DURATION_CHOICE,required=False, label="Длительность")


class ReviewFilterForm(forms.Form):
    PRICE_CHOICE = [("False", "Любая"), ("1", "Подешевле: меньше 1000"), ("2", "Средние: от 1000 до 5000"),
                    ("3", "Подороже: больше 5000")]
    DURATION_CHOICE = [("False", "Любая"),(1,"Побыстрее: меньше 3ч"),(2,"Средние: от 3ч до 6ч"),(3,"Подольше: больше 6ч")]
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория",empty_label="Любая")
    price = forms.ChoiceField(choices=PRICE_CHOICE,required=False, label="Цена")
    duration = forms.ChoiceField(choices=DURATION_CHOICE,required=False, label="Длительность")



