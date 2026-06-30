from datetime import datetime

class RestTriggerUtils:
    """
    Utility class for generating CRON expressions based on various scheduling parameters.
    """
    def generate_cron(self,repeats, repeats_every, days_of_week, repeat_by, day_of_month=False, day_of_week=False):
        """
        Generates a CRON expression based on the scheduling parameters.

        :param repeats: The frequency of repetition (e.g., "minutely", "hourly", "daily", "weekly", "monthly", "yearly").
        :type repeats: str
        :param repeats_every: The interval at which the task should repeat.
        :type repeats_every: int
        :param days_of_week: List of days of the week on which the task should run (for weekly schedules).
        :type days_of_week: list of str
        :param repeat_by: Date or format to determine repeat schedule (e.g., "2024-07-01" for monthly, or "2 3" for weekly).
        :type repeat_by: str
        :param day_of_month: Whether to repeat by day of the month (for monthly schedules).
        :type day_of_month: bool
        :param day_of_week: Whether to repeat by day of the week (for monthly schedules).
        :type day_of_week: bool
        :return: The generated CRON expression.
        :rtype: str
        :raises ValueError: If parameters are invalid or in incorrect format.
        """
        if repeats == "minutely":
            return f"*/{repeats_every} * * * *"
        elif repeats == "hourly":
            return f"0 */{repeats_every} * * *"
        elif repeats == "daily":
            return f"0 0 */{repeats_every} * *"
        elif repeats == "weekly":
            if days_of_week:
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                days_str = ",".join(str(days.index(day)) for day in days_of_week)
                return f"0 0 * * {days_str}"
            else:
                return f"0 0 * * 0"  # Sunday as the default
        elif repeats == "monthly":
            if day_of_month:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    day_of_month = date.day
                    return f"0 0 {day_of_month} */{repeats_every} *"
                except ValueError:
                    raise ValueError("Invalid date format for repeat_by. It must be in the format 'dd-mm-yyyy'.")
            elif day_of_week:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    week_of_month = RestTriggerUtils().get_week_of_month(date)
                    day_of_week =  RestTriggerUtils().get_day_of_week(date)
                    return f"0 0 * * {day_of_week}#{week_of_month}"
                except ValueError:
                    raise ValueError("Invalid format for repeat_by. It must be in the format 'week_of_month day_of_week' (e.g., '2 3').")  
            else:
                raise ValueError("Invalid repeat_by_format. It must be either 'day_of_month' or 'day_of_week'.")
        elif repeats == "yearly":
            return f"0 0 1 1 */{repeats_every}"
        else:
            raise ValueError("Invalid repeat interval")
        

    def get_week_of_month(self, date):
        """
        Determines the week of the month for the given date.

        :param date: The date to determine the week of the month for.
        :type date: datetime
        :return: The week number of the month.
        :rtype: int
        """
        # Find the first day of the month
        first_day = date.replace(day=1)
        # Calculate the day of the week for the first day of the month (0=Monday, 6=Sunday)
        first_day_weekday = first_day.weekday()
        # Calculate the week number
        if first_day_weekday == 6:
            # If the first day is Sunday, then the first week starts from day 1 to day 7
            week_number = (date.day - 1) // 7 + 1
        else:
            # Calculate the week number based on the first day of the month
            week_number = (date.day + first_day_weekday - 1) // 7 + 1
        return week_number

    def get_day_of_week(self, date):
        """
        Determines the day of the week index for the given date.

        :param date: The date to determine the day of the week for.
        :type date: datetime
        :return: The day index (0=Sunday, 6=Saturday).
        :rtype: int
        """
        # Define a list of day names
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        # Get the weekday number (0=Sunday, 6=Saturday)
        day_index = date.strftime("%A")  
        # Return the corresponding day index
        return days.index(day_index)
        
