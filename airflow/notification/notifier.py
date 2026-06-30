from notification.email.service import SMTPNotifier


class Notifier:
    collection_mapping = {
        "email": SMTPNotifier
    }

    @staticmethod
    def create_object(notification):
        try:
            notification_type = notification.get('type')
            collection = Notifier.collection_mapping.get(notification_type)
            if collection is None:
                raise ValueError(f"No matching notifier found for type: {notification_type}")
            
            notification_obj = collection
            return notification_obj()
            # collection = Notifier.collection_mapping.get(collection)
            # return collection
        except Exception as e: # pragma: no cover
            print("error while creating object", str(e))
            return None
