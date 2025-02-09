menu = [{'title': "Туры", 'url_name': 'tours'},
        {'title': 'Создать заказ', 'url_name': 'add_booking'},
        {'title': "Ваши заказы", 'url_name': 'my_bookings'},
        {'title': "Наши контакты", 'url_name': 'contacts'},
        {'title':'Отзывы','url_name': 'reviews'},
        {'title':'Панель сотрудника','url_name': 'employee_panel'},
        ]

static_root = 'css/base.css'

class DataMixin:
	def get_mixin_context(self,context,**kwargs):
		context['static_root'] = static_root
		context['static_js_root'] = ('sitetour/js/dropdown.js',)
		context.update(kwargs)
		return context