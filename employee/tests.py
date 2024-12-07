from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Employee, AdvancePayment, WorkAssignment, Request
from .wizforms import RequestTypeForm, AdvancePaymentForm, RequestDetailsForm
from .reqview import RequestWizard
from django.core.files.uploadedfile import SimpleUploadedFile

class FormTests(TestCase):

    def test_request_type_form(self):
        form = RequestTypeForm(data={'request_type': 'administrative'})
        self.assertTrue(form.is_valid(), "RequestTypeForm should be valid with 'administrative' selected")
        
        form = RequestTypeForm(data={'request_type': 'work_assignment'})
        self.assertTrue(form.is_valid(), "RequestTypeForm should be valid with 'work_assignment' selected")

    def test_advance_payment_form(self):
        data = {
            'amount': '500.00',
            'notes': 'Advance for emergency.',
        }
        form = AdvancePaymentForm(data=data)
        self.assertTrue(form.is_valid(), "AdvancePaymentForm should be valid with valid data")
        
        # Check if 'amount' field is present and correct
        self.assertIn('amount', form.fields)
        self.assertIn('notes', form.fields)

    def test_request_details_form(self):
        data = {
            'requestMessage': 'This is a test request message',
        }
        form = RequestDetailsForm(data=data)
        self.assertTrue(form.is_valid(), "RequestDetailsForm should be valid with a message")
        
        # Check if crispy form layout exists
        self.assertTrue(hasattr(form, 'helper'), "RequestDetailsForm should have a crispy form helper")
        self.assertIn('requestMessage', form.fields)
        self.assertIn('file_attachment', form.fields)


class RequestWizardViewTests(TestCase):

    def setUp(self):
        # Create test employee and superadmin
        self.employee = Employee.objects.create_user(username='testuser', password='12345', email='test@user.com')
        self.superadmin = Employee.objects.create_user(username='superadmin', password='12345', email='super@admin.com', is_superuser=True)
        self.client.login(username='testuser', password='12345')

    def test_request_wizard_step1(self):
        response = self.client.get(reverse('employee:request_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_step1.html')
        self.assertContains(response, "Select Request Type")

    def test_request_wizard_step2_admin(self):
        # Submit step 1 data (selecting administrative request)
        response = self.client.post(reverse('employee:request_dashboard'), {'request_type': 'administrative'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_step2_admin.html')

        # Check form fields for AdvancePayment
        self.assertContains(response, 'amount')
        self.assertContains(response, 'notes')

    def test_request_wizard_step3(self):
        # Submit step 1 and step 2 (administrative request)
        self.client.post(reverse('employee:request_dashboard'), {'request_type': 'administrative'})
        response = self.client.post(reverse('employee:request_dashboard'), {'amount': '500.00', 'notes': 'Advance for emergency'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_step3.html')

        # Check if RequestDetailsForm is rendered
        self.assertContains(response, 'requestMessage')

    def test_advance_payment_submission(self):
        # Submit step 1 and step 2 data for administrative request
        self.client.post(reverse('employee:request_dashboard'), {'request_type': 'administrative'})
        self.client.post(reverse('employee:request_dashboard'), {'amount': '500.00', 'notes': 'Advance for emergency'})

        # Submit step 3 data
        response = self.client.post(reverse('employee:request_dashboard'), {
            'requestMessage': 'This is a test request message',
            'file_attachment': SimpleUploadedFile("file.txt", b"file_content")
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful form submission
        self.assertRedirects(response, reverse('employee:request_dashboard'))

        # Check if an AdvancePayment and Request object were created
        self.assertTrue(AdvancePayment.objects.exists(), "AdvancePayment object should be created")
        self.assertTrue(Request.objects.exists(), "Request object should be created")

    def test_work_assignment_submission(self):
        # Submit step 1 for work assignment
        response = self.client.post(reverse('employee:request_dashboard'), {'request_type': 'work_assignment'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_step2_assignment.html')

        # Submit step 2 for work assignment
        response = self.client.post(reverse('employee:request_dashboard'), {
            'taskerId': self.superadmin.id,  # Assign to superadmin
            'work': 'Test Work Assignment',
            'assignDate': timezone.now().isoformat(),
            'dueDate': (timezone.now() + timezone.timedelta(days=5)).isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_step3.html')

        # Submit step 3 data
        response = self.client.post(reverse('employee:request_dashboard'), {
            'requestMessage': 'Work assignment request message',
            'file_attachment': SimpleUploadedFile("file.txt", b"file_content")
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful form submission
        self.assertRedirects(response, reverse('employee:request_dashboard'))

        # Check if WorkAssignment and Request object were created
        self.assertTrue(WorkAssignment.objects.exists(), "WorkAssignment object should be created")
        self.assertTrue(Request.objects.exists(), "Request object should be created")


