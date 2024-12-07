from django.core.management.base import BaseCommand
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate a magic login link for a given user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email of the user to generate the magic link for')

    def handle(self, *args, **kwargs):
        email = kwargs['email']

        try:
            # Get the user by email
            user = User.objects.get(email=email)

            # Create the token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Generate the magic login link
            link = reverse('accounts:magic_login', kwargs={'uidb64': uid, 'token': token})
            magic_link = f"{settings.SITE_URL}{link}"

            # Print the magic link
            self.stdout.write(f"Magic link: {magic_link}")

        except User.DoesNotExist:
            self.stderr.write(f"Error: No user found with email {email}")

