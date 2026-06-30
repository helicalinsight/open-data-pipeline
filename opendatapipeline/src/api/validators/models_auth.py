from flask_restx import fields
import os
class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'

class UDFModels:
        """
        The `Models` class provides a convenient way to manage and instantiate different models used in a Flask RESTful API.
        """
        def __init__(self):
            """
            Initializes the Models class, creating a mapping between model names and corresponding model initialization methods.

            Attributes:
                models_mapping (dict): A dictionary containing model names as keys and corresponding model initialization methods as values.
            """
            pass

        def SignUp(self):
            """
            Initializes and returns an instance of the SignUpModel.

            Returns:
                SignUpModel: An instance of the SignUpModel.
            """
            return SignUpModel()

        def Login(self):
            """
            Initializes and returns an instance of the LoginModel.

            Returns:
                LoginModel: An instance of the LoginModel.
            """
            return LoginModel()

        def UserEdit(self):
            """
            Initializes and returns an instance of the UserEditModel.

            Returns:
                UserEditModel: An instance of the UserEditModel.
            """
            return UserEditModel()

        def Google(self):
            """
            Initializes and returns an instance of the GoogleSignUp.

            Returns:
                GoogleSignUp: An instance of the GoogleSignUp.
            """
            return GoogleSignUp()


class SignUpModel:
    """
    The `SignUpModel` class represents the data model for user sign-up information.
    """
    def __init__(self):
        """
        Initializes the SignUpModel class, defining the model data attributes for user sign-up information.

        Attributes:
            model_data (dict): A dictionary containing field names and corresponding Marshmallow fields with validation rules.
        """
        self.model_data = {
            "firstname": fields.String(required=True, min_length=2, max_length=32),
            "lastname": fields.String(required=False, min_length=2, max_length=32),
            "gender": fields.String(required=True, min_length=2, max_length=32),
            "email": fields.String(required=True, min_length=4, max_length=64),
            "password": fields.String(required=True, min_length=4, max_length=16)
        }

    def model(self):
        """
        Returns the model data dictionary.

        Returns:
            dict: The model data dictionary.
        """
        return self.model_data

class LoginModel:
    """
    The `LoginModel` class represents the data model for user login information.
    """
    def __init__(self):
        """
        Initializes the LoginModel class, defining the model data attributes for user login information.

        Attributes:
            model_data (dict): A dictionary containing field names and corresponding Marshmallow fields with validation rules.
        """
        self.model_data = {
            "email": fields.String(required=True),
            "password": fields.String(required=True)
        }

    def model(self):
        """
        Returns the model data dictionary.

        Returns:
            dict: The model data dictionary.
        """
        return self.model_data

class UserEditModel:
    """
    The `UserEditModel` class represents the data model for user profile editing information.
    """
    def __init__(self):
        """
        Initializes the UserEditModel class, defining the model data attributes for user profile editing.

        Attributes:
            model_data (dict): A dictionary containing field names and corresponding Marshmallow fields with validation rules.
        """
        self.model_data = {
            "userID": fields.String(required=True, min_length=1, max_length=32),
            "firstname": fields.String(required=True, min_length=2, max_length=32),
            "email": fields.String(required=True, min_length=4, max_length=64)
        }

    def model(self):
        """
        Returns the model data dictionary.

        Returns:
            dict: The model data dictionary.
        """
        return self.model_data




class GoogleSignUp:
    """
    The `SignUpModel` class represents the data model for user sign-up information.
    """
    def __init__(self):
        """
        Initializes the SignUpModel class, defining the model data attributes for user sign-up information.

        Attributes:
            model_data (dict): A dictionary containing field names and corresponding Marshmallow fields with validation rules.
        """
        environment=os.environ.get("SERVER_ENVIRONMENT")
        if environment=="prod":
            self.model_data = {
        "id": fields.String(required=True),
        "email": fields.String(required=True),
        "verified_email": fields.Boolean(required=True),
        "name": fields.String(required=True),
        "given_name": fields.String(required=True),
        "family_name": fields.String(required=False),
        "picture": fields.Url(required=True),
}
        else:
            self.model_data = {
        "id": fields.String(required=False),
        "email": fields.String(required=False),
        "verified_email": fields.Boolean(required=False),
        "name": fields.String(required=False),
        "given_name": fields.String(required=False),
        "family_name": fields.String(required=False),
        "picture": fields.Url(required=False)
}
    def model(self):
        """
        Returns the model data dictionary.

        Returns:
            dict: The model data dictionary.
        """
        return self.model_data
