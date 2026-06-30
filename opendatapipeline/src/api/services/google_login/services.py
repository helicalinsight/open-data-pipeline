from ....models.udf.GoogleUserModels import GoogleUsers
from ...validators.jwt_authentication import JWTAuthentication
import logging
import os
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent

environment=os.environ.get("SERVER_ENVIRONMENT")

class GoogleLoginService(ServiceParent):
	"""Service class for handling Google login operations.

    This class manages Google authentication, including checking if a user
    already exists and creating a new user if necessary. It also handles
    JWT token generation for authenticated users.
    """

	def __init__(self,session=None):
		"""Initializes the GoogleLoginService with a session.

        :param session: The database session to use for operations.
        :type session: Session
        """
		super().__init__(session)
	
	@Logger.generate
	def google_login(self, request):
		"""Handles the Google login process.

        Retrieves user information from the Google login request, checks if
        the user already exists in the database, and either creates a new user
        or retrieves the existing user's ID. It then generates a JWT token
        for the user and returns a response with the user's ID, token, and a
        message.

        :param request: The HTTP request object containing the Google login data.
        :type request: Request
        :return: A dictionary containing the success status, user ID, JWT token,
                 and a message. HTTP status code 200 for success, 500 for errors.
        :rtype: tuple(dict, int)
        :raises Exception: If an error occurs during the login process.
        """
		try:

			
			req_data = request.get_json()
			google_id = req_data.get("id")
			email = req_data.get("email")
			name = req_data.get("given_name")
			user_exists = GoogleUsers(req_data, session=self.session).get_by_id(google_id)
			user_id = str(user_exists["_id"]) if user_exists else None

			if user_exists is None:
					new_user = GoogleUsers(req_data, self.session)
					new_user.save()
					new_user.setup()
					token = JWTAuthentication().encode(email, new_user._id)
					logger.info("Kindly await while we configure everything for you.")
					return {
						"success": True,
						"userid": new_user._id,
						"token": token,
						"msg": "Kindly await while we configure everything for you."
					}, 200
			else:
					token = JWTAuthentication().encode(email, user_id)
					logger.info(f"Welcome back {name}! Getting your workspace ready.")
					return {
						"success": True,
						"userid": user_id,
						"token": token,
						"msg": f"Welcome back {name}! Getting your workspace ready."
					}, 200	

		except Exception as e: # pragma: no cover
			logger.error(f"{e}", exc_info=True)
			self._safe_abort_transaction()  
			return {
				"success": False,
				"msg": "Please provide a valid input.",
				"error": "An error occurred"
			}, 500