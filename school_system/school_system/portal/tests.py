from django.test import TestCase
from .models import Class, Subject  # Adjust the import based on your actual model names

class AcademicSetupTests(TestCase):

    def setUp(self):
        # Create initial data for tests
        self.class1 = Class.objects.create(class_name='Form 1')
        self.class2 = Class.objects.create(class_name='Form 2')
        self.subject1 = Subject.objects.create(subject_name='Mathematics')
        self.subject2 = Subject.objects.create(subject_name='Physics')

    def test_add_class(self):
        response = self.client.post('/your-url-to-add-class/', {'class_name': 'Form 3'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful addition
        self.assertTrue(Class.objects.filter(class_name='Form 3').exists())

    def test_delete_class(self):
        response = self.client.post('/your-url-to-delete-class/', {'class_id': self.class1.id})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful deletion
        self.assertFalse(Class.objects.filter(id=self.class1.id).exists())

    def test_add_subject(self):
        response = self.client.post('/your-url-to-add-subject/', {'subject_name': 'Chemistry'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful addition
        self.assertTrue(Subject.objects.filter(subject_name='Chemistry').exists())

    def test_delete_subject(self):
        response = self.client.post('/your-url-to-delete-subject/', {'subject_id': self.subject1.id})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful deletion
        self.assertFalse(Subject.objects.filter(id=self.subject1.id).exists())