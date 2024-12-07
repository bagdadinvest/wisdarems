import subprocess
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from urllib.parse import unquote
from django.utils.translation import gettext as _
from .models import Command
import os
import platform

# Function to get the virtual environment activation command based on OS
def get_venv_activate_command():
    if platform.system() == 'Windows':
        return os.path.join('venv', 'Scripts', 'activate')
    else:
        return os.path.join('venv', 'bin', 'activate')

# Base command for manage.py commands
BASE_COMMAND = ['python', 'manage.py']

def stream_logs(command):
    """
    Generator that runs the command and streams the output line by line
    in Server-Sent Event format (SSE).
    """
    print(f"Debug: Starting the stream_logs function with command: {command}")
    try:
        venv_activate_command = get_venv_activate_command()
        if platform.system() == 'Windows':
            full_command = f'cmd /c "{venv_activate_command} && {" ".join(command)}"'
        else:
            full_command = f'source {venv_activate_command} && {" ".join(command)}'

        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        print(f"Debug: Subprocess started with command: {full_command}")

        for stdout_line in iter(process.stdout.readline, ''):
            # Properly send each line as a server-sent event with a newline to preserve format
            yield f"data: {stdout_line.strip()}\n\n"  # Ensure each line is sent separately
        for stderr_line in iter(process.stderr.readline, ''):
            # Properly send stderr as well
            yield f"data: {stderr_line.strip()}\n\n"

        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()

        print(f"Debug: Command return code: {return_code}")

        if return_code != 0:
            yield f"data: Command exited with error code {return_code}\n\n"
            print(f"Debug: Command exited with error code {return_code}")
        else:
            yield "data: Command completed successfully!\n\n"
            print("Debug: Command completed successfully!")

    except Exception as e:
        print(f"Debug: Exception occurred: {str(e)}")
        yield f"data: Error: {str(e)}\n\n"

def run_predefined_command(request):
    """
    View to execute predefined Django Extension commands from the database and stream the output.
    """
    command_name = request.GET.get('command', None)

    if not command_name:
        return JsonResponse({'error': _('Invalid or missing command')}, status=400)

    try:
        # Fetch the command from the database
        command_instance = Command.objects.get(name=command_name)
        command = BASE_COMMAND + command_instance.usage.split()  # Get the command usage from the DB
        print(f"Debug: Running predefined command: {command}")

        response = StreamingHttpResponse(stream_logs(command), content_type='text/event-stream')
        print("Debug: Returning StreamingHttpResponse for predefined command...")
        return response
    except Command.DoesNotExist:
        return JsonResponse({'error': _('Command not found')}, status=404)
    except Exception as e:
        print(f"Debug: Exception in run_predefined_command: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def run_custom_command(request):
    """
    View to execute a custom command input by the user.
    """
    command = request.GET.get('custom_command', None)

    if not command:
        return JsonResponse({'error': _('No custom command provided')}, status=400)

    try:
        # Decode and split the custom command
        decoded_command = unquote(command).split()
        print(f"Debug: Running custom command: {decoded_command}")

        response = StreamingHttpResponse(stream_logs(decoded_command), content_type='text/event-stream')
        print("Debug: Returning StreamingHttpResponse for custom command...")
        return response
    except Exception as e:
        print(f"Debug: Exception in run_custom_command: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def metrics_view(request):
    """
    The main view to display the command input form and predefined command buttons.
    """
    commands = Command.objects.all()  # Retrieve all commands from the database
    return render(request, 'metrics/metrics_view.html', {'commands': commands})
