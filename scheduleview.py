import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import WorkSchedule, DaySchedule
from .forms import WorkScheduleForm, DayScheduleForm
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import inlineformset_factory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Admin check function
def admin_check(user):
    logger.debug(f"Checking if user '{user.username}' is an admin or part of the 'Admins' group.")
    result = user.is_superuser or user.groups.filter(name='Admins').exists()
    logger.debug(f"Admin check result for user '{user.username}': {result}")
    return result

@user_passes_test(admin_check)
def manage_work_schedules(request):
    logger.debug("Entering manage_work_schedules view.")

    # Fetch all work schedules and associated day schedules
    schedules = WorkSchedule.objects.all().select_related('employee')
    schedule_count = schedules.count()
    logger.debug(f"Found {schedule_count} work schedules in the database.")

    # Get the current date and determine the start of the current week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week

    # Prepare the data for the frontend (JSON serializable format)
    schedule_data = []
    if schedule_count > 0:
        logger.info("List of work schedules and their associated day schedules:")
        for schedule in schedules:
            logger.info(f"Work Schedule ID: {schedule.id}, Employee: {schedule.employee}")

            # Prepare day schedules for this employee
            day_schedules = schedule.schedules.all()
            for day_schedule in day_schedules:
                # Calculate the date for each `day_of_week`
                day_offset = {
                    'Monday': 0,
                    'Tuesday': 1,
                    'Wednesday': 2,
                    'Thursday': 3,
                    'Friday': 4,
                    'Saturday': 5,
                    'Sunday': 6,
                }[day_schedule.day_of_week]

                event_date = start_of_week + timedelta(days=day_offset)

                # Format the full start and end datetime
                full_start = event_date.strftime('%Y-%m-%d') + f'T{day_schedule.start_time}'
                full_end = event_date.strftime('%Y-%m-%d') + f'T{day_schedule.end_time}'

                schedule_data.append({
                    'title': f'{schedule.employee} - {day_schedule.work_type.capitalize()}',
                    'start': full_start,
                    'end': full_end,
                    'employee': str(schedule.employee),
                    'day_of_week': day_schedule.day_of_week,
                    'active': day_schedule.active,
                    'description': f'{day_schedule.work_type.capitalize()} work, {day_schedule.start_time} to {day_schedule.end_time}',
                    'backgroundColor': '#1f77b4'  # Default to blue, you can make this dynamic
                })

                logger.info(f"  - {day_schedule.day_of_week}: {'Active' if day_schedule.active else 'Inactive'}, "
                            f"Work Type: {day_schedule.work_type}, Start: {day_schedule.start_time}, End: {day_schedule.end_time}")
    else:
        logger.info("No work schedules found in the database.")

    # Pass the data as JSON to the template
    schedule_data_json = json.dumps(schedule_data, cls=DjangoJSONEncoder)

    # Render the template
    logger.debug("Rendering the 'admin/manage_schedules.html' template with the fetched schedules.")
    return render(request, 'admin/manage_schedules.html', {'schedule_data': schedule_data_json})


# Edit work schedule
@user_passes_test(admin_check)
def edit_work_schedule(request, schedule_id):
    logger.debug(f"Entering edit_work_schedule view for schedule ID: {schedule_id}")

    # Get the specific work schedule by ID
    schedule = get_object_or_404(WorkSchedule, id=schedule_id)
    logger.debug(f"Successfully retrieved work schedule: {schedule}")

    # Define inline formset for DaySchedule
    DayScheduleFormSet = inlineformset_factory(WorkSchedule, DaySchedule, fields=('day_of_week', 'start_time', 'end_time', 'active', 'work_type'))

    if request.method == 'POST':
        logger.debug(f"Received POST request for schedule ID: {schedule_id}. Processing form data.")

        # Populate the formset with POST data
        formset = DayScheduleFormSet(request.POST, instance=schedule)
        logger.debug(f"Created formset from POST data: {formset}")

        if formset.is_valid():
            logger.debug("Formset is valid. Saving changes.")
            formset.save()
            logger.debug("Successfully updated the schedule.")
            return JsonResponse({'success': True})
        else:
            logger.debug(f"Formset is invalid: {formset.errors}")
            return JsonResponse({'success': False, 'errors': formset.errors})
    
    logger.debug("Handling GET request to display the edit form.")
    formset = DayScheduleFormSet(instance=schedule)
    logger.debug(f"Rendering formset in the 'admin/schedule_modal_form.html' template.")
    return render(request, 'admin/schedule_modal_form.html', {'formset': formset, 'schedule': schedule})

# Delete work schedule
@user_passes_test(admin_check)
def delete_work_schedule(request, schedule_id):
    logger.debug(f"Entering delete_work_schedule view for schedule ID: {schedule_id}")

    # Find the schedule to be deleted
    schedule = get_object_or_404(WorkSchedule, id=schedule_id)
    logger.debug(f"Schedule found: {schedule}. Proceeding with deletion.")

    # Delete the schedule
    schedule.delete()
    logger.debug(f"Successfully deleted schedule ID: {schedule_id}")

    # Return success response
    return JsonResponse({'success': True})

# Employee schedule view
def employee_schedule_view(request):
    """
    View for employees to see their work schedule for the week.
    """
    logger.debug(f"Entering employee_schedule_view for user: {request.user.username}")

    # Get the current user's work schedule
    work_schedule = WorkSchedule.objects.filter(employee=request.user).first()
    if work_schedule:
        logger.debug(f"Work schedule found for user '{request.user.username}': {work_schedule}")
    else:
        logger.debug(f"No work schedule found for user '{request.user.username}'.")

    # Prepare events data for FullCalendar
    events = []
    if work_schedule:
        logger.debug(f"Preparing events for FullCalendar from the work schedule.")
        for schedule in work_schedule.schedules.all():
            logger.debug(f"Processing schedule for day: {schedule.day_of_week}, active status: {schedule.active}")
            if schedule.active:
                day_offset = {
                    'Sunday': 6,
                    'Monday': 0,
                    'Tuesday': 1,
                    'Wednesday': 2,
                    'Thursday': 3,
                    'Friday': 4,
                    'Saturday': 5,
                }.get(schedule.day_of_week, 0)

                event_start = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(days=day_offset)
                logger.debug(f"Calculated event start time: {event_start}")

                event_data = {
                    'title': f"Work - {'Office' if schedule.work_type == 'office' else 'Remote'}",
                    'start': f"{event_start.date()}T{schedule.start_time}",
                    'end': f"{event_start.date()}T{schedule.end_time}",
                }
                events.append(event_data)
                logger.debug(f"Event added: {event_data}")

    # Debug: Check if events list is empty
    if not events:
        logger.debug(f"No events found for user '{request.user.username}'.")
        message = "No active work schedule found for this week."
    else:
        logger.debug(f"{len(events)} events prepared for user '{request.user.username}'.")
        message = ""

    # Debug: Output the final context
    context = {
        'events': json.dumps(events, cls=DjangoJSONEncoder),
        'message': message
    }
    logger.debug(f"Final context being passed to template: {context}")

    return render(request, 'scheduletemp.html', context)


def editsched(request):
    return render(request, "admin/exampsched.html")