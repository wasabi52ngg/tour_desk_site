# tests/test_views.py
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Tour, Location, Guide, Booking, Review, TourSession, Category, LocationPhoto
from django.utils import timezone


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # employee_group = Group.objects.create(name='employees')
        # cls.employee = User.objects.create_user(
        #     username='employee',
        #     email='employee@example.com',
        #     password='employeepass'
        # )
        # cls.employee.groups.add(employee_group)
        #
        # cls.category = Category.objects.create(
        #     name='Test Category',
        #     description='Test category description'
        # )
        #
        # cls.guide = Guide.objects.create(
        #     name='Иван',
        #     surname='Петров',
        #     phone='+79161234567',
        #     email='guide@example.com',
        #     bio='Тестовый гид'
        # )
        #
        # cls.location = Location.objects.create(
        #     name='Тестовая локация',
        #     address='Тестовый адрес',
        #     description='Тестовое описание'
        # )
        #
        # cls.location_photo = LocationPhoto.objects.create(
        #     location=cls.location,
        #     photo=SimpleUploadedFile(
        #         "test_location.jpg",
        #         b"file_content",
        #         content_type="image/jpeg"
        #     )
        # )
        #
        # cls.tour = Tour.objects.create(
        #     title='Тестовый тур',
        #     category=cls.category,
        #     description='Тестовое описание тура',
        #     duration=4,
        #     max_participants=10,
        #     price=1000,
        #     guide_id=cls.guide,
        #     location_id=cls.location
        # )
        #
        # start_time = timezone.now() + timezone.timedelta(days=1)
        # cls.session = TourSession.objects.create(
        #     tour=cls.tour,
        #     start_datetime=start_time,
        #     end_datetime=start_time + timezone.timedelta(hours=4)
        # )
        #
        # cls.booking = Booking.objects.create(
        #     session=cls.session,
        #     user_id=cls.user,
        #     participants=2,
        #     total_price=2000
        # )
        #
        # cls.review = Review.objects.create(
        #     tour_id=cls.tour,
        #     user_id=cls.user,
        #     comment='Отличный тур!',
        #     rating=5
        # )

    def setUp(self):
        self.client = Client()

    def test_homepage(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_tour_list(self):
        response = self.client.get(reverse('tours'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tours/list.html')

    def test_tour_detail(self):
        response = self.client.get(reverse('detail_tour', args=[self.tour.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour.title)

    def test_non_existing_page(self):
        response = self.client.get('/non-existing-url/')
        self.assertEqual(response.status_code, 404)


class AuthenticatedUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_user_bookings(self):
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)

    def test_booking_creation(self):
        response = self.client.post(reverse('add_booking'), {
        })
        self.assertEqual(response.status_code, 302)


class EmployeePanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        employee_group = Group.objects.create(name='employees')

        cls.employee = User.objects.create_user(
            username='employee',
            password='employeepass'
        )
        cls.employee.groups.add(employee_group)

        cls.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass'
        )

    def test_employee_panel_access(self):
        response = self.client.get(reverse('employee_panel'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("employee_panel")}')

        self.client.login(username='regular', password='regularpass')
        response = self.client.get(reverse('employee_panel'))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='employee', password='employeepass')
        response = self.client.get(reverse('employee_panel'))
        self.assertEqual(response.status_code, 200)

    def test_tour_management(self):
        self.client.login(username='employee', password='employeepass')

        # Тестирование создания тура
        response = self.client.post(reverse('add_tour'), {
            # данные формы
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tour.objects.exists())


class StaticFilesTests(TestCase):
    def test_static_files(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'css/styles.css')
        self.assertContains(response, 'js/main.js')

    def test_media_files(self):
        test_photo = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        obj = Location.objects.create(
            name="Test Location",
            photo=test_photo
        )
        response = self.client.get(reverse('detail_location', args=[obj.slug]))
        self.assertContains(response, obj.photo.url)


class FormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def test_review_form(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_review'), {
            'text': 'Great service!',
            'rating': 5
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.exists())
