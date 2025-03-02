from django.contrib.auth.decorators import user_passes_test
from django.urls import path, include
from . import views
from django.views.decorators.cache import cache_page
from debug_toolbar.toolbar import debug_toolbar_urls

from .views import ManageLocationPhotosView

# def employee_check(user):
#     return user.groups.filter(name='employees').exists()
urlpatterns = [
    path('',views.HomePageView.as_view(),name='home'),
    path('detail_tour/<slug:tour_slug>', views.DetailTourView.as_view(), name='detail_tour'),
    path('detail_guide/<slug:guide_slug>', views.DetailGuideView.as_view(), name='detail_guide'),
    path('detail_location/<slug:location_slug>', views.DetailLocationView.as_view(), name='detail_location'),
    path('tours', cache_page(30) (views.ListToursView.as_view()), name='tours'),
    path('profile', views.AddTourView.as_view(), name='profile'),
    path('contacts', views.ContactsPageView.as_view(), name='contacts'),
    path('reviews',views.ListReviewsView.as_view(), name='reviews'),
    path('add_review', views.CreateReviewView.as_view(), name='add_review'),
    path('update_review/<int:pk>', views.UpdateReviewView.as_view(), name='update_review'),
    path('add_booking', views.CreateBookingView.as_view(), name='add_booking'),
    path('my_bookings', views.ListUserBookingsView.as_view(), name='my_bookings'),
    path('delete_booking/<int:pk>', views.DeleteBookingView.as_view(), name='delete_booking'),
    path('get_free_seats/', views.get_free_seats, name='get_free_seats'),
    path('get_tour_price/', views.get_tour_price, name='get_tour_price'),
    path('get-available-sessions/', views.get_available_sessions, name='get_available_sessions'),
    path('employee_panel/', views.RenderEmployeePanelView.as_view(), name='employee_panel'),
    # path('employee_panel/', user_passes_test(employee_check)(views.RenderEmployeePanelView.as_view()), name='employee_panel'),
    path('employee_panel/tour_panel', views.TourPanelView.as_view(), name='employee_panel_tour'),
    path('employee_panel/location_panel', views.LocationPanelView.as_view(), name='employee_panel_location'),
    path('employee_panel/guide_panel', views.GuidePanelView.as_view(), name='employee_panel_guide'),
    path('employee_panel/add_tour', views.AddTourView.as_view(), name='add_tour'),
    path('employee_panel/update_tour/<int:pk>', views.UpdateTourView.as_view(), name='update_tour'),
    path('create-sessions/', views.CreateSessionView.as_view(), name='create_sessions'),
    path('employee_panel/delete_tour/<int:pk>', views.DeleteTourView.as_view(), name='delete_tour'),
    path('employee_panel/add_location', views.AddLocationView.as_view(), name='add_location'),
    path('employee_panel/update_location/<int:pk>', views.UpdateLocationView.as_view(), name='update_location'),
    path('employee_panel/manage-location-photos/', ManageLocationPhotosView.as_view(), name='manage_location_photos'),
    path('employee_panel/delete_location', views.DeleteLocationView.as_view(), name='delete_location'),
    path('employee_panel/add_guide', views.AddGuideView.as_view(), name='add_guide'),
    path('employee_panel/update_guide/<int:pk>', views.UpdateGuideView.as_view(), name='update_guide'),
    path('employee_panel/delete_guide', views.DeleteGuideView.as_view(), name='delete_guide'),
    path('employee_panel/bookings_wtpm', views.ListBookingsWTPMView.as_view(), name='list_bookings_wtpm'),
    path('employee_panel/bookings_paid', views.ListBookingsPAIDView.as_view(), name='list_bookings_paid'),
    path('employee_panel/bookings_archive', views.ListBookingsArchiveView.as_view(), name='bookings_archive'),
    path('bookings/<int:pk>/confirm/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    path('bookings/<int:pk>/cancel/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('bookings_user/<int:pk>/cancel/', views.CancelBookingDefaultUserView.as_view(), name='cancel_booking_user'),
]  + debug_toolbar_urls()
