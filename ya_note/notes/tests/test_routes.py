from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='adic')
        cls.reader = User.objects.create(username='padic')
        # От имени одного пользователя создаём комментарий к note:
        cls.notes = Note.objects.create(
            author=cls.author,
            text='Текст комментария'
        ) 

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.notes.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        urls = (
            ('notes:home',None),
            ('notes:edit',(self.notes.id,)),
            ('notes:delete',(self.notes.id,)),
            
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 



    # def test_home_page(self):
    #     url = reverse('notes:home')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK) 