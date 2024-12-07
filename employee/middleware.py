
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DarkModeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Retrieve the 'darkMode' cookie, default to 'disabled' if not found
        dark_mode_status = request.COOKIES.get('darkMode', 'disabled')
        
        # Debugging print (can be removed in production)
        print(f"Dark mode status: {dark_mode_status}")
        
        # Attach the dark mode value to the request object for template access
        request.dark_mode = dark_mode_status

    def process_response(self, request, response):
        # If the 'darkMode' cookie doesn't exist, set it to 'disabled' for 7 days
        if 'darkMode' not in request.COOKIES:
            response.set_cookie('darkMode', 'disabled', max_age=7*24*60*60)  # Set for 7 days
            logger.info("DarkMode cookie set to 'disabled' by default")

        return response
