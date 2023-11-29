from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='adic')
        cls.author_in=Client()
        cls.reader_in=Client()
        cls.author_in.force_login(cls.author)
        cls.reader = User.objects.create(username='radic')
        cls.reader_in.force_login(cls.reader)
        # От имени одного пользователя создаём комментарий к note:
        cls.notes = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст комментария',
            slug='Slug1'
        ) 
        cls.urls_redirects =(
            ('notes:delete', (cls.notes.slug,)),
        )



    def test_pages_availability(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup')
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author_in, HTTPStatus.OK),
            (self.reader_in, 404),
        )
        for user, status in users_statuses:
            for name, args in self.urls_redirects:
                with self.subTest(user=self.reader_in, name=name):        
                    url = reverse(name, args=args)
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    



    # def test_home_page(self):
    #     url = reverse('notes:home')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK) 