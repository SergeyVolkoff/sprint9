from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    Note_list = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='adic')
        cls.reader = User.objects.create(username='radic')
        cls.author_in=Client()
        cls.reader_in=Client()
        cls.reader_in.force_login(cls.reader)
        cls.author_in.force_login(cls.author)
        # От имени одного пользователя создаём комментарий к note:
        cls.notes = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст комментария',
            slug='Slug1'
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', (cls.notes.slug,)),
        )
    
    def test_availability_form(self):
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_in.get(url)
                self.assertIn('form', response.context)

    def test_availability_detail_in_list(self):
        response = self.author_in.get(self.Note_list)
        self.assertIn(self.notes, response.context['object_list'])
    
    def test_reader_has_note_list(self):
        response = self.reader_in.get(self.Note_list)
        self.assertNotIn(self.notes, response.context['object_list'])