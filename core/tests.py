from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import User
from .services import generate_quiz_from_pdf
from PyPDF2 import PdfWriter
from io import BytesIO


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_get(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu Zona de Estudio')

    def test_upload_pdf_and_submit_quiz(self):
        pdf_content = b'%PDF-1.4\n%...'  # contenido ficticio
        pdf_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')

        response = self.client.post(reverse('dashboard'), {'pdf_file': pdf_file}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('quiz_data' in self.client.session)

        quiz = self.client.session['quiz_data']
        answers = {'answer_1': quiz[0]['correct'], 'answer_2': quiz[1]['correct'], 'answer_3': quiz[2]['correct']}
        response = self.client.post(reverse('submit_quiz'), answers, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.sizu_points, 30)
        self.assertContains(response, '¡Felicidades!')

    def test_generate_quiz_from_pdf(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        pdf_file = SimpleUploadedFile('test.pdf', buffer.getvalue(), content_type='application/pdf')
        quiz = generate_quiz_from_pdf(pdf_file)

        self.assertIsInstance(quiz, list)
        self.assertEqual(len(quiz), 3)
        self.assertIn('question', quiz[0])

    def test_chat_api(self):
        response = self.client.post(reverse('chat_api'), {'message': 'Hola'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('reply', response.json())

