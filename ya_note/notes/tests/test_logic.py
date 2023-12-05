from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestNoteCreation(TestCase):

    NOTE_TEXT = 'note'
    NOTE_TITLE = 'title'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_in = Client()
        cls.author_in.force_login(cls.author)
        cls.reader = User.objects.create(username='reader')
        cls.reader_in = Client()
        cls.reader_in.force_login(cls.reader)
        cls.form_data = {'text': cls.NOTE_TEXT,
                         'title': cls.NOTE_TITLE,
                         'slug':cls.NOTE_SLUG}
        cls.url_for_add = reverse('notes:add')
        

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(
            self.url_for_add,
            data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url_for_add}'
        self.assertRedirects(response, expected_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count,0)

    def test_user_can_create_note(self):
        response = self.author_in.post(
            self.url_for_add, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.NOTE_SLUG)

class TestNotetEditDelete(TestCase):

    NOTE_TEXT = 'note'
    NOTE_TITLE = 'title'
    NEW_NOTE_TEXT = 'new note'
    NOTE_SLUG = 'slug'
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_in = Client()
        cls.author_in.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_in = Client()
        cls.reader_in.force_login(cls.reader)
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug=cls.NOTE_SLUG,
                                       author=cls.author,
                                       )
        cls.url_success = reverse('notes:success', None)
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NOTE_TITLE, 
                         'text': cls.NEW_NOTE_TEXT}
    
    def test_author_can_edit_note(self):
        response = self.author_in.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.note.slug)
        self.assertEqual(self.note.author, self.note.author)
    
    def test_author_can_delete_note(self):
        response = self.author_in.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_edit_note_of_author(self):
        response = self.reader_in.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.note.author)

    def test_reader_cant_delete_note_of_author(self):
        response = self.reader_in.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)