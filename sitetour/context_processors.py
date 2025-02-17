from django.urls import resolve

def selected_menu_item(request):
    current_url_name = request.path_info
    selected = None

    if current_url_name.startswith('/employee_panel'):
        selected = 'employee_panel'
    elif current_url_name == '/tours':
        selected = 'tours'
    elif current_url_name == '/add_booking':
        selected = 'add_booking'
    elif current_url_name == '/my_bookings':
        selected = 'my_bookings'
    elif current_url_name == '/contacts':
        selected = 'contacts'
    elif current_url_name == '/reviews':
        selected = 'reviews'
    elif current_url_name == '/users/profile':
        selected = 'profile'

    return {'selected': selected}
