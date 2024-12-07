print("Loading context processors...")

import logging

import subprocess
import ast


# Initialize the logger
logger = logging.getLogger(__name__)

def run_command(command):
    """
    Executes a command using subprocess and returns the output.
    """
    try:
        logger.info(f"Running command: {command}")  # Log the command being run
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        output = result.stdout
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {command}, {e.output}")  # Log any errors
        return f"Error: {e.output}"

def format_command_output(output):
    """
    Format the command output into key-value pairs for display in the template.
    """
    lines = output.splitlines()
    formatted_output = []

    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            try:
                value = ast.literal_eval(value.strip())  # Try to evaluate Python literals like dicts/lists
            except (ValueError, SyntaxError):
                value = value.strip()  # If it's not a literal, keep it as a string
            formatted_output.append({"key": key.strip(), "value": value})
        else:
            formatted_output.append({"key": line, "value": ""})  # If no key-value pair, treat as a standalone line

    logger.debug(f"Formatted command output: {formatted_output}")  # Log formatted output for debugging
    return formatted_output

def command_context_processor(request):
    """
    Context processor to provide command output to templates.
    """
    logger.info("Loading command context processor...")  # Log that the context processor is being loaded
    command_output = run_command("python manage.py show_settings")  # Example command
    formatted_output = format_command_output(command_output)
    
    # Add the formatted output to the context
    return {
        'command_output': formatted_output
    }
