from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

def shell_view(request):
    if request.method == "POST":
        command = request.POST.get('command', '')

        # Allowed commands you want to expose
        allowed_commands = {
            'all_users': 'User.objects.all()',
            'user_count': 'User.objects.count()',
            'get_user_types': '[{"username": user.username, "user_type": user.get_user_type_display()} for user in User.objects.all()]'
        }
        
        # Check if the command is one of the allowed commands
        if command in allowed_commands:
            try:
                # Safely evaluate the allowed command
                result = eval(allowed_commands[command])
                output = str(result)
            except Exception as e:
                output = str(e)
        else:
            output = "Command not allowed."
        
        return JsonResponse({'output': output})
    
    return render(request, 'metrics/shell_template.html')
