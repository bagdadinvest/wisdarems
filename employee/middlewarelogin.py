from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude paths like login or signup
        if not request.user.is_authenticated and request.path not in [reverse('login'), reverse('signup')]:
            if request.is_ajax() or request.path.startswith('/api/'):
                return JsonResponse({'error': 'Login required'}, status=403)  # handle ajax
            else:
                return redirect(f"{reverse('home')}?next={request.path}")  # show modal
        return self.get_response(request)
