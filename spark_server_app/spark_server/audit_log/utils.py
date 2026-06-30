from .service import AuditUsage
from pyspark.sql import DataFrame
from ..logger.logger import logger


def audit_usage_decorator():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize auditor, passing session or other parameters if needed
            auditor = AuditUsage()
            cls = args[0]
            schedule_id = cls.schedule_id
            run_id = cls.run_id
            intent_name = cls.intent_name
            user_id = cls.user_id
            chat_id = cls.chat_id
            execution_type = cls.execution_type
            # in this case, the old_df can either be a dict or a DataFrame
            old_df = args[1]
            
            try:
                auditor.start()

                auditor.set_step_name(intent_name)

                # Call the original function
                new_dataframe = func(*args, **kwargs)
                success = True
                
                # Set auditor status and details based on function execution
                auditor.set_status(success)

                auditor.compute_record_change(intent_name, old_df, new_dataframe)

            except Exception as e:
                # Log the exception in the audit (optional)
                auditor.set_status(False)
                raise e

            finally:
                # Ensure the audit ends even if an exception occurs
                auditor.end()
                auditor.save_audit_record(user_id=user_id, chat_id=chat_id, schedule_id=schedule_id, run_id=run_id, execution_type=execution_type)

            # Return the results from the original function or fallback in case of failure
            return new_dataframe

        return wrapper
    return decorator
