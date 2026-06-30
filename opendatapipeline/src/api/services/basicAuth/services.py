from datetime import datetime, timedelta
from time import timezone
from core.mongo.read_connector import ReadMongoConnector
from core.mongo.connector import MongoConnector
from ....models.udf.UsersModel import Users
from ...validators.jwt_authentication import JWTAuthentication
import logging
import os
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent

logging.basicConfig(level=logging.DEBUG)

environment = os.environ.get("SERVER_ENVIRONMENT")

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client

class UserServices(ServiceParent):
    """
    Service class for handling user registration and login operations.

    :param session: The database session for interacting with the user model.
    :type session: object
    """

    def __init__(self,session=None):
        """
        Constructor method.

        :param session: The database session for interacting with the user model.
        :type session: object
        """
        super().__init__(session)
    
    @Logger.generate
    def register(self, request):
        """
        Registers a new user.

        :param request: The HTTP request object containing the user registration data.
        :type request: flask.Request
        :return: A dictionary with success status and message, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises UtilityException: If an error occurs during the registration process.
        """
        try:
            logger.info("User registration started")
            req_data = request.get_json()
            email=req_data["email"]
            password=req_data["password"]
            user_exists = Users(req_data,session=self.session).get_by_email(email)
            user_id = str(user_exists["_id"]) if user_exists else None
            if user_exists is None:
                new_user = Users(req_data, session=self.session)
                new_user.set_password(password)
                new_user.save()
                new_user.setup()
                logger.info("User Registration Successful")
                return {
                    "success": True,
                    "msg": "Registration Successful. Please login"
                }, 200
            else:# pragma: no cover
                raise Exception("Already Registered. Please Login")
                # return {
                #     "success": True,
                #     "msg": f"{email} Already Registered. Please Login"
                # }, 200
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "msg": f"{e}",
                # "msg": "Please provide a valid input.",
                "error": "An error occurred"
            }, 500

    @Logger.generate
    def login(self, request):
        """
        Logs in an existing user.

        :param request: The HTTP request object containing the user login data.
        :type request: flask.Request
        :return: A dictionary with success status, user ID, token, user details, and message, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises UtilityException: If an error occurs during the login process.
        """
        try:
            req_data = request.get_json()
            email = req_data.get("email")
            password = req_data.get("password")
            user_exists = Users(req_data,session=self.session).get_by_email(email)
            user_id = str(user_exists["_id"]) if user_exists else None

            if user_exists is None:
                raise Exception("Please Register The account First.")
                # return {
                #     "success": True,
                #     "msg": "Please Register The account First."
                # }, 200
            if not Users(req_data,session=self.session).check_password(user_exists["password"],password): # pragma: no cover
                raise Exception("Wrong credentials.")
                            # return {"success": False, "msg": "Wrong credentials."}, 400
            else:
                token = JWTAuthentication().encode(email, user_id)
                name=user_exists["name"]
                del user_exists["_id"]
                del user_exists["password"]
                del user_exists["date_joined"]
                del user_exists["role"]
                logger.info("User login successful")
                return {
                    "success": True,
                    "userid": user_id,
                    "token": token,
                    "users":user_exists,
                    "msg": f"Welcome back {name}! Getting your workspace ready."
                }, 200
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "msg" : f"{e}",
                # "msg": "Please provide a valid input.",
                "error": "An error occurred"
            }, 500


    def api_key_generation(self, request):
        """
        Creating an jwt token from user_id, user email id and with expiration time .

        :param request: The HTTP request object containing the user data, expiry_date in YYYY-MM-DD format

        :return: A dictionary with success status, user ID, token, and HTTP status code.
        :raises Exception: If an error occurs during the token creation and updation process.
        """
        try:
            data = request.json
            email = data.get("email")
            token_name = data.get("token_name")
            expiry_date = data.get("expiry_date")

            # Default expiry period: 60 days from today
            if not expiry_date:
                expiry_days = 60
            else:
                try:
                    expiry_datetime = datetime.strptime(expiry_date, "%Y-%m-%d")  # Convert to datetime
                    expiry_days = (expiry_datetime.date() - datetime.utcnow().date()).days
                    if expiry_datetime < datetime.utcnow():
                        return {"success": False, "msg": "Expiry date cannot be in the past"}, 400
                except ValueError:
                    return {"success": False, "msg": "Invalid expiry_date format. Expected YYYY-MM-DD."}, 400

            expiry_minutes = expiry_days * 60 * 24

            user_exists = Users(data,session=self.session).get_by_email(email)

            user_id = str(user_exists["_id"]) if user_exists else None
            if not user_id:
                return {"success": False, "msg": "Invalid user credentials"}, 401
            token = JWTAuthentication().encode(email, user_id, expiry_in_minutes = expiry_minutes)
            expiration_time = (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
          
            user_data = {
                "api_key": token,
                "api_key_expiry_date": expiration_time,
                "token_name":token_name,
            }

            result = mongo_client.users.update_one(
                {"_id": user_exists["_id"]}, 
                {"$set": user_data}
                )
            return {"success": True, "api_key": token , "expires_at": expiration_time,"token_name" : token_name}, 200      

        except Exception as e: 
            logger.error(str(e), exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "msg" : f"{e}",
                "error": "An error occurred"
            }, 400
    
    def get_api_key(self, _id):
        """
        get the jwt token with token_name, user id,token name and with expiration time .
        If the token details are not present in mongo return empty string

        :param request: The HTTP request object containing the user id.
        :return: A dictionary with success status, user ID, token, user details and HTTP status code.
        :raises Exception: If an error occurs during the getting the access token .
        """
        try:
            
            user_data = Users.get_by_user_id(_id)
            if not user_data:
                return {"success": False, "message": "User not present"}, 400  
            
            if (not user_data.get("api_key") or not user_data.get("api_key_expiry_date") or not user_data.get("token_name")):
                return {"success": True, "api_key": "" , "expiry_date": "" ,"token_name" : ""},200

            expiration_time = user_data["api_key_expiry_date"]

            return {"success": True, "api_key": user_data["api_key"] , "expiry_date": expiration_time ,"token_name" : user_data["token_name"]}, 200      

        except Exception as e: 
            logger.error(str(e), exc_info=True)
            return {
                "success": False,
                "msg" : f"{e}",
                "error": "An error occurred"
            }, 400
      
    def delete_jwt_api_key(self, user_id):
        """
        delete the api key details from the user table 
        """
        try:
            result = Users.delete_api_key(user_id)
            if result.modified_count > 0:
                return {"success": True, "message": "API key and related fields removed successfully."},200
            else:
                return {"success": False, "message": "User not found or fields already removed."} ,400

        except Exception as e: 
            logger.error(str(e), exc_info=True)
            # self.session.abort_transaction()
            self._safe_abort_transaction()
            return {
                "success": False,
                "msg" : f"{e}",
                "error": "An error occurred"
            }, 400