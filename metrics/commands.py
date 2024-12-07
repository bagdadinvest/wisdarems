# commands.py
# This file holds the predefined Django extension commands.

PREDEFINED_COMMANDS = {
    # Display all URLs in the project
    'show_urls': ['show_urls'],

    # Run scheduled jobs (replace 'daily' with 'weekly', 'monthly' if necessary)
    'run_daily_jobs': ['runjobs', 'daily'],

    # List all available jobs
    'list_jobs': ['listjobs'],

    # Generate a graph model visualization (you can replace 'myapp' with your app's name)
    'graph_models': ['graph_models', 'myapp', '-o', 'myapp_models.png'],

    # Show the current settings used in the Django project
    'show_settings': ['show_settings'],

    # Display the project dependencies (such as installed packages)
    'show_dependencies': ['show_dependencies'],

    # Clear expired sessions from the database
    'clearsessions': ['clearsessions'],

    # Run Django shell
    'shell_plus': ['shell_plus'],  # Enhanced Django shell with auto-imports

    # Export the SQL schema of your database
    'sqldiff': ['sqldiff'],

    # List all the management commands available to the project
    'show_commands': ['show_commands'],

    # Test the outgoing email configuration (send a test email)
    'sendtestemail': ['sendtestemail', 'youremail@example.com'],

    # Print SQL queries for a given model
    'print_sql': ['print_sql', 'myapp.MyModel'],

    # Reset the migrations and create a fresh migration for all apps
    'reset_db': ['reset_db'],

    # Execute a particular database command
    'dbshell': ['dbshell'],

    # Displays the `admin` URL with the proper hostname and port configuration
    'show_admin_url': ['show_admin_url'],

    # Create a new superuser
    'createsuperuser': ['createsuperuser'],

    # Open an interactive Python debugger shell for development
    'runserver_plus': ['runserver_plus'],
}
