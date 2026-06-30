from datetime import datetime
import pytz
from notification.base import Basenotifierclass

from airflow.utils.email import send_email
from notification.email.utils import get_templates

class SMTPNotifier(Basenotifierclass):
    template_fields = ("message",)

    def notifier(self, **context):
        execution_date = datetime.now(pytz.utc)
        # timezone = context.get("timezone")
        schedule_name = None
        job_name = None

        if 'dag' in context:
            for tag in context.get('dag').tags:
                if tag.startswith('job_name:'):
                    job_name = tag.split(':')[1]
                elif tag.startswith('schedule_name:'):
                    schedule_name = tag.split(':')[1]

        timezone = context.get('dag').timezone.name

        # Convert execution_date to the provided timezone
        if timezone:
            target_timezone = pytz.timezone(timezone)
            execution_date = execution_date.astimezone(target_timezone)
        
        subject_template = get_templates('subject_template.html')
        body_template = get_templates('email_template.html')
        to = context.get("notify_details", {}).get('to', None)
        # subject = context.get("notify_details").get('subject')
        
        subject =  context.get("notify_details", {}).get("subject")
        schedule_id = context.get("schedule_id")
        if not schedule_id:
            raise Exception("Schedule_id is not present")
        # status = context.get("status")
        status = context.get('ti').state.split(':')[-1]
        
        # Define context for template rendering
        subject_context = {
            "job_name": job_name,
            "schedule_id": schedule_id
        }
        body_template_context = {
            "execution_date": execution_date,
            "status": status,
            "job_name": job_name,
            "schedule_name": schedule_name
        }

        # Render the template with the context
        rendered_subject = subject_template.render(subject_context)
        rendered_html = body_template.render(body_template_context)

        html_content =  context.get("notify_details", {}).get('body')
        if html_content is None:
            html_content=rendered_html
        # subject = context.get("notify_details").get('subject') if context.get("notify_details").get('subject') != None else rendered_subject
        subject = rendered_subject
        if to is not None:
            send_email(to = to, subject = subject, html_content = html_content)
