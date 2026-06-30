import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
from notification.email.service import SMTPNotifier

class TestSMTPNotifier(unittest.TestCase):

    @patch('notification.email.utils.get_templates')
    @patch('notification.email.service.send_email')
    def test_notifier(self, mock_send_email, mock_get_templates):
        mock_subject_template = MagicMock()
        mock_body_template = MagicMock()
        
        # Define mock template rendering return values
        mock_subject_template.render.return_value = 'Test Subject'
        mock_body_template.render.return_value = 'Test Email Body'

        # Configure the mock for `get_templates`
        mock_get_templates.side_effect = [mock_subject_template, mock_body_template]
        
        # Define test context
        test_context = {
            'timezone': 'Asia/Kolkata',
            'schedule_name': 'Daily Run',
            'job_name': 'Data Processing',
            'subject': 'Custom Subject',
            'status': 'success',
            'details': {
                'to': 'test@example.com',
                'subject': 'Custom Subject'
            }
        }
        
        # Initialize SMTPNotifier and call notifier
        notifier = SMTPNotifier()
        notifier.notifier(**test_context)

        # Extract the actual call arguments
        self.assertEqual(mock_send_email.call_count, 1)
        
        

if __name__ == '__main__':
    unittest.main()
