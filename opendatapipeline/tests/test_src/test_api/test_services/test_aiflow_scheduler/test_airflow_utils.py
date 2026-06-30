import unittest
from datetime import datetime
import uuid

from requests import patch
from src.api.services.airflow_service.utils import RestTriggerUtils
from src.api.services.airflow_service.utils import NotificationUtils
from src.api.services.airflow_service.utils import ExportPipeline
from src.models.connector import MongoConnector
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestNotificationUtils(unittest.TestCase):
    def test_get_notification_details(self):
        user_id = "66c884e41b675b0e8f066ad9"
        notification = {
            "type": "email",
            "details": {
                "to": "already_set@example.com",
                "subject": "Test Subject"
            }
        }
        
        result = NotificationUtils(session).get_notification_details(user_id, notification)
        
        expected = {
            "type": "email",
            "details": {
                "to": "already_set@example.com",
                "subject": "Test Subject"
            }
        }
        
        self.assertEqual(result, expected)

    def test_prepare_schedule_data_with_all_params(self):
        job_id = "job_123"
        user_id = "user_456"
        schedule_interval = "0 0 * * *"
        advanced_scheduling = {"repeat_by": "monthly", "day_of_month": True}
        pipeline = [{"task": "task1"}, {"task": "task2"}]
        config = {"key": "value"}
        schedule_name = "Daily Job"
        code = "JOB_CODE_789"
        replace_connections = {"old_conn": "new_conn", "key1": "conn1", "key2": "conn2"}
        notification = {"type": "email", "details": {"to": "example@example.com"}}
        engine_type = "spark"
        generated_cron_expression = "0 0 * * *"

        expected = {
            "chat_id": job_id,
            "user_id": user_id,
            "schedule_name": schedule_name,
            "engine_type":engine_type,
            "export_files_list": [],
            "schedule_interval": schedule_interval,
            "generated_cron_expression":generated_cron_expression,
            "advanced_scheduling": advanced_scheduling,
            "pipeline": pipeline,
            "configurations": config,
            "code": code,
            "replace_connections": replace_connections,
            "notification": notification,
            "type": "localstorage",
            "execution_type": "code",
            "job_details": {"files_list": [], "type": "localstorage"},
            "export_format" : None
        }

        result = ExportPipeline().prepare_schedule_data(
            job_id=job_id,
            user_id=user_id,
            schedule_interval=schedule_interval,
            advanced_scheduling=advanced_scheduling,
            pipeline=pipeline,
            config=config,
            schedule_name=schedule_name,
            code=code,
            engine_type=engine_type,
            generated_cron_expression=generated_cron_expression,
            replace_connections=replace_connections,
            notification=notification,
            export_files_list=[],
            type="localstorage",
            execution_type="code",
            job_details={"files_list": [], "type": "localstorage"}
        )
        
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()

class TestRestTriggerUtils(unittest.TestCase):
    
    def setUp(self):
        self.utils = RestTriggerUtils()

    def test_generate_cron_minutely(self):
        result = self.utils.generate_cron("minutely", 5, [], "", False, False)
        self.assertEqual(result, "*/5 * * * *")

    def test_generate_cron_hourly(self):
        result = self.utils.generate_cron("hourly", 2, [], "", False, False)
        self.assertEqual(result, "0 */2 * * *")

    def test_generate_cron_daily(self):
        result = self.utils.generate_cron("daily", 3, [], "", False, False)
        self.assertEqual(result, "0 0 */3 * *")

    def test_generate_cron_weekly_with_days_of_week(self):
        result = self.utils.generate_cron("weekly", 1, ["Monday", "Wednesday"], "", False, False)
        self.assertEqual(result, "0 0 * * 1,3")

    def test_generate_cron_weekly_default(self):
        result = self.utils.generate_cron("weekly", 1, [], "", False, False)
        self.assertEqual(result, "0 0 * * 0")

    def test_generate_cron_monthly_day_of_month(self):
        result = self.utils.generate_cron("monthly", 1, [], "2024-08-15", True, False)
        self.assertEqual(result, "0 0 15 */1 *")

    def test_generate_cron_monthly_day_of_week(self):
        result = self.utils.generate_cron("monthly", 1, [], "2024-08-15", False, True)
        self.assertEqual(result, "0 0 * * 4#3")  

    def test_generate_cron_yearly(self):
        result = self.utils.generate_cron("yearly", 1, [], "", False, False)
        self.assertEqual(result, "0 0 1 1 */1")

    def test_generate_cron_invalid_repeats(self):
        with self.assertRaises(ValueError):
            self.utils.generate_cron("invalid", 1, [], "", False, False)

    def test_generate_cron_invalid_repeat_by_date_format(self):
        with self.assertRaises(ValueError):
            self.utils.generate_cron("monthly", 1, [], "invalid_date", True, False)

    def test_get_week_of_month(self):
        date = datetime(2024, 8, 15)  
        result = self.utils.get_week_of_month(date)
        self.assertEqual(result, 3)

    def test_get_week_of_month_first_day(self):
        date = datetime(2024, 8, 1)  
        result = self.utils.get_week_of_month(date)
        self.assertEqual(result, 1)

    def test_get_day_of_week(self):
        date = datetime(2024, 8, 15)  
        result = self.utils.get_day_of_week(date)
        self.assertEqual(result, 4)  

    def test_get_day_of_week_sunday(self):
        date = datetime(2024, 8, 18)  
        result = self.utils.get_day_of_week(date)
        self.assertEqual(result, 0)  

if __name__ == '__main__':
    unittest.main()
