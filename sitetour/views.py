from datetime import datetime, timedelta
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum, F, ExpressionWrapper, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.forms import IntegerField
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from django.template.defaultfilters import title
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from .models import Tour, Guide, Location, Review, Booking, LocationPhoto, TourSession
from .forms import TourForm, ReviewForm, BookingForm, GuideForm, PhotoFormSet, TourDeleteForm, \
    LocationDeleteForm, GuideDeleteForm, UpdateTourForm, UpdateLocationForm, UpdateGuideForm, TourFilterForm, \
    UpdateReviewForm, AddLocationForm, AddLocationPhotoFormSet, LocationChoiceForm, TourSessionForm
from .utils import DataMixin


# Create your views here.
def homeview(request):
    return render(request, 'sitetour/home.html', context={'title': 'Главная'})

class EmployeeRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='employees').exists()

    def handle_no_permission(self):
        return redirect('home')

class HomePageView(DataMixin, TemplateView):
    template_name = 'sitetour/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Домашняя страница')
        return context


class RenderEmployeePanelView(EmployeeRequiredMixin,DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'sitetour/employee_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Панель сотрудника',
                                         static_root="sitetour/css/employee_panel.css"
                                         )
        return context



class ContactsPageView(DataMixin, TemplateView):
    template_name = 'sitetour/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Наши контакты',)
        return context


class TourPanelView(EmployeeRequiredMixin,DataMixin, TemplateView):
    template_name = 'sitetour/tour_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Панель туров', static_root="sitetour/css/employee_panel.css")
        return context


class GuidePanelView(EmployeeRequiredMixin,DataMixin, TemplateView):
    template_name = 'sitetour/guide_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Панель гидов', static_root="sitetour/css/employee_panel.css")
        return context


class LocationPanelView(EmployeeRequiredMixin,DataMixin, TemplateView):
    template_name = 'sitetour/location_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Панель локации', static_root="sitetour/css/employee_panel.css")
        return context


class AddTourView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, CreateView):
    form_class = TourForm
    template_name = 'sitetour/add_tour.html'
    success_url = reverse_lazy('add_tour')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Добавление тура',
                                         static_root="sitetour/css/employee_panel.css"
                                         )
        return context


class AddLocationView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, CreateView):
    model = Location
    form_class = AddLocationForm
    template_name = 'sitetour/add_location.html'
    success_url = reverse_lazy('add_location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['photo_formset'] = AddLocationPhotoFormSet(self.request.POST, self.request.FILES)
        else:
            context['photo_formset'] = AddLocationPhotoFormSet()
        context = self.get_mixin_context(context, title='Добавление тура',
                                         static_root="sitetour/css/employee_panel.css")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        if photo_formset.is_valid():
            self.object = form.save()
            photo_formset.instance = self.object
            photo_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class AddGuideView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, CreateView):
    form_class = GuideForm
    template_name = 'sitetour/add_guide.html'
    success_url = reverse_lazy('add_guide')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title='Добавление гида',
                                         static_root="sitetour/css/employee_panel.css")
        return context


class CreateBookingView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = BookingForm
    template_name = 'sitetour/add_booking.html'
    success_url = reverse_lazy('my_bookings')
    tour = None

    def dispatch(self, request, *args, **kwargs):
        self.tour = self.get_tour()
        return super().dispatch(request, *args, **kwargs)

    def get_tour(self):
        tour_id = self.request.GET.get('tour_id')
        return get_object_or_404(Tour, id=tour_id) if tour_id else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'tour': self.tour,
            'static_js_root': 'sitetour/js/bookings.js',
            'title': 'Создание брони',
            'user': self.request.user
        })
        return self.get_mixin_context(context)

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user_id = self.request.user  #
        session = form.cleaned_data['session']
        participants = form.cleaned_data['participants']

        if not session.is_available(participants):
            form.add_error(None, 'Недостаточно свободных мест')
            return self.form_invalid(form)

        booking.total_price = participants * session.tour.price
        booking.save()

        session.refresh_from_db()
        if session.get_free_seats() <= 0:
            session.status = TourSession.END
            session.save(update_fields=['status'])

        return super().form_valid(form)


def get_free_seats(request):
    tour_id = request.GET.get('tour_id')
    if tour_id:
        free_seats = Booking.get_free_seats(tour_id)
        return JsonResponse({'free_seats': free_seats})
    return JsonResponse({'free_seats': None})


def get_tour_price(request):
    tour_id = request.GET.get('tour_id')
    if tour_id:
        tour = Tour.objects.get(pk=tour_id)
        return JsonResponse({'price': tour.price})
    return JsonResponse({'price': 0})


def get_available_sessions(request):
    tour_id = request.GET.get('tour_id')
    date = request.GET.get('date')

    if not tour_id:
        return JsonResponse({'error': 'Не указан ID тура'}, status=400)

    try:
        tour = Tour.objects.get(id=tour_id)
    except Tour.DoesNotExist:
        return JsonResponse({'error': 'Тур не найден'}, status=404)

    sessions = TourSession.objects.filter(
        tour=tour,
        status=TourSession.ACT
    ).prefetch_related('bookings')

    if date:
        try:
            target_date = datetime.fromisoformat(date).date()
            sessions = sessions.filter(start_datetime__date=target_date)
        except ValueError:
            return JsonResponse({'error': 'Неверный формат даты'}, status=400)

    sessions_data = []
    for session in sessions:
        free_seats = session.get_free_seats()
        if free_seats > 0:
            sessions_data.append({
                'id': session.id,
                'start_datetime': session.start_datetime.isoformat(),
                'free_seats': free_seats,
                'max_participants': session.tour.max_participants,
                'price': session.tour.price  # Добавляем цену
            })

    return JsonResponse({'sessions': sessions_data})

class CreateReviewView(DataMixin, CreateView):
    form_class = ReviewForm
    template_name = 'sitetour/add_review.html'
    success_url = reverse_lazy('reviews')

    def get_form_kwargs(self):
        kwargs = super(CreateReviewView, self).get_form_kwargs()
        user = self.request.user
        kwargs['user'] = user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context)
        return context

    def form_valid(self, form):
        w = form.save(commit=False)
        w.user_id = self.request.user
        return super().form_valid(form)



class ListToursView(ListView):
    template_name = 'sitetour/list_tours.html'
    model = Tour
    context_object_name = 'tours'
    allow_empty = True
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rating_for_tours = {tour.pk: tour.average_rating() for tour in context['tours']}

        context['rating_for_tours'] = rating_for_tours
        context['filter_form'] = TourFilterForm(self.request.GET)
        context['title'] = 'Туры'
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_form = TourFilterForm(self.request.GET)

        if filter_form.is_valid():
            category_value = filter_form.cleaned_data.get('category')
            price_values = self.request.GET.getlist('price')
            duration_values = self.request.GET.getlist('duration')

            if category_value and str(category_value) != 'False':
                queryset = queryset.filter(category=category_value)

            if price_values and 'False' not in price_values:
                price_queries = Q()
                for price in price_values:
                    if price == '1':
                        price_queries |= Q(price__lt=1000)
                    elif price == '2':
                        price_queries |= Q(price__gte=1000, price__lt=5000)
                    elif price == '3':
                        price_queries |= Q(price__gte=5000)
                queryset = queryset.filter(price_queries)

            if duration_values and 'False' not in duration_values:
                duration_queries = Q()
                for duration in duration_values:
                    if duration == '1':
                        duration_queries |= Q(default_duration_hours__lt=3)
                    elif duration == '2':
                        duration_queries |= Q(default_duration_hours__gte=3, default_duration_hours__lte=6)
                    elif duration == '3':
                        duration_queries |= Q(default_duration_hours__gt=6)
                queryset = queryset.filter(duration_queries)

        return queryset


class ListUserBookingsView(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'sitetour/list_bookings.html'
    model = Booking
    context_object_name = 'bookings'
    allow_empty = True
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Ваши заказы",
                                         static_root="sitetour/css/list_bookings.css",
                                         )
        return context

    def get_queryset(self):
        query_set = self.request.user.booking.all()
        return query_set


class ListBookingsWTPMView(EmployeeRequiredMixin,DataMixin, ListView):
    template_name = 'sitetour/list_bookings_wtpm.html'
    model = Booking
    context_object_name = 'bookings'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Заказы ожидающие оплаты",
                                         static_root="sitetour/css/orders_wtpm.css")
        return context

    def get_queryset(self):
        query_set = Booking.objects.filter(status='WTPM')
        return query_set


class ListBookingsPAIDView(EmployeeRequiredMixin,DataMixin, ListView):
    template_name = 'sitetour/list_bookings_paid.html'
    model = Booking
    context_object_name = 'bookings'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Оплаченные заказы",
                                         static_root="sitetour/css/employee_panel.css")
        return context

    def get_queryset(self):
        query_set = Booking.objects.filter(status='PAID')
        return query_set


class ListBookingsArchiveView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, ListView):
    template_name = 'sitetour/bookings_archive.html'
    model = Tour
    context_object_name = 'tours'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Оплаченные заказы",
                                         static_root="sitetour/css/employee_panel.css")
        return context

    def get_queryset(self):
        query_set = Tour.objects.filter(status='Завершена')
        return query_set


class ListReviewsView(DataMixin, ListView):
    template_name = 'sitetour/list_reviews.html'
    model = Review
    context_object_name = 'reviews'
    allow_empty = True
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get('filter') == 'my_reviews' and self.request.user.is_authenticated:
            queryset = queryset.filter(user_id=self.request.user)

        selected_tours = self.request.GET.get('tours')
        if selected_tours:
            selected_tours = selected_tours.split(',')
            queryset = queryset.filter(tour_id__in=selected_tours)

        sort_by = self.request.GET.get('sort_by', 'created_at')
        sort_direction = self.request.GET.get('sort_direction', 'desc')

        if sort_by not in ['tour_id', 'created_at', 'rating']:
            sort_by = 'created_at'

        ordering = f"{'-' if sort_direction == 'desc' else ''}{sort_by}"
        queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список отзывов"

        context['tours'] = Tour.objects.all()

        selected_tours = self.request.GET.get('tours', '').split(',')
        context['selected_tours'] = [int(tour) for tour in selected_tours if tour.isdigit()]

        context['sort_by'] = self.request.GET.get('sort_by', 'created_at')
        context['sort_direction'] = self.request.GET.get('sort_direction', 'desc')

        return context


class DetailTourView(DataMixin, DetailView):
    model = Tour
    template_name = 'sitetour/detail_tour.html'
    context_object_name = 'tour'
    slug_url_kwarg = 'tour_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Информация о туре")
        context['available'] = is_available_tour(context['tour'])
        return context


class DetailGuideView(DataMixin, DetailView):
    model = Guide
    template_name = 'sitetour/detail_guide.html'
    context_object_name = 'guide'
    slug_url_kwarg = 'guide_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Информация о гиде")
        return context


class DetailLocationView(DataMixin, DetailView):
    model = Location
    template_name = 'sitetour/detail_location.html'
    context_object_name = 'location'
    slug_url_kwarg = 'location_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = self.get_mixin_context(context, title="Информация о локации",static_js_root=('sitetour/js/map.js',))
        return context


class UpdateTourView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, UpdateView):
    model = Tour
    form_class = UpdateTourForm
    template_name = 'sitetour/update_tour.html'
    success_url = reverse_lazy('update_tour')
    extra_context = {'title': 'Обновление тура', 'static_root': "sitetour/css/employee_panel.css",
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get_success_url(self):
        return reverse_lazy('update_tour', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'tour_choice' in self.request.POST:
            tour_id = self.request.POST['tour_choice']
            if tour_id:
                tour = get_object_or_404(Tour, id=tour_id)
                kwargs['instance'] = tour
        return kwargs

    def form_valid(self, form):
        tour_id = self.request.POST['tour_choice']
        if tour_id:
            tour = get_object_or_404(Tour, id=tour_id)
            form.instance = tour
        return super().form_valid(form)


class UpdateGuideView(EmployeeRequiredMixin,LoginRequiredMixin, UpdateView):
    model = Guide
    form_class = UpdateGuideForm
    template_name = 'sitetour/update_guide.html'
    success_url = reverse_lazy('update_guide')
    extra_context = {'title': 'Обновление гида', 'static_root': "sitetour/css/employee_panel.css",
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get_success_url(self):
        return reverse_lazy('update_guide', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'guide_choice' in self.request.POST:
            guide_id = self.request.POST['guide_choice']
            if guide_id:
                guide = get_object_or_404(Guide, id=guide_id)
                kwargs['instance'] = guide
        return kwargs

    def form_valid(self, form):
        guide_id = self.request.POST['guide_choice']
        if guide_id:
            guide = get_object_or_404(Guide, id=guide_id)
            form.instance = guide
        return super().form_valid(form)


class UpdateLocationView(EmployeeRequiredMixin,LoginRequiredMixin, UpdateView):
    model = Location
    form_class = UpdateLocationForm
    template_name = 'sitetour/update_location.html'
    success_url = reverse_lazy('update_location')
    extra_context = {'title': 'Обновление локации', 'static_root': "sitetour/css/employee_panel.css",
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get_success_url(self):
        return reverse_lazy('update_location', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'location_choice' in self.request.POST:
            location_id = self.request.POST['location_choice']
            if location_id:
                location = get_object_or_404(Location, id=location_id)
                kwargs['instance'] = location
        return kwargs

    def form_valid(self, form):
        location_id = self.request.POST['location_choice']
        if location_id:
            location = get_object_or_404(Location, id=location_id)
            form.instance = location
        return super().form_valid(form)


class ManageLocationPhotosView(EmployeeRequiredMixin, LoginRequiredMixin, View):
    def get_formset(self, instance):
        return PhotoFormSet(
            instance=instance,
            queryset=LocationPhoto.objects.filter(location=instance).order_by('id')
        )

    def get(self, request):
        location_form = LocationChoiceForm(request.GET or None)
        selected_location = None
        formset = None

        if location_form.is_valid():
            selected_location = location_form.cleaned_data['location_choice']
            formset = self.get_formset(selected_location)

        return render(request, 'sitetour/update_location_photo.html', {
            'location_form': location_form,
            'formset': formset,
            'selected_location': selected_location,
            'title': 'Редактирование фотографий',
            'static_root': "sitetour/css/employee_panel.css",
            'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')
        })

    def post(self, request):
        location_form = LocationChoiceForm(request.GET or None)
        selected_location = None

        if location_form.is_valid():
            selected_location = location_form.cleaned_data['location_choice']

        if not selected_location:
            return redirect('manage_location_photos')

        formset = self.get_formset(selected_location)
        formset = PhotoFormSet(
            request.POST,
            request.FILES,
            instance=selected_location,
            queryset=LocationPhoto.objects.filter(location=selected_location).order_by('id')
        )

        if formset.is_valid():
            instances = formset.save(commit=False)
            for form in formset:
                if form.cleaned_data.get('photo') is False and form.instance.pk:
                    form.instance.photo.delete()
                    form.instance.delete()

            for instance in instances:
                instance.location = selected_location
                instance.save()

            return redirect(
                f"{reverse('manage_location_photos')}"
                f"?location_choice={selected_location.id}"
            )

        return render(request, 'sitetour/update_location_photo.html', {
            'location_form': location_form,
            'formset': formset,
            'selected_location': selected_location,
            'title': 'Редактирование фотографий',
            'static_root': "sitetour/css/employee_panel.css",
            'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')
        })



class UpdateReviewView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = UpdateReviewForm
    template_name = 'sitetour/update_review.html'
    context_object_name = 'review'

    def get_success_url(self):
        return reverse_lazy('reviews')

    def get_queryset(self):
        return Review.objects.filter(user_id=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Редактирование отзыва',
            'static_root': 'css/base.css'
        })
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Review, pk=pk, user_id=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeleteTourView(EmployeeRequiredMixin,LoginRequiredMixin, DeleteView):
    model = Tour
    template_name = 'sitetour/delete_tour.html'
    success_url = reverse_lazy('employee_panel')
    extra_context = {'title': 'Обновление локации', 'static_root': "sitetour/css/employee_panel.css",
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get(self, request, *args, **kwargs):
        form = TourDeleteForm()
        return render(request, self.template_name, {'form': form,**self.extra_context})

    def post(self, request, *args, **kwargs):
        form = TourDeleteForm(request.POST)
        if form.is_valid():
            tour = form.cleaned_data['tour']
            tour.delete()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form,**self.extra_context})


class DeleteGuideView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, DeleteView):
    template_name = 'sitetour/delete_guide.html'
    success_url = reverse_lazy('employee_panel')
    extra_context = {'title': 'Удаление гида', 'static_root': 'sitetour/css/employee_panel.css',
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get(self, request, *args, **kwargs):
        form = GuideDeleteForm()
        return render(request, self.template_name, {'form': form,**self.extra_context})

    def post(self, request, *args, **kwargs):
        form = GuideDeleteForm(request.POST)
        if form.is_valid():
            tour = form.cleaned_data['tour']
            tour.delete()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form,**self.extra_context})


class DeleteLocationView(EmployeeRequiredMixin,LoginRequiredMixin, DataMixin, DeleteView):
    template_name = 'sitetour/delete_location.html'
    success_url = reverse_lazy('employee_panel')
    extra_context = {'title': 'Удаление локации', 'static_root': 'sitetour/css/employee_panel.css',
                     'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')}

    def get(self, request, *args, **kwargs):
        form = LocationDeleteForm()
        return render(request, self.template_name, {'form': form,**self.extra_context})

    def post(self, request, *args, **kwargs):
        form = LocationDeleteForm(request.POST)
        if form.is_valid():
            tour = form.cleaned_data['tour']
            tour.delete()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form,**self.extra_context})


class DeleteBookingView(LoginRequiredMixin, DataMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('my_bookings')


class ConfirmBookingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'PAID'
        booking.save()
        return redirect(reverse('list_bookings_wtpm'))


class CancelBookingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'CANC'
        booking.save()
        return redirect(reverse('list_bookings_wtpm'))


class CancelBookingDefaultUserView(View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'CANC'
        booking.save()
        return redirect(reverse('my_bookings'))

def page_not_found_view(request, exception):
    return render(request, 'sitetour/404_page.html', status=404)


class CreateSessionView(EmployeeRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = TourSessionForm
    template_name = 'sitetour/create_sessions.html'
    success_url = reverse_lazy('create_sessions')

    def form_valid(self, form):
        tour = form.cleaned_data['tour']
        dates = form.cleaned_data['dates']
        time_start = form.cleaned_data['time_start']
        created = 0
        errors = []

        for date_str in dates:
            try:
                # Преобразуем строку даты в объект date
                date = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Создаем datetime объект с указанным временем
                naive_start = datetime.combine(date, time_start)

                # Преобразуем в aware datetime с учетом часового пояса
                start_datetime = timezone.make_aware(naive_start)

                # Рассчитываем время окончания
                end_datetime = start_datetime + timedelta(hours=tour.duration)

                # Создаем сессию
                TourSession.objects.create(
                    tour=tour,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    status=TourSession.ACT
                )
                created += 1

            except Exception as e:
                errors.append(f"{date_str}: {str(e)}")

        if created:
            messages.success(self.request, f'Создано {created} сессий')
        if errors:
            messages.error(self.request, f'Ошибки: {"; ".join(errors)}')

        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Добавление сессии'
        context['static_root'] = 'sitetour/css/employee_panel.css'
        context['static_js_root'] = ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')
        return context


def is_available_tour(tour):
    available_sessions = tour.sessions.filter(
        status=TourSession.ACT
    ).annotate(
        booked_seats=Sum('bookings__participants', filter=~Q(bookings__status='CANC'))
    ).filter(
        tour__max_participants__gt=F('booked_seats')
    )
    return available_sessions.exists()

