import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from src.api.services.audit_log.service import AuditUsage
from dataclasses import dataclass


@dataclass
class ComputationResult:
    rows: int
    cols: int
    cost: int

class TestAuditUsageService(unittest.TestCase):

    def test_start(self):
        audit_usage = AuditUsage()  
        audit_usage.start()         
        self.assertIsNotNone(audit_usage._start_timestamp)  
        self.assertTrue(isinstance(audit_usage._start_timestamp, datetime))

    def test_end(self):
        audit_usage = AuditUsage()  
        audit_usage.end()         
        self.assertIsNotNone(audit_usage._end_timestamp)  
        self.assertTrue(isinstance(audit_usage._end_timestamp, datetime))

    def test_set_status(self):
        status = "success"
        audit_usage = AuditUsage()  
        audit_usage.set_status(status)       
        self.assertEqual(audit_usage._status, status)

    def test_set_step_name(self):
        step_name = "test_step"
        audit_usage = AuditUsage()  
        audit_usage.set_step_name(step_name)
        self.assertEqual(audit_usage._step_name, step_name)

    def test_compute_record_change_valid_step(self):
        step_name = "concat"
        audit_usage = AuditUsage() 
        old_df = MagicMock()
        old_df.size = 20   
        df = MagicMock()
        df.size = 20  
        step_compute_class = Mock()
        step_compute_class.compute.return_value = ComputationResult(rows=20, cols=2, cost=40)
        audit_usage._custom_record_computation = {
            step_name: step_compute_class
        }
        
        audit_usage.compute_record_change(step_name, old_df, df)
        self.assertEqual(audit_usage._records_processed, 40)
        self.assertEqual(audit_usage._rows, 20)
        self.assertEqual(audit_usage._cols, 2)
        audit_usage._custom_record_computation[step_name].compute.assert_called_once_with(old_df, df)

    def test_compute_record_change_invalid_step(self):
        step_name = "invalid_step"
        audit_usage = AuditUsage()  
        old_df = MagicMock()
        old_df.size = 20   
        df = MagicMock()
        df.size = 20
        df.shape = [10, 2]
        step_compute_class = Mock()
        step_compute_class.compute.return_value = ComputationResult(rows=20, cols=2, cost=40)
        audit_usage._custom_record_computation = {
            "concat": step_compute_class
        }

        audit_usage.compute_record_change(step_name, old_df, df)
        
        self.assertEqual(audit_usage._records_processed, 20)
        self.assertEqual(audit_usage._rows, 10)
        self.assertEqual(audit_usage._cols, 2)

    @patch('src.models.mongo.mongo_factory.MongoFactory.insert_one')
    def test_save_audit_record(self, mock_insert_one):
        mock_insert_one.return_value = (True, "12345")
        audit_usage = AuditUsage() 
        audit_usage._step_name = "test_step"
        audit_usage._start_timestamp = datetime.now()
        audit_usage._end_timestamp = datetime.now()
        audit_usage._records_processed = 100
        audit_usage._rows = 50
        audit_usage._cols = 2
        audit_usage._status = "success"
        
        user_id = "user_1"
        chat_id = "chat_1"
        schedule_id = None
        run_id = "run_1"
        execution_type = "code"
        
        audit_usage.save_audit_record(user_id, chat_id, schedule_id, run_id, execution_type)
        
        expected_record = {
            "user_id": user_id,
            "chat_id": chat_id,
            "schedule_id": schedule_id if schedule_id else None,
            "run_id": run_id,
            "execution_type": execution_type,
            "step_name": "test_step",
            "start_time": audit_usage._start_timestamp,
            "end_time": audit_usage._end_timestamp,
            "step_cost": 100,
            "step_status": "success",
            "rows": audit_usage._rows,
            "cols": audit_usage._cols
        }

        mock_insert_one.assert_called_once_with(expected_record)

    @patch('src.models.mongo.mongo_factory.MongoFactory.find')
    def test_get_audit_with_filters_and_time_range(self, mock_find):
        user_id = "user_123"
        req_data = {
            "chat_id": "chat_abc",
            "schedule_id": "sched_1",
            "run_id": "run_42",
            "mode": "pipeline",
            "start_time": "2025-08-04T00:00",
            "end_time": "2025-08-04T23:59"
        }
        # Prepare two step docs for same (chat_id, schedule_id, run_id)
        step1_start = datetime(2025, 8, 4, 5, 30, 23)
        step1_end = datetime(2025, 8, 4, 8, 1, 42)
        step2_start = datetime(2025, 8, 4, 6, 0, 0)
        step2_end = datetime(2025, 8, 4, 7, 0, 0)  # earlier end to match current min() behavior in code
        mock_find.return_value = [
            {
                "user_id": user_id,
                "chat_id": req_data["chat_id"],
                "schedule_id": req_data["schedule_id"],
                "run_id": req_data["run_id"],
                "execution_type": req_data["mode"],
                "service_type": "dts",
                "step_cost": 5,
                "rows": 10,
                "cols": 2,
                "start_time": step1_start,
                "end_time": step1_end
            },
            {
                "user_id": user_id,
                "chat_id": req_data["chat_id"],
                "schedule_id": req_data["schedule_id"],
                "run_id": req_data["run_id"],
                "execution_type": req_data["mode"],
                "service_type": "dts",
                "step_cost": 7,
                "rows": 3,
                "cols": 4,
                "start_time": step2_start,
                "end_time": step2_end
            }
        ]

        audits_resp, status = AuditUsage().get_audit(user_id, req_data)
        self.assertEqual(status, 200)
        self.assertIn('Audits', audits_resp)
        self.assertEqual(len(audits_resp['Audits']), 1)

        audit = audits_resp['Audits'][0]
        self.assertEqual(audit['Chat_id'], req_data['chat_id'])
        self.assertEqual(audit['Schedule_id'], req_data['schedule_id'])
        self.assertEqual(audit['Run_id'], req_data['run_id'])
        self.assertEqual(audit['mode'], req_data['mode'])
        # Aggregations
        self.assertEqual(audit['Total_run_cost'], 12)
        self.assertEqual(audit['Total_rows'], 13)
        self.assertEqual(audit['Total_cols'], 6)
        self.assertEqual(audit['Total_steps'], 2)
        # Start is min of starts; End uses current code's min of ends
        self.assertEqual(
            audit['run_start_time'], 
            min(step1_start.isoformat(), step2_start.isoformat()))
        self.assertEqual(
            audit['run_end_time'], 
            max(step1_end.isoformat(), step2_end.isoformat()))

        # Verify query contents used for find
        called_query = mock_find.call_args[0][0]
        self.assertEqual(called_query["user_id"], user_id)
        self.assertEqual(called_query["chat_id"], req_data["chat_id"])
        self.assertEqual(called_query["schedule_id"], req_data["schedule_id"])
        self.assertEqual(called_query["run_id"], req_data["run_id"])
        self.assertEqual(called_query["execution_type"], req_data["mode"])
        self.assertIn("start_time", called_query)
        self.assertIn("end_time", called_query)
        self.assertTrue(isinstance(called_query["start_time"]["$gte"], datetime))
        self.assertTrue(isinstance(called_query["end_time"]["$lte"], datetime))

    @patch('src.models.mongo.mongo_factory.MongoFactory.find')
    def test_get_audit_without_time_range(self, mock_find):
        user_id = "user_999"
        req_data = {
            "chat_id": None,
            "schedule_id": None,
            "run_id": None,
            "mode": None
        }
        now_start = datetime(2025, 1, 1, 0, 0, 0)
        now_end = datetime(2025, 1, 1, 1, 0, 0)
        mock_find.return_value = [
            {
                "user_id": user_id,
                "chat_id": "chatX",
                "schedule_id": None,
                "run_id": "runX",
                "execution_type": "pipeline",
                "service_type": "dts",
                "step_cost": 2,
                "rows": 1,
                "cols": 1,
                "start_time": now_start,
                "end_time": now_end
            }
        ]

        audits_resp, status = AuditUsage().get_audit(user_id, req_data)
        self.assertEqual(status, 200)
        self.assertIn('Audits', audits_resp)
        self.assertEqual(len(audits_resp['Audits']), 1)

        # Ensure find called with only user_id when no time range supplied
        called_query = mock_find.call_args[0][0]
        self.assertEqual(called_query, {"user_id": user_id})


if __name__ == "__main__":
    unittest.main()
