from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from django.template.defaultfilters import title
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView

from .models import Tour, Guide, Location, Review, Booking, LocationPhoto
from .forms import TourForm, ReviewForm, BookingForm, GuideForm, LocationForm, LocationPhotoFormSet, TourDeleteForm, \
    LocationDeleteForm, GuideDeleteForm, UpdateTourForm, UpdateLocationForm, UpdateGuideForm, TourFilterForm, \
    UpdateReviewForm, AddLocationForm, AddLocationPhotoFormSet
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

    def get(self, request, *args, **kwargs):
        # Получаем tour_id из GET-параметров
        tour_id = request.GET.get('tour_id')
        if tour_id:
            # Проверяем, существует ли тур с таким ID
            tour = get_object_or_404(Tour, id=tour_id)
            # Проверяем, есть ли свободные места
            free_seats = Booking.get_free_seats(tour.id)
            if free_seats <= 0:
                return HttpResponseRedirect(reverse('tours'))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_id = self.request.GET.get('tour_id')
        available_tours = []
        for tour in Tour.objects.all():
            free_seats = Booking.get_free_seats(tour.id)
            if free_seats > 0:
                available_tours.append(tour)

        if tour_id:
            tour = get_object_or_404(Tour, id=tour_id)
            free_seats = Booking.get_free_seats(tour.id)
            if free_seats > 0:
                context['free_seats'] = free_seats
                context['tour'] = tour
            else:
                context['free_seats'] = None
                context['tour'] = None
        else:
            context['free_seats'] = None
            context['tour'] = None

        context['form'].fields['tour_id'].queryset = Tour.objects.filter(id__in=[tour.id for tour in available_tours])

        if tour_id:
            context['form'].initial['tour_id'] = tour_id

        context = self.get_mixin_context(context, title='Создание брони')
        return context

    def form_valid(self, form):
        w = form.save(commit=False)
        w.user_id = self.request.user
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
        notavailable_tours = []
        for tour in context['tours']:
            free_seats = Booking.get_free_seats(tour.id)
            if free_seats == 0:
                notavailable_tours.append(tour.id)
        rating_for_tours = {tour.pk: tour.average_rating() for tour in Tour.objects.all()}
        context['notavailable_tours'] = notavailable_tours
        context['filter_form'] = TourFilterForm(self.request.GET)
        context['rating_for_tours'] = rating_for_tours
        context['title'] = 'Туры'
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='ACT')
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
                        duration_queries |= Q(duration__lt=3)
                    elif duration == '2':
                        duration_queries |= Q(duration__gte=3, duration__lte=6)
                    elif duration == '3':
                        duration_queries |= Q(duration__gt=6)
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
        context['available'] = context['tour'] in get_available_tours()
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
    template_name = 'sitetour/update_location_photo.html'

    # Исправленный метод get_formset
    def get_formset(self, instance=None):
        if instance:
            existing_count = instance.photos.count()
            return LocationPhotoFormSet(instance=instance)
        else:
            return LocationPhotoFormSet(queryset=LocationPhoto.objects.none())

    def get(self, request):
        location_id = request.GET.get('location_choice')
        location = None
        if location_id:
            try:
                location = Location.objects.get(pk=location_id)
            except Location.DoesNotExist:
                pass

        location_form = LocationForm(initial={'location_choice': location_id})

        formset = self.get_formset(location)
        return render(request, self.template_name, {
            'location_form': location_form,
            'formset': formset,
            'title': 'Фото локации',
            'static_root': 'sitetour/css/employee_panel.css',
            'static_js_root': ('sitetour/js/tour_choice.js', 'sitetour/js/dropdown.js')
        })

    def post(self, request):
        location_id = request.POST.get('location_choice')
        location = None

        if location_id:
            try:
                location = Location.objects.get(pk=location_id)
            except (Location.DoesNotExist, ValueError):
                pass

        location_form = LocationForm(request.POST, initial={'location_choice': location_id})

        formset = LocationPhotoFormSet(
            request.POST,
            request.FILES,
            instance=location,
            queryset=location.photos.all() if location else LocationPhoto.objects.none()
        )

        if location_form.is_valid() and formset.is_valid():
            if location:
                formset.save()
                return redirect('manage_location_photos')

        return render(request, self.template_name, {
            'location_form': location_form,
            'formset': formset,
            'title': 'Фото локации',
            'static_root': 'sitetour/css/employee_panel.css',
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


def get_available_tours():
    available_tours = []
    for tour in Tour.objects.all():
        free_seats = Booking.get_free_seats(tour.id)
        if free_seats > 0:
            available_tours.append(tour)
    return available_tours

