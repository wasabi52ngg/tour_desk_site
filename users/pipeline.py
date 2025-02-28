from urllib.request import urlopen
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import Group


def new_users_handler(backend, user, response, *args, **kwargs):
    group = Group.objects.filter(name='social')
    if group.exists():
        user.groups.add(group[0])

    if backend.name == 'github':
        email = response.get('email') or f"{response.get('login')}@github.com"
        if email and user.email != email:
            user.email = email

        if not user.photo:
            avatar_url = response.get('avatar_url')
            if avatar_url:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urlopen(avatar_url).read())
                img_temp.flush()
                user.photo.save(f"avatar_{user.id}.jpg", File(img_temp))

        user.save()


def save_vk_user_data(backend, user, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        email = response.get('email')
        if email and not user.email:
            user.email = email

        avatar_url = response.get('photo_max')
        if avatar_url and not user.photo:
            try:
                from urllib.request import urlopen
                from django.core.files import File
                from django.core.files.temp import NamedTemporaryFile

                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urlopen(avatar_url).read())
                img_temp.flush()
                user.photo.save(f"vk_avatar_{user.id}.jpg", File(img_temp))
            except Exception as e:
                print(f"Ошибка загрузки аватара: {e}")

        user.save()