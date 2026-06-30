from .service import AuditUsage


def audit_usage_decorator():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize auditor, passing session or other parameters if needed
            auditor = AuditUsage()

            cls = args[0]
            user_id = cls.user_info.get("user_id")
            chat_id = cls.user_info.get("chat_id")
            intent_name = cls.intent_name
            old_df = args[1]
            try:
                auditor.start()
                
                if not args or len(args) <= 1 or not isinstance(intent_name, str):
                    raise ValueError("Invalid intent_name: args[1] must be a string and should be provided.")

                auditor.set_step_name(intent_name)

                # Call the original function
                dataframe, success, metadata, message, new_df, details = func(*args, **kwargs)

                # Set auditor status and details based on function execution
                auditor.set_status(success)

                auditor.compute_record_change(intent_name, old_df, dataframe)

            except Exception as e:
                auditor.set_status(False)
                success = False
                metadata = None
                dataframe = None
                message = f"Function failed: {str(e)}"
                new_df = None
                details = None

            finally:
                # Ensure the audit ends even if an exception occurs
                auditor.end()
                auditor.save_audit_record(user_id, chat_id, schedule_id=None, run_id=None, execution_type="pipeline")

            return dataframe, success, metadata, message, new_df, details

        return wrapper
    return decorator
