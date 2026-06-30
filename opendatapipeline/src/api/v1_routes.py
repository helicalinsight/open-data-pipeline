# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import shutil
import uuid
import time

from src.exceptions.exception import LangchainServiceException


from .services.files.service import FileService, FileServiceCache
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from bson import ObjectId
from flask import  send_file, send_from_directory, request
from flask_restx import Api, Resource, reqparse, fields ,Namespace
from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern

from flask import render_template, make_response, Blueprint
import os
from ..logger.logger import Logger, logger

from .services.undo_redo.service import UndoRedoService
from .services.files.service import FileService
from .services.chat.service import ChatService
from .services.chat_history.service import ChatHistoryService
from .services.pipeline.service import PipelineHistoryService
from .services.catalogs.service import ListCatalogsService
from .services.data_connector.service import DataConnectorsService
from .services.data_sources.service import DatasourcesService
from .services.saved_connections.service import SavedConnectionsService
from .services.google_login.services import GoogleLoginService
from .services.connections.service import ConnectionService
from .services.upload_config.service import UploadConfigService
from .services.data_loads.service import DataLoadService
from .services.execute.service import ExecuteService
from .services.download.service import DownloadService
from .services.export_config.service import ExportConfigService
from .services.get_application.service import ApplicationService
from .services.basicAuth.services import UserServices
from .services.settings.service import SettingsService
from .validators.jwt_authentication import *
from .validators.models_auth import UDFModels
from . services.changeCWF.services import ChangeCWF
from .services.airflow_service.service import AirflowAPI
from .services.rerun.service import ReRunService
from .services.pyspark_service.service import PySparkCodeGenerator
from .services.audit_log.service import AuditUsage
from .services.s3.service import S3Service

from core.mongo.connector import MongoConnector
from core.mongo.read_connector import ReadMongoConnector 
from ..configurations.api.config import BaseConfig,SourceConfig
import configparser


from ..hooks.database_connector import DatabaseConnector
import json

from ..models.mongo.mongo_factory import MongoFactory
from ..models.mongo.mongo_langchain import MongoLangchain
from .services.langchain_service.service import LangchainService
from audit_tracker.audit_tracker import AuditTracker, ScheduleRunContext
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# mongo_connector = MongoConnector()
# mongo_client = mongo_connector.client
# mongo_langchain = MongoFactory(mongo_client, "langchain")


models_instance = UDFModels()
jwt_authentication=JWTAuthentication()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


blueprint = Blueprint('api', __name__)
api_blueprint = Blueprint('api_backend', __name__, url_prefix='/api/v1',template_folder='../templates') 


parser = reqparse.RequestParser()
parser.add_argument('param1', type=str, required=True, help='Parameter 1 description')

client = MongoConnector().client
wc_majority = WriteConcern("majority", wtimeout=1000)


rest_api = Api(
    api_blueprint, 
    version="1.0", 
    title="Ask On Data API", 
    add_specs=True,  
    doc=False,   
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Please enter the JWT token you received from the login API."
        }
    },
    security='Bearer'
)

app_env=os.getenv("APP_ENVIRONMENT", "dev")

# For custom swagger UI
@api_blueprint.route('/doc/')
def swagger_ui_template():
    """Load Swagger UI from external template"""
    return render_template('swagger-ui.html', app_env=app_env)


google_signup_model = rest_api.model('UserSignUpModel',models_instance.Google().model())
login_model = rest_api.model('UserLoginModel',models_instance.Login().model())

# Add authentication namespace 
authentication_api = Namespace('Authentication', description=' Authentication & Authorization operations including login, registration, and API key management.',path='/')
rest_api.add_namespace(authentication_api)

# Add file management namespace
file_management_api = Namespace('File Management', description=' File upload, management, and configuration operations',path='/')
rest_api.add_namespace(file_management_api)

#  Add chat management namespace
chat_conversations_api = Namespace('Chat & Conversations', description=' Chat sessions, conversation history, and context management',path='/')
rest_api.add_namespace(chat_conversations_api)

data_connections_api = Namespace('Data Connectors & Sources', description=' Database connectors, data sources, and connection management',path='/')
rest_api.add_namespace(data_connections_api)

dms_service_api = Namespace('Data Migration Service (DMS)', description='APIs related to Data Migration Service', path='/')
rest_api.add_namespace(dms_service_api)

airflow_scheduling_api = Namespace('Airflow & Scheduling', description=' Airflow scheduling, DAG management, and job automation',path='/')
rest_api.add_namespace(airflow_scheduling_api)

pipeline_workflows_api = Namespace('Pipeline Workflows', description=' Data transformation pipelines, execution, and workflow management',path='/')
rest_api.add_namespace(pipeline_workflows_api)

llm_code_generation_api = Namespace('LLM & Code Generation', description=' Ollama-powered language models for natural language processing and PySpark code generation',path='/')
rest_api.add_namespace(llm_code_generation_api)

user_management_api = Namespace('User Management', description=' User profiles, preferences, and account settings',path='/')
rest_api.add_namespace(user_management_api)

audit_billing_api = Namespace('Audit & Billing', description=' Usage analytics, billing summaries, and monitoring',path='/')
rest_api.add_namespace(audit_billing_api)

export_download_api = Namespace('Export & Download', description=' Data export, file downloads, and output management',path='/')
rest_api.add_namespace(export_download_api)

"""
   Helper function for JWT token required
"""

@authentication_api.route("/googleauth/login")
class GoogleLoginResource(Resource):

    @rest_api.expect(google_signup_model, validate=True)
    def post(self):
        """
        Authenticate user with Google OAuth profile data
        
        Processes Google user profile information to authenticate users and create or update accounts in the system.

        **Request Body (JSON):**

        ```json
        {
            "id": "123456789",
            "email": "user@gmail.com",
            "verified_email": true,
            "name": "User_a",
            "given_name": "User_a",
            "family_name": "User_b",
            "picture": "picture-123"
        }
        ```

        **Request Parameters:**
        * **id** (`str`): Google user unique identifier
        * **email** (`str`): User's verified Google email address
        * **verified_email** (`bool`): Email verification status from Google
        * **name** (`str`): User's full display name
        * **given_name** (`str`): User's first name
        * **family_name** (`str`): User's last name
        * **picture** (`str`): URL to user's Google profile picture

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "userid": "user_id_123",
            "token": "<JWT_TOKEN_PLACEHOLDER>",
            "msg": "Welcome back {name}! Getting your workspace ready."
        }
        ```

        **Returns:**
        * **success** (`bool`): Authentication success status
        * **userid** (`str`): Unique user identifier in the system
        * **token** (`str`): JWT authentication token for API access
        * **msg** (`str`): Message about account setup or login

        **Use Cases:**
        * New user registration with Google account
        * Existing user authentication via Google
        * Profile synchronization with Google data
        """
        try:

            resp = GoogleLoginService().google_login(request)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred.", "token": None}, 500



@authentication_api.route("/register")
class UserServiceRegister(Resource): # pragma: no cover
    @authentication_api.expect(rest_api.model('UserRegistrationModel', {
    "name": fields.String(example="User_name"),
    "family_name": fields.String(example="family_name"),
    "email": fields.String(example="user@gmail.com"),
    "password": fields.String(example="password"),
    "confirm": fields.String(example="password")}), validate=False)
    def post(self):
        """
        User registration
        This endpoint allows new users to register an account by providing their personal information and credentials.
        
        **Request Body (JSON):**
        
        ```json
        {
            "name": "User_123",
            "family_name": "family_name",
            "email": "user_123@gmail.com",
            "password": "password",
            "confirm": "password"
        }
        ```
        
        **Request Parameters:**
        * **name** (`str`): User's first name or given name.
        * **family_name** (`str`): User's last name or family name.
        * **email** (`str`): User's email address (must be unique and valid format).
        * **password** (`str`): User's password (must meet security requirements).
        * **confirm** (`str`): Password confirmation (must match the password field).
        
        **Response (Success ):**
        
        ```json
        {
            "success": true,
            "msg": "Registration Successful. Please login"
        }
        ```
    
        **Returns:**
        * **success** (`bool`): Indicates if the registration was successful.
        * **msg** (`str`): Descriptive message about the operation result.

        
        **Validation Requirements:**
        * Email must be in valid email format and unique in the system
        * Password and confirm fields must match exactly
        * All fields are required and cannot be empty
        """
        try:
            resp = UserServices().register(request)
            return resp

        except Exception as e: 
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred.", "token": None}, 500

@authentication_api.expect(login_model, validate=True)  
@authentication_api.route("/login")
class UserServiceLogin(Resource): # pragma: no cover

    def post(self):
        """
        Authenticate the user and return a JWT token.

        This endpoint verifies the user's credentials (email and password). If authentication is successful,
        it returns a JWT token along with user details, which can be used to authorize subsequent API requests.

        **Request Body (JSON):**
        ```json
        {
            "email": "user@example.com",
            "password": "your_password"
        }
        ```

        **Response (Success):**
        ```json
        {
            "success": true,
            "userid": "68b6d4e69349b8c6ac3e",
            "token": "<JWT_TOKEN_PLACEHOLDER>",
            "users": {
                "email": "user123@gmail.com",
                "name": "Praveen",
                "given_name": "Praveen",
                "family_name": "P",
                "picture": "",
                "locale": "",
                "external": "",
                "jwt_auth_active": false,
                "settings": {
                "files": {
                    "file_size": 5,
                    "num_records": 100
                }
                }
            },
            "msg": "Welcome back Praveen! Getting your workspace ready."
            }
        ```

        **Response Fields:**
        - **token** (`str`): JWT token to be included in the `Authorization` header as `Bearer <token>`.
        - **userid** (`str`): Unique identifier of the authenticated user.
        - **users** (`dict`): User details returned upon successful login.
        - **msg** (`str`): Message indicating success or failure of login.
        - **success** (`bool`): Indicates whether the login was successful.

        """

        try:
            resp = UserServices().login(request)
            return resp
        
        except Exception as e: 
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred.", "token": None}, 500
        

@blueprint.route("/")
@blueprint.route("/session")
@blueprint.route("/chat")
@blueprint.route("/login")
@blueprint.route("/error")
@blueprint.route("/work-space")
def index_page():# pragma: no cover
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('index.html'), 200, headers)                             


@authentication_api.route("/generate_api_key")
class APIKeyService(Resource):  

    @token_required
    @authentication_api.expect(rest_api.model('APIKeyGenerationModel', {
        "email": fields.String(example="user@gmail.com", description="User's email address",required=True),
        "token_name": fields.String(example="New_token", description="Custom name for the API key",required=True),
        "expiry_date": fields.String(example="2025-08-20", description="Expiration date in YYYY-MM-DD format",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Generate API key
        This endpoint allows authenticated users to generate a new API key for programmatic access to the OLLAMA server. The API key can be used to authenticate API requests.
        
        **Request Body (JSON):**
        
        ```json
        {
            "email": "user@gmail.com",
            "token_name": "New_token",
            "expiry_date": "2025-08-20"
        }
        ```
        
        **Request Parameters:**
        * **email** (`str`): User's email address (must match authenticated user's email).
        * **token_name** (`str`): Custom name to identify the API key .
        * **expiry_date** (`str`): Expiration date for the API key in YYYY-MM-DD format.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "api_key": "jwt_token",
            "expires_at": "2025-08-20T07:26:11.857866",
            "token_name": "New_token"
        }
        ```
        **Returns:**
        * **success** (`bool`): Indicates if the API key generation was successful.
        * **api_key** (`str`): The generated JWT API key token for authentication.
        * **expires_at** (`str`): Full timestamp when the API key will expire (ISO format).
        * **token_name** (`str`): The custom name assigned to the API key.
        
        """
        try:
            resp = UserServices().api_key_generation(request)
            return resp
        except Exception as e:
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred."}, 500

    @token_required
    @authentication_api.doc(params={'user_id': {'description': 'User ID to retrieve API key information for','type': 'string','required': True,'in': 'query','example': 'user_id_123'}})
    def get(self, current_user):
        """
        Get API key information
        This endpoint retrieves the current API key information for a specified user to interact with OLLAMA server, including the key details, expiration date, and token name.
        
        **Query Parameters:**
        * **user_id** (`str`): User ID to retrieve API key information for.
        
        **Example Request:**
        ```
        GET /generate_api_key?user_id=684aaaa4ae12
        ```
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "api_key": "JWT_token",
            "expiry_date": "2025-08-25T07:35:26.928812",
            "token_name": "New_token"
        }
        ```
    
        **Returns:**
        * **success** (`bool`): Indicates if the API key retrieval was successful.
        * **api_key** (`str` or `null`): The current active API key for the user (JWT format).
        * **expiry_date** (`str` or `null`): ISO timestamp when the API key expires.
        * **token_name** (`str` or `null`): The custom name assigned to the API key.
        
        """
        try:
            user_id = request.args.get("user_id")
            resp = UserServices().get_api_key(user_id)
            return resp
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

    @token_required
    @authentication_api.doc(params={'user_id': {'description': 'User ID to delete API key information','type': 'string','required': True,'in': 'query','example': 'user_id_123'}})
    def delete(self, current_user):
        """
        Delete/revoke API key
        This endpoint allows deletion or revocation of an existing API key for a specified user. Once deleted, the API key will no longer be valid for authentication .
        
        **Query Parameters:**
        * **user_id** (`str`): User ID whose API key should be deleted/revoked.
        
        **Example Request:**
        ```
        DELETE /generate_api_key?user_id=user_id_123
        ```
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "msg": "API key and related fields removed successfully."
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the API key deletion was successful.
        * **msg** (`str`): Descriptive message about the operation result.

        """
        try:
            user_id = request.args.get("user_id")
            if not user_id:
                return {"success": False, "msg": "User ID is required"}, 400
            resp = UserServices().delete_jwt_api_key(user_id)
            return resp

        except Exception as e:
            logger.error(f"Deletion failed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred."}, 500


@file_management_api.route('/files')
# @file_management_api.route('/files/<string:file_id>') #Not used by the FE
class FilesResource(Resource):

    @token_required
    def get(self, current_user):
        """
        Get user files list
        This endpoint allows user to retrieve a list of all files uploaded and managed by the authenticated user.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "filesList": [
                {
                    "_id": "file_id",
                    "alias": "file_name",
                    "fileType": ".xlsx"
                },
                {
                    "_id": "file_id",
                    "alias": "file_name",
                    "fileType": ".csv"
                }
            ]
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the file list retrieval was successful.
        * **filesList** (`array`): List of user's uploaded files, each containing:
          * **_id** (`str`): Unique identifier of the file (UUID format).
          * **alias** (`str`): User-friendly name or alias for the file.
          * **fileType** (`str`): File extension indicating the file format (e.g., ".xlsx", ".csv").
        
        """
        try:
            user_id = str(self['_id'])
 
            resp = FileService().get_files_list(user_id)
            return resp

        except Exception as e: # pragma: no cover
            return {"success": False,
                    "msg": f"Failed to retrieve files! {e} "}, 500

    @token_required
    @file_management_api.expect(rest_api.parser().add_argument('file', location='files', type='file',required=True,help='File to upload'))
    def post(self, current_user):
        """
        Upload file
        This endpoint allows user to upload a file to the platform. The file will be processed and made available for data analysis and manipulation.
        
        **Request (Multipart Form Data):**
        * **file** (`binary`): The file to be uploaded. Supports various formats file formats.
        
        **Supported File Types:**
        * **.csv** - Comma-separated values files
        * **.xlsx** - Excel spreadsheet files  

        
        **File Size Limits:**
        * Maximum file size: Varies based on file type and system configuration
        * Recommended: Files under 100MB for optimal performance
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "filesUploaded": {
                "_id": "ec966262-b83a-4db7-a1d8-9a40403e2c68",
                "alias": "xyz",
                "fileType": ".csv"
            },
            "message": "File uploaded successfully"
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the file upload was successful.
        * **filesUploaded** (`object`): Details of the uploaded file:
        * **_id** (`str`): Unique identifier assigned to the uploaded file.
        * **alias** (`str`): File name or alias (derived from original filename).
        * **fileType** (`str`): File extension indicating the file format.
        * **message** (`str`): Descriptive message about the operation result.
        
        **Upload Process:**
        1. File is received and validated
        2. File metadata is extracted
        3. File is stored in secure storage
        4. Database record is created with file information
        5. File is made available for data processing
        
        """
        try:
            file = request.files['file']
            user_id = str(self["_id"])
            for retry in range(5):
                try:
                    with client._Database__client.start_session() as session:
                        resp=session.with_transaction(
                            lambda s: FileService(session).upload_file(user_id, file, request.content_length/1024),
                            read_concern=ReadConcern("local"),
                            write_concern=wc_majority,
                            read_preference=ReadPreference.PRIMARY,
                        )   
                    return resp
                except OperationFailure as exc: # pragma: no cover
                    if retry == 4:
                        raise Exception("Transaction Failed :Please Retry") # If it's the last retry or not a transient error, re-raise the exception
                    logger.info(f"TransientTransactionError encountered, retrying... ({retry+1}/5)")
                    time.sleep(2 ** retry)

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": f"Failed to upload file! {e} "}, 400

    @token_required
    @file_management_api.expect(rest_api.model('FileDeleteModel', {
    "ids": fields.List(fields.String(), 
                      example=["e433a743-9b1e-40f5-ac69-83b1e26949cd"], 
                      description="Array of file IDs to be deleted",
                      required=True)
    }), validate=False)
    def delete(self,  current_user):
        """
        Delete files
        This endpoint allows user to delete one or multiple files by providing their file IDs. Supports bulk deletion of files.
        
        **Request Body (JSON):**
        
        ```json
        {
            "ids": ["file_id"]
        }
        ```
        
        **Request Parameters:**
        * **ids** (`array`): List of file IDs to be deleted. Each ID should be a valid UUID string.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "message": "File deleted successfully.",
            "failed_file_ids": []
        }
        ```

        **Bulk Deletion Features:**
        * Supports deleting multiple files in a single request
        * Returns detailed results including any failed deletions
        * Only deletes files owned by the authenticated user
        * Maintains data integrity with database transactions
        
        """
        try:
            user_id = str(self["_id"])
            file_ids = request.json["ids"]
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: FileService(session).delete_file(user_id, file_ids),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp
        
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": f"Error deleting file: {e}"}, 500

    @token_required
    @file_management_api.expect(rest_api.model('FileUpdateModel', {
        "_id": fields.String(example="file_id", description="Unique identifier of the file"),
        "alias": fields.String(example="new_alias", description="New name or alias for the file"),
        "fileType": fields.String(example=".csv", description="File extension (for context)"),
        "key": fields.String(example="file_id", description="Additional identifier key")
    }), validate=False)
    def patch(self, current_user):# pragma: no cover
        """
        Update file name/alias
        This endpoint allows user to update the name or alias of an existing file using its file ID.
        
        **Request Body (JSON):**
        
        ```json
        {
            "_id": "file_id",
            "alias": "new_alias",
            "fileType": ".csv",
            "key": "file_id"
        }
        ```
        
        **Request Parameters:**
        * **_id** (`str`): Unique identifier of the file to be updated.
        * **alias** (`str`): New name or alias for the file.
        * **fileType** (`str`, optional): File extension (included for context but not updated).
        * **key** (`str`, optional): Additional identifier key (typically same as _id).
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "message": "File name updated successfully."
        }
        ```
       
        **Returns:**
        * **success** (`bool`): Indicates if the file name update was successful.
        * **message** (`str`): Descriptive message about the operation result.
        
        **Validation Rules:**
        * File ID (_id) must be provided and exist in user's files
        * New alias cannot be empty or null
        * Only the file owner can update the file name
        * File type cannot be changed through this endpoint
        """
        try:
            user_id = str(self["_id"])
            args = request.get_json()
            file_id = args.get("_id",None)
            new_file_name = args.get("alias", None) 
            resp = FileService().update_file_name(user_id, file_id, new_file_name)
            return resp
            
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": f"Error updating file name: {e}"}, 500


@chat_conversations_api.route('/chat', methods=['GET', 'POST'])
@chat_conversations_api.route('/chat/<string:chat_id>', methods=['PATCH', 'DELETE'])
class ChatsResource(Resource):

    @chat_conversations_api.expect(rest_api.model('ChatCreateModel', {
    "chat_name": fields.String(example="Job 123"),
    "user_id": fields.String(example="user_id_1234"),
    "service_mode": fields.String(example="DMS")}), validate=False)
    @token_required
    def post(self, current_user):
        """
        Create a new chat session.

        This endpoint creates a new chat for the authenticated user using a custom chat name.

        **Request Body (JSON):**
        ```json
        {
            "chat_name": "Job 123",
            "user_id": "user_id_123456",
            "service_mode": "DTS"
        }
        ```

        **Functionality:**
        - Initializes a new chat session with the provided custom name.
        - Links the chat session to the specified authenticated user.
        - Returns a unique identifier (`chat_id`) for the newly created chat.

        **Returns:**
        - **chat_id** (`str`): Unique ID of the newly created chat.
        - **chat_name** (`str`): Name of the chat as provided by the user.
        - **success** (`bool`): Indicates whether the chat creation was successful.
        """

        try:
            req_data = request.get_json()
            chat_name = req_data.get("chat_name")
            service_mode = req_data.get("service_mode", "DTS").upper()
            user_id = str(self['_id'])
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: ChatService(session).create_chat(user_id, chat_name, service_mode),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp
            
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

    @chat_conversations_api.expect(rest_api.model('ChatUpdateModel', {"chat_name": fields.String(example="Updated Job 123")}), validate=False)
    @token_required
    def patch(self,  current_user, chat_id):
        """
        Update the name of an existing chat.

        This endpoint allows user to update the name of a specific chat session using its `chat_id`.

        **URL Parameter:**
        - **chat_id** (`str`): Unique identifier of the chat session to be updated.

        **Request Body (JSON):**
        ```json
        {
            "chat_name": "Updated Chat Name"
        }
        ```

        **Response (Success - 200):**
        ```json
        {
            "success": true,
            "user_id": "your_user_id",
            "chat_id": "chat_id_of_updated_chat",
            "chat_name": "Job 123"
        }
        ```

        **Returns:**
        - **success** (`bool`): Indicates if the update was successful.
        - **user_id** (`str`): ID of the user who owns the chat session.
        - **chat_id** (`str`): ID of the updated chat session.
        - **chat_name** (`str`): The new name of the chat session.
        """

        try:
            req_data = request.get_json()
            chat_name = req_data.get("chat_name")
            user_id = str(self['_id']) 
            resp = ChatService().update_chat(user_id, chat_id, chat_name)
            return resp
            

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

    @token_required
    def delete(self,current_user, chat_id):
        """
        Delete a chat session.

        Permanently deletes a chat session and all associated messages for the specified chat ID.

        **URL Parameter:**
        - **chat_id** (`str`): Unique identifier of the chat session to be deleted.

        **Response (Success):**
        ```json
        {
            "success": true,
            "msg": "Chat deleted successfully.",
            "chat_id": "chat_id_123"
        }
        ```

        **Returns:**
        - **success** (`bool`): Indicates whether the deletion was successful.
        - **msg** (`str`): Status message confirming the deletion.
        - **chat_id** (`str`): ID of the deleted chat session.
        """
        try:
            user_id = str(self["_id"])
            with client._Database__client.start_session() as session:
                
                resp=session.with_transaction(
                    lambda s: ChatService(session).delete_chat(user_id, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp
            

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

    @chat_conversations_api.doc(params={
        'service_mode': {'description': 'Filter chats by service mode (default: dts)', 'type': 'string', 'in': 'query'}
    })
    @token_required
    def get(self, current_user):
        """
        Retrieve all chat sessions for the user.

        This endpoint returns a list of all chat sessions associated with the currently authenticated user.
        You can optionally pass a query parameter "service_mode" (default value of this parameter will be "dts").
        If "service_mode" is passed as "dms", we query the chat documents which have the key "service_mode": "dms" and return the result.
        If "service_mode" is passed as "dts", we ignore all chats that have "service_mode": "dms" and return the result.

        **Query Parameters:**
        * **service_mode** (`str`, optional): Allows filtering by service mode. Can be "dms" or "dts". Default is "dts".

        **Response Example (Success):**
        ```json
        {
            "success": true,
            "chats": [
                {
                    "chat_id": "chat_12345",
                    "chat_name": "Job 1"
                },
                {
                    "chat_id": "chat_67890",
                    "chat_name": "Job 2"
                }
            ],
            "msg": "Chats retrieved successfully."
        }
        ```

        **Response Fields:**
        - **chat_id** (`str`): Unique identifier for each chat session.
        - **chat_name** (`str`): Name of the chat.
        - **success** (`bool`): Indicates whether the retrieval was successful.
        - **msg** (`str`): A message describing the result of the operation.
        - **chats** (`list`): List of chat sessions associated with the user.
        """

        try:
            user_id = str(self["_id"])
            service_mode = request.args.get('service_mode', 'dts')

            if service_mode.lower() == 'dms':
                resp = ChatService().get_chats(user_id, filter_fields={"service_mode": "DMS"})
            else:
                resp = ChatService().get_chats(user_id, ignore_fields={"service_mode": "DMS"})
            return resp

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

@chat_conversations_api.route('/get_data/<string:chat_id>')
class ChatsDataResource(Resource):
    @chat_conversations_api.expect(rest_api.model('GetDataModel', {
    "value": fields.String(example="print(\"Hello\")"),
    "mode": fields.String(example="python")}), validate=False)
    @token_required
    def post(self, current_user, chat_id):
        """
        Create or update chat data
        This endpoint allows user to create or update data associated with a specific chat session using its `chat_id`.
        
        **Path Parameter:**
        **chat_id** (`str`): Unique identifier of the chat session to create or update data for.
        
        **Request Body (JSON):**
        
        ```json
        {
            "value": "print("Hello")",
            "mode": "python"
        }
        ```
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "chat_id": "chat_id_123",
            "message": "Updated chat data"
        }

        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the data creation/update was successful.
        * **chat_id** (`object`):  Unique identifier of the updated chat data session.
        * **message** (`str`): Descriptive message about the operation result.
        """
        try:
            req_data = request.get_json()
            resp = ChatService().create_or_update_data(chat_id, req_data)
            return resp
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500
    
    @token_required
    def get(self, current_user, chat_id):
        """
        Get chat data
        This endpoint allows user to retrieve data associated with a specific chat session using its `chat_id`.
        
        **Path Parameter:**
        * **chat_id** (`str`): Unique identifier of the chat session to retrieve data for.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "chats": {
                "code": "",
                "history": ""
            },
            "msg": "Chat data retrieved Successfully."
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the data retrieval was successful.
        * **chats** (`object`): Contains the chat data with:
        * **code** (`str`): Code snippet or script associated with the chat session.
        * **history** (`str`): Conversation history or context information.
        * **msg** (`str`): Descriptive message about the operation result.
        """
        try:
            resp = ChatService().get_data(chat_id)
            return resp
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500
        
@chat_conversations_api.route('/get_information')
class ChatsInformation(Resource):
    @token_required
    @rest_api.doc(params={
        'chat_id': {'description': 'Unique identifier of the chat session','type': 'string','required': True,'in': 'query'}
    })
    def get(self, current_user):
        """
        Get chat conversation information
        This endpoint allows user to retrieve detailed information about a specific chat session using its `chat_id`.
        
        **URL Parameter:**
        * **chat_id** (`str`): Unique identifier of the chat session to retrieve information for.

        **Returns:**
        * **success** (`bool`): Indicates if the information retrieval was successful.
        * **chats** (`object`): Contains the chat session information with the following properties:
          * **cwf** (`null` or `object`): Current workflow file information.
          * **loaded_files** (`array`): List of files loaded in the chat session.
          * **metadata** (`array`): Additional metadata associated with the chat session.
          * **configurations** (`object`): Configuration settings for the chat session.
          * **job_mode** (`str`): The mode of operation for the chat (e.g., "llm").
        * **msg** (`str`): Descriptive message about the operation result.
        """
        try:
            chat_id = request.args.get("chat_id")  
            resp = ChatService().get_information(chat_id)
            return resp

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

@chat_conversations_api.route('/update_mode/<string:chat_id>')
class UpdateJobMode(Resource):
    @token_required
    @chat_conversations_api.expect(rest_api.model('UpdateJobModeModel', {"job_mode": fields.String(example="llm")}), validate=False)
    def patch(self, current_user, chat_id):
        """
            Update chat job mode
            This endpoint allows user to change the job mode for a specific chat session. The job mode determines how the chat processes and executes user requests.
            
            **Path Parameter:**
            * **chat_id** (`str`): Unique identifier of the chat session to update the job mode for.
            
            **Request Body (JSON):**
            
            ```json
            {
                "job_mode": "llm"
            }
            ```
            
            **Available Job Modes:**
            * **llm**: Natural language processing mode using large language models
            * **yaml**: Declarative data transformation mode using YAML configuration
            * **python**: Custom scripting mode using Python code
            
            **Cache Behavior:**
            * **Switching from "llm" to "yaml"/"python"**: Chat cache is invalidated to ensure clean state
            * **Switching back to "llm" mode**: Cache needs to be reconstructed for optimal performance
            ---
            ### Sample Responses

            **Success – 204 No Content**
            - Body: _empty_ (mode changed successfully)

            **Invalid Mode – 404**
            ```json
            {
            "success": false,
            "message": "mode not valid"
            }
            ```

            **Invalid Chat ID – 404**
            ```json
            {
            "success": false,
            "message": "Invalid chat id <chat_id>"
            }
            ```

            **Server Error – 500**
            ```json
            {
            "success": false,
            "message": "Failed to update job mode"
            }
            ```
        """
        try:
            job_mode = request.get_json().get("job_mode")
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s:ChatService(session).update_mode(chat_id, job_mode),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )
            return resp
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

@file_management_api.route('/upload_config')
class UploadConfig(Resource):

    @token_required
    @file_management_api.doc(params={
        'file': {'description': 'Google Sheets service account credentials file in JSON format','type': 'file','in': 'formData','required': True},
        'db_name': {'description': 'google_sheets','type': 'string', 'in': 'formData','required': True}
    })

    def post(self, current_user):
        """
        Upload Google Sheets service account credentials
        
        This endpoint allows users to upload Google Sheets service account credentials for establishing secure connections between the application and Google Sheets. The uploaded credentials enable seamless data exchange and interaction with Google Sheets.

        **Purpose:**
        The Google Sheets connector facilitates seamless interaction and data exchange between your application and Google Sheets by using service account credentials for authentication.

        **Form Parameters:**
        * **file** (`file`): Google Sheets service account credentials file in JSON format
        * **db_name** (`str`): Service identifier - use "google_sheets" for Google Sheets credentials

        **Example Request:**
        ```
        POST /upload_config
        Content-Type: multipart/form-data

        file: [credentials.json] (binary data)
        db_name: google_sheets
        ```

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "user_id": "user_id_123",
            "details": {
                "file": "hadoop_local/upload/user_id_123/configurations/google_sheets/credentials.json"
            }
        }
        ```
        **Use Cases:**
        * **Data Import**: Read data from Google Sheets into data pipelines
        * **Data Export**: Write processed data back to Google Sheets
        * **Real-time Sync**: Synchronize application data with Google Sheets

        """
        try:
            db_name = request.form.get("db_name")
            file = request.files['file']
            user_id = str(self["_id"])
            resp = UploadConfigService().upload_config(file,db_name,user_id) 
            return resp
        except Exception as e: # pragma: no cover
            logger.error(str(e), exc_info=True)
            return {
                "success": False,
                "msg": "Unable to Upload."
            },500


@chat_conversations_api.route('/chat_history/<string:chat_id>')
class ChatHistoryResource(Resource):
    @token_required
    def get(self,current_user, chat_id):
        """
        Get chat conversation history
        This endpoint allows user to retrieve the conversation history of a specific chat session using its `chat_id` with pagination support.
        
        **Path Parameter:**
        * **chat_id** (`str`): Unique identifier of the chat session to retrieve history for.
        
        **Query Parameters:**
        * **offset** (`int`, optional): Number of messages to skip for pagination. Default is 0.
        * **limit** (`int`, optional): Maximum number of messages to return. Default is 10.
        
        **Returns:**
        * **chat_history** (`array`): List of conversation messages in chronological order, each containing:
          * **isUser** (`bool`): Indicates if the message is from user (true) or assistant (false).
          * **text** (`str`): The actual message content or response text.
          * **timestamp** (`float`): Unix timestamp when the message was created.
          * **message_id** (`str`): Unique identifier for the individual message.
        * **has_more** (`bool`): Indicates if there are more messages available beyond the current page for pagination.
        """
        try:
            user_id = str(self["_id"])
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 10))
            
            resp = ChatHistoryService().get_chat_history(user_id, chat_id, offset, limit)
            return resp

        except Exception as e: # pragma: no cover
            return {
                'chat_history': [],
                'has_more': False,
            }, 500

    @token_required
    def delete(self, current_user, chat_id):
        """
        Delete chat conversation history
        This endpoint allows user to permanently delete the entire conversation history of a specific chat session using its `chat_id`.
        
        **Path Parameter:**
        * **chat_id** (`str`): Unique identifier of the chat session to delete history for.
        
        **Response (Success - 200):**
        
        ```json
        {
            "status": true,
            "chat_history": [],
            "has_more": false,
            "selected_files": [],
            "loaded_files": [],
            "columns": [],
            "metadata": {},
            "message": "Chat history deleted successfully"
        }
        ```
        
        **Response (Error - 500):**
        
        ```json
        {
            "status": false,
            "message": "Failed to delete chat history"
        }
        ```
        
        **Returns:**
        * **status** (`bool`): Indicates if the deletion was successful.
        * **chat_history** (`array`): Empty array after successful deletion.
        * **has_more** (`bool`): Always false after deletion as no messages remain.
        * **selected_files** (`array`): List of currently selected files in the chat session.
        * **loaded_files** (`array`): List of files that were loaded in the chat session.
        * **columns** (`array`): Data columns information associated with the chat session.
        * **metadata** (`object`): Additional metadata related to the chat session.
        * **message** (`str`): Descriptive message about the operation result.
        """
        try:
            user_id = str(self["_id"])
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: ChatHistoryService(session).delete_chat_history(user_id, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp

        except Exception as e: # pragma: no cover
            return {"status": False, "message": "Failed to delete chat history"}, 500


@pipeline_workflows_api.route('/pipeline_history')
# @pipeline_workflows_api.route('/pipeline_history/<string:chat_id>') # Not using in FE chat_id is passing as query params only
class PipelineHistoryResource(Resource):
    @token_required
    @rest_api.doc(params={
        'chat_id': {
            'description': 'Unique identifier of the chat session to retrieve pipeline history for',
            'type': 'string',
            'required': False,
            'in': 'query',
            'example': '64a7b8c9d1e2f3a4b5c6d7e8'
        }
    })
    def get(self, current_user):
        """
        Get pipeline execution history
        This endpoint retrieves the pipeline execution history for a specific chat session, including all data transformation steps, file operations, and available connections.
        
        **Query Parameters:**
        * **chat_id** (`str`, optional): Unique identifier of the chat session to retrieve pipeline history for.
        
        **Sample Response (Success ):**
        
        ```json
        {
            "success": true,
            "history": [
                {
                    "function": "read_files",
                    "parameters": [
                        {
                            "alias": "xyz",
                            "_id": "xyz_id"
                        }
                    ],
                    "files": null,
                    "database_alias": "flat_files"
                },
                {
                    "function": "delete_files",
                    "parameters": [
                        {
                            "source_id": "14f9a81a-a83e-48a6-b0e1-279e42ba43d6"
                        }
                    ],
                    "files": []
                }
            ],
            "next": [],
            "connections": [
                {
                    "_id": "connection_id_123",
                    "alias": "Dev Test DB",
                    "type": "postgres"
                },
                {
                    "_id": "connection_id_xyz",
                    "alias": "xyz",
                    "type": "file"
                }
            ]
        }
        ```
        **Returns:**
        * **success** (`bool`): Indicates if the pipeline history retrieval was successful.
        * **history** (`array`): List of executed pipeline operations in order.
          * **function** (`str`): Name of the executed function (e.g., "read_files", "delete_files", "filter_value").
          * **parameters** (`array`): Parameters used for the function execution.
          * **files** (`array` or `null`): Files affected by the operation.
          * **database_alias** (`str`, optional): Database alias used for the operation.
        * **next** (`array`): Suggested next operations or recommendations for the pipeline.
        * **connections** (`array`): Available data connections and files for the user:
          * **_id** (`str`): Unique identifier of the connection or file.
          * **alias** (`str`): User-friendly name for the connection or file.
          * **type** (`str`): Type of connection ("postgres", "mysql", "file", etc.).
        
        **Pipeline Operations Tracked:**
        * **Data Loading**: read_files, read_tables, read (S3)
        * **Data Cleaning**: delete_files, drop_columns, fill_na, deduplicate
        * **Data Transformation**: filter_value, sort, aggregate, joins, concat
        * **Data Export**: export operations and file outputs
    
        """
        try:
            user_id = str(self["_id"])
            chat_id = request.args.get("chat_id")
            if not chat_id:
                return {"success": True, "history": [], "next": []}
  
            resp = PipelineHistoryService().get_pipeline_history(chat_id)
            if resp[0]["success"] is True:
                connection_details = DataConnectorsService().get_all_data_connectors(user_id)
                file_details = FileService().get_files_list(user_id)
                connections = []
                connections.extend(
                    [
                        {
                            "_id": str(connector["_id"]), 
                            "alias": connector.get("connection_alias", "na"), 
                            "type": connector.get("type", "na")
                        } for connector in connection_details[0]["data_connectors"]
                    ]
                )
                connections.extend(
                    [
                        {
                            "_id": str(file["_id"]), 
                            "alias": file.get("alias", "na"), 
                            "type": "file"
                        } for file in file_details[0]["filesList"]
                    ]
                )
                resp[0]["connections"] = connections

            return resp

        except ValueError as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 400
        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "Internal server error"}, 500

@pipeline_workflows_api.route('/undo')
class UndoTransformationsResource(Resource):
   @token_required
   @pipeline_workflows_api.expect(rest_api.model('UndoModel', {
        "chat_id": fields.String(example="689b2f73d9b5775e6b7f707c", description="Chat session ID to undo the last transformation in",required=True)
    }), validate=False)
   def post(self,current_user):
       """
        Undo last transformation
        This endpoint reverts the most recent data transformation operation performed in a specific chat session, restoring the dataset to its previous state.
        
        **Request Body (JSON):**
        
        ```json
        {
            "chat_id": "chat_id_123"
        }
        ```
        
        **Request Parameters:**
        * **chat_id** (`str`): Chat session ID where the undo operation should be performed.
        
        **Response (Success - 200):**
        
        ```json
        {
            "msg": "Undo Successful",
            "success": true
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the undo operation was successful.
        * **msg** (`str`): Descriptive message about the operation result.
        
        **Undo Functionality:**
        * **Last Operation**: Reverts only the most recent transformation
        * **State Restoration**: Restores dataset to the previous valid state
        * **Pipeline History**: Updates the transformation history accordingly
        * **Data Integrity**: Ensures data consistency after undo operation

        **Use Cases:**
        * Revert accidental data transformations
        * Backtrack from incorrect filter operations
        * Undo unwanted column modifications
        * Restore data after failed transformation attempts
        * Experiment with different transformation approaches
    
        """
       try:
            user_id = str(self["_id"])
            chat_id = request.json.get("chat_id")
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: UndoRedoService(session).undo(user_id, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp

       except ValueError as e:# pragma: no cover
           return {"success": False, "msg": str(e)}, 400
       except Exception as e: # pragma: no cover
           logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
           return {"success": False, "msg": "Internal server error"}, 500
       

@pipeline_workflows_api.route('/redo')
class RedoTransformationsResource(Resource):
   @token_required
   @pipeline_workflows_api.expect(rest_api.model('RedoTransformationModel', {
        "chat_id": fields.String(example="689b2f73d9b5775e6b7f707c", description="Chat session ID to redo the last transformation in",required=True)
    }), validate=False)
   def post(self,current_user):
       """
        Redo last undone transformation

        This endpoint reapplies the most recently undone data transformation operation in a specific chat session, moving forward in the transformation history.

        ### Request Body (JSON):

        ```json
        {
            "chat_id": "chat_id_123"
        }
        ```

        ### Request Parameters:
        * **chat_id** (`str`): Chat session ID where the redo operation should be performed.

        ### Response (Success - 200):

        ```json
        {
            "msg": "Redo Successful",
            "success": true
        }
        ```

        ### Returns:
        * **success** (`bool`): Indicates if the redo operation was successful.
        * **msg** (`str`): Descriptive message about the operation result.

        ### Use Cases:
        * Reapply accidentally undone transformations
        * Navigate forward through transformation history
        * Test different transformation sequences
        * Restore workflow after exploring alternatives
        """
       try:
           user_id = str(self["_id"])
           chat_id = request.json.get("chat_id")
           with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: UndoRedoService(session).redo(user_id, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
           return resp

       except ValueError as e: # pragma: no cover
           return {"success": False, "msg": str(e)}, 400
       except Exception as e: # pragma: no cover
           logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
           return {"success": False, "msg": "Internal server error"}, 500

@dms_service_api.route('/dms/progress')
class DMSProgress(Resource):
    @token_required
    @dms_service_api.expect(rest_api.model('DMSProgressModel', {
        "dms_migration_mode": fields.String(example="custom-sql", description="The migration mode selected for the DMS", required=False),
        "chat_id": fields.String(example="chat_id_123", description="The chat ID", required=False),
        "source_details": fields.Raw(example={"type": "postgres", "connection_id": "conn_123"}, description="Details for selected DMS source", required=False),
        "destination_details": fields.Raw(example={"type": "mysql", "connection_id": "conn_456", "schema": "public"}, description="Details for selected DMS destination", required=False)
    }), validate=False)
    def post(self, current_user):
        """
        Update DMS progress
        This endpoint verifies the specified chat, checks its service_mode, and attaches payload keys (dms_migration_mode, source_details, destination_details) to the chat document.
        """
        try:
            req_data = request.get_json()
            user_id = str(self['_id'])
            chat_id = req_data.get("chat_id")
            
            with client._Database__client.start_session() as session:
                resp = session.with_transaction(
                    lambda s: ChatService(session).update_dms_progress(user_id, chat_id, req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "Internal server error"}, 500

    @token_required
    @dms_service_api.doc(params={'chat_id': {'description': 'The chat ID to retrieve DMS progress for', 'type': 'string', 'required': True, 'in': 'query'}})
    def get(self, current_user):
        """
        Get DMS progress
        This endpoint verifies the specified chat, checks its service_mode, and returns the DMS specific payload config keys.
        """
        try:
            user_id = str(self['_id'])
            chat_id = request.args.get("chat_id")
            
            with client._Database__client.start_session() as session:
                resp = session.with_transaction(
                    lambda s: ChatService(session).get_dms_progress(user_id, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )
            return resp

        except ValueError as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 400
        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "Internal server error"}, 500


@data_connections_api.route('/datasources')
class DatasourcesResource(Resource):
    @token_required
    def get(self,current_user):
        """
        Get available data sources
        This endpoint retrieves all available data source connectors that can be used to establish connections to various databases, cloud services, and data storage systems.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "configuration": {
                "datasources": []
            },
            "msg": "Datasources fetched successfully."
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the datasources retrieval was successful.
        * **configuration** (`object`): Contains datasources configuration with:
          * **datasources** (`array`): List of available data source connectors, each containing:
            * **driver** (`str`): Unique identifier for the datasource driver.
            * **name** (`str`): Human-readable name of the datasource.
            * **verified** (`bool`): Indicates if the connector has been verified and tested.
            * **categoryName** (`str`): Category classification (e.g., "RDBMS", "Big Data", "Cloud").
            * **categoryType** (`str`): Type classification (e.g., "sql", "nosql", "Cloud").
            * **available** (`bool`): Indicates if the datasource is currently available for use.
            * **pooling** (`bool`, optional): Whether connection pooling is supported.
            * **spark** (`str/array`, optional): Spark connector dependencies required.
            * **connection_string** (`object`, optional): Template for connection string parameters.
            * **description** (`str`, optional): Detailed documentation for the connector.
            * **parameters** (`object`, optional): Configuration parameters required for connection.
        * **msg** (`str`): Descriptive message about the operation result.

        """
        try:
  
            resp = DatasourcesService().get_datasources()
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "configuration": None, "msg": "Error fetching datasources."}, 500

@chat_conversations_api.route('/get_application')
class ApplicationConfigResource(Resource):
    @token_required
    def get(self, current_user):
        """
        Get application configuration
        This endpoint allows user to retrieve comprehensive application configuration including user permissions, available data sources, editor configurations, and job help information.
        
        **Sample Response (Success):**
        
        ```json
        {
            "success": true,
            "configuration": {
                "role": "admin",
                "chat": [],
                "job": [],
                "datasources": []
            },
            "editor_configuration": {
                "yaml": []
            },
            "job_help_info": {
                "yaml": "Comprehensive YAML function documentation...",
                "python": "Comprehensive Python class documentation..."
            },
            "version": "0.0",
            "msg": "Application Configurations and editor Configurations Fetched Successfully!"
        }
        ```

        
        **Returns:**
        * **success** (`bool`): Indicates if the configuration retrieval was successful.
        * **configuration** (`object`): User-specific configuration containing:
          * **role** (`str`): User's role level (e.g., "admin").
          * **chat** (`array`): Available chat functionalities and permissions.
          * **job** (`array`): Available job management operations.
          * **datasources** (`array`): List of supported data source types.
        * **editor_configuration** (`object`): Code editor autocomplete and IntelliSense configuration:
          * **yaml** (`array`): YAML function definitions with documentation and snippets.
          * **python** (`array`): Python class definitions with methods and documentation.
        * **job_help_info** (`object`): Detailed help documentation:
          * **yaml** (`str`): Complete YAML function documentation with examples.
          * **python** (`str`): Complete Python class and method documentation.
        * **version** (`str`): Application configuration version.
        * **msg** (`str`): Descriptive message about the operation result.
        """
        try:
            user_id = str(self["_id"]) 
            resp = ApplicationService().get_appservice(user_id)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "configuration": None, "msg": "Error fetching datasources."}, 500

@data_connections_api.route('/Saved_connections')
# @data_connections_api.route('/Saved_connections/<string:type>') # not used by FE
class SavedConnectionsResource(Resource):
    @token_required
    @rest_api.doc(params={
        'type': {
            'description': 'Filter connections by database type (postgres, mysql, snowflake, etc.)',
            'type': 'string',
            'required': False,
            'in': 'query',
            'enum': ['postgres', 'mysql', 'snowflake', 'redshift', 'oracle', 'ms_sql_server', 'cassandra', 'astra', 'couchbase', 's3', 'google_sheets'],
            'example': 'postgres'
        }
    })
    def get(self, current_user):
        """
        Get saved database connections
        This endpoint retrieves all saved database connections for the authenticated user, optionally filtered by connection type.
        
        **Query Parameters:**
        * **type** (`str`, optional): Filter connections by database type. Available types include postgres, mysql, snowflake, redshift, oracle, ms_sql_server, cassandra, astra, couchdb, couchbase, s3, google_sheets.
        
        **Example Request:**
        ```
        GET /Saved_connections?type=postgres
        ```
        
        **Sample Response (Success ):**
        
        ```json
        {
            "success": true,
            "databases": [
                {
                    "_id": "684aad3e20ef26522ff885f7",
                    "alias": "Dev Test DB",
                    "type": "postgres"
                },
                {
                    "_id": "684aad3e20ef26522ff885f8",
                    "alias": "Production DB",
                    "type": "postgres"
                }
            ],
            "msg": "Fetched connections successfully."
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the connections retrieval was successful.
        * **databases** (`array`): List of saved database connections:
          * **_id** (`str`): Unique identifier of the database connection.
          * **alias** (`str`): User-friendly name assigned to the connection.
          * **type** (`str`): Database type/driver (e.g., "postgres", "mysql", "snowflake").
        * **msg** (`str`): Descriptive message about the operation result.
        
        **Supported Connection Types:**
        * **RDBMS**: postgres, mysql, oracle, ms_sql_server
        * **Data Warehouses**: snowflake, redshift
        * **NoSQL**: cassandra, astra, couchbase
        * **Cloud Storage**: s3, google_sheets
        
        **Use Cases:**
        * List all available database connections for data analysis
        * Filter connections by specific database type
        * Get connection details for pipeline configuration
        * Manage and organize multiple database connections
        * Select appropriate connection for data operations
        """

        try:
            user_id = str(self["_id"])
            type=request.args.get("type")
 
            resp = SavedConnectionsService().get_saved_connections(user_id,type)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "databases": None, "msg": "Error fetching connections."}, 500

@user_management_api.route('/user_preferences')
class UserPreferenceResource(Resource):
    @token_required
    def get(self, current_user):
        """
        Get user preferences
        This endpoint retrieves the user's personal preferences and settings for file handling, data processing, and application behavior.
        
        **Response (Success - 200):**
        
        ```json
        {
            "files": {
                "file_size": 5,
                "num_records": 100
            }
        }
        ```
        
        **Returns:**
        * **files** (`object`): File-related preferences and limits:
        * **file_size** (`int`): Maximum file size limit in MB for uploads.
        * **num_records** (`int`): Maximum number of records to display in data previews.
        
        
        **Use Cases:**
        * Configure file upload and processing limits
        * Set data preview and display preferences
        * Customize application behavior based on user needs
        * Enforce resource usage limits for performance optimization
        * Personalize user experience settings
        
        **Default Values:**
        * **file_size**: 5 MB (typical default for file uploads)
        * **num_records**: 100 (default number of records shown in previews)
        """
        try:
            user_id = str(self["_id"])
            resp = SettingsService().get_settings(user_id)
            return resp, 200
 

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "Error fetching settings."}, 500
    
    @token_required
    @user_management_api.expect(rest_api.model('UserPreferencesModel', {
    "files": fields.Raw(example={
        "file_size": 10,
        "num_records": 100
    }, description="File-related preferences including size limits and record display settings")
    }), validate=False)
    def post(self, current_user):
        """
        Create or update user preferences
        This endpoint allows user to create or update their personal preferences and settings for file handling, data processing, and application behavior.
        
        **Request Body (JSON):**
        
        ```json
        {
            "files": {
                "file_size": 10,
                "num_records": 100
            }
        }
        ```
        
        **Request Parameters:**
        * **files** (object): File-related preferences:
        * **file_size** (number, **int | float**): Maximum file size limit in MB for uploads
            (e.g., 5, 10, 25, 10.5).  
            _Note: This can be an integer or a floating-point value._
        * **num_records** (`int`): Maximum number of records to display in data previews
            (e.g., 50, 100, 500).
        
        **Response (Success - 201):**
        
        ```json
        {
            "files": {
                "file_size": 10,
                "num_records": 100
            }
        }

        ```
        
        **Returns:**
        * **files** (`object`): File-related preferences:
        * **file_size** (**int | float**): Maximum file size limit in MB for uploads (e.g., 5, 10.5, 25).
        * **num_records** (**int**): Maximum number of records to display in data previews (e.g., 50, 100, 500).
        """
        try:
            user_id = str(self["_id"])
            req_data = request.json 
            resp = SettingsService().create_settings(user_id, req_data)
            return resp, 201

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": f"Error saving settings: {e}"}, 500


@data_connections_api.route('/Data_connectors')
class DataConnectorsResource(Resource):
    @token_required
    @data_connections_api.expect(rest_api.model('DataConnectorCreateModel', {
        "connection_alias": fields.String(example="Dev Test DB", description="Display name for the data connection", required=True),
        "type": fields.String(example="postgres", description="Data source type (postgres, mysql, oracle, snowflake, s3, etc.)", required=True),
        "connection_details": fields.Raw(example={
            "sourceName": "Dev Test DB",
            "host": "localhost",
            "port": "0000",
            "username": "dbusername",
            "password": "dbpassword",
            "database": "test",
            "connection_pool": {
                "spark_pooling": {},
                "pandas_pooling": {}
            }
        }, description="Connection configuration details (varies by data source type)", required=True)
    }), validate=False)
    def post(self,current_user):
        """
        Create new data connector
        
        This endpoint creates a new data connection configuration for various data sources. The payload structure varies based on the selected data source type.

        **Request Parameters (Common):**
        * **connection_alias** (`str`): Display name for the data connection
        * **type** (`str`): Data source type identifier
        * **connection_details** (`object`): Source-specific configuration (structure varies by type)

        **PostgreSQL/MySQL/SQL Server Example:**

        ```json
        {
            "connection_alias": "postgres_test_db",
            "type": "postgres",
            "connection_details": {
                "sourceName": "postgres_test_db",
                "host": "162.32.285.40",
                "port": "5433",
                "username": "abc",
                "password": "xyz",
                "database": "test",
                "connection_pool": {
                "spark_pooling": {},
                "pandas_pooling": {}
                }
            }
            }
        ```
        ### Parameter Details

        **Top-level fields**
        - `connection_alias` *(string, required)*: Human-friendly name for the connector shown in the UI.
        - `type` *(string, required)*: One of postgres | mysql | mssql | oracle | snowflake | redshift | s3 | mongodb | databricks | bigquery | ....
        - `connection_details` *(object, required)*: Source-specific configuration. See per-type requirements below.

        **Common `connection_details` fields (may not apply to all types)**
        - `sourceName` *(string, required)*: Logical name of this source (often same as `connection_alias`).
        - `host` *(string, required for DB types)*: Hostname or IP of the database.
        - `port` *(string, required for DB types)*: Service port (e.g., `"5432"`, `"3306"`).
        - `username` *(string, required for DB types)*.
        - `password` *(string, required for DB types)*.
        - `database` *(string, required for many DB types)*: Default DB/schema/catalog depending on engine.
        - `ssl` *(boolean, optional)*: Enable TLS if supported by the source.
        - `extra_params` *(object, optional)*: Driver-specific flags (key/value).
        - `connection_pool` *(object, optional)*:
          - `spark_pooling` *(object)*: Spark connector pooling settings.
          - `pandas_pooling` *(object)*: Pandas/SQLAlchemy pooling settings.

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "connection_id": "connection_id_123",
            "message": "Connection saved successfully."
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the connection creation was successful
        * **connection_id** (`str`): Unique identifier assigned to the new connection
        * **message** (`str`): Status message about the operation

        **Use Cases:**
        * **Database Integration**: Connect to various database systems for data access
        * **Cloud Data Access**: Access data stored in cloud storage services
        * **File System Access**: Connect to remote file systems and data repositories
        """
        try:
            req_data = request.get_json()
            user_id = str(self["_id"])  
            resp = DataConnectorsService().create_data_connector(req_data, user_id)
            return resp


        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "message": "Error saving data connector.", "connection_id": None}, 500

    @token_required
    @data_connections_api.doc(params={
        'connection_id': {'description': 'Unique identifier of the data connection to retrieve','type': 'string','required': True,'in': 'query','example': '684aad3e20ef26522ff885f7'}
    })
    def get(self,current_user):
        """
        Retrieve data connector details
        
        This endpoint fetches complete configuration details for a specific data connection using its unique identifier.

        **Query Parameters:**
        * **connection_id** (`str`): Unique identifier of the data connection

        **Example Request:**
        ```
        GET /Data_connectors?connection_id=684aad3e20ef26522ff885f7
        ```

        **Sample Response (Success – 200):**
        ```json
        {
        "success": true,
        "connection_data": {
            "connection_id": "68bec9a6aeab8bac1c175a",
            "connection_details": {
            "sourceName": "Dev Test DB",
            "host": "161.82.285.48",
            "port": "5432",
            "username": "xyz",
            "password": "abc",
            "database": "test",
            "connection_pool": {
                "spark_pooling": {},
                "pandas_pooling": {}
            }
            }
        },
        "msg": "Connection details fetched successfully."
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the retrieval was successful
        * **connection_data** (`object`): Complete connection configuration including:
        * **connection_id** (`str`): Unique connection identifier
        * **connection_details** (`object`): All connection parameters and settings
        * **msg** (`str`): Status message about the operation
        * **connection_pool**: Engine-specific connection pool settings
        * **Authentication**: Username/password or OAuth credentials

        **Use Cases:**
        * Retrieve connection settings for data pipeline configuration
        * Validate connection parameters before use
        * Edit or update existing connection configurations
        * Troubleshoot connection issues
        """
        try:
            connection_id=request.args.get("connection_id")
            resp = DataConnectorsService().get_data_connector(connection_id)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "connection_data": None, "msg": "Error fetching connection details."}, 500

    @token_required
    @data_connections_api.expect(rest_api.model('DataConnectorUpdateModel', {
    "connection_alias": fields.String(example="Dev Test DB postgres", description="Updated alias name for the connection", required=True),
    "type": fields.String(example="postgres", description="Data source type (postgres, mysql, oracle, snowflake, s3, google_sheets, etc.)", required=True),
    "connection_details": fields.Raw(example={}, description="Connection configuration details (varies by data source type)", required=True),
    "connection_id": fields.String(example="connection_id_123", description="Unique identifier of the connection to update", required=True)}), validate=False)
    def patch(self,current_user): # pragma: no cover
        """
        Update existing data connector
        
        This endpoint updates the configuration of an existing data connection. The payload structure varies based on the selected data source type.

        **Request Parameters (Common):**
        * **connection_alias** (`str`): Updated display name for the connection
        * **type** (`str`): Data source type identifier
        * **connection_details** (`object`): Source-specific configuration (structure varies by type)
        * **connection_id** (`str`): Unique identifier of the connection to update

        **Request Example:**

        ```json
        {
            "connection_alias": "Dev Test DB postgres",
            "type": "postgres",
            "connection_details": {
                "sourceName": "Test DB postgres",
                "host": "localhost",
                "port": "0000",
                "username": "dbusername",
                "password": "dbpassword",
                "database": "test",
                "connection_pool": {
                    "spark_pooling": {},
                    "pandas_pooling": {}
                }
            },
            "connection_id": "connection_id_123"
        }
        ```

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "updated_data": {.......},
            "msg": "Connection details updated successfully."
        }
        ```
        """
        try:
            req_data = request.get_json()
            resp = DataConnectorsService().update_data_connector(req_data)
            return resp

        except Exception as e: 
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "connection_id": None, "updated_data": None, "msg": "Error updating connection details."}, 500

    @token_required
    @data_connections_api.expect(rest_api.model('DataConnectorDeleteModel', {
    "_id": fields.String(example="connection_id_123", description="Unique identifier of the connection to delete", required=True)}), validate=False)
    def delete(self, current_user):
        """
        Delete data connector
        
        This endpoint permanently removes a data connection configuration from the system. Once deleted, the connection cannot be used for data operations and cannot be recovered.

        **Request Body (JSON):**

        ```json
        {
            "_id": "connection_id_123"
        }
        ```

        **Request Parameters:**
        * **_id** (`str`): Unique identifier of the connection to delete

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "msg": "Connection deleted successfully.",
            "connection_id": "connection_id_123"
        }
        ```


        **Returns:**
        * **success** (`bool`): Indicates if the deletion was successful
        * **msg** (`str`): Status message about the deletion operation
        * **connection_id** (`str`): ID of the deleted connection (for confirmation)

        """
        try:
            req_data = request.get_json()
            resp = DataConnectorsService().delete_data_connector(req_data)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "Error deleting the connection.", "connection_id": None}, 500


@data_connections_api.route('/List_catalogs')
class ListCatalogsResource(Resource):
    @token_required
    @data_connections_api.expect(rest_api.model('ListCatalogsModel', {
        "source": fields.String(example="database", description="Data source type (database, flat_files, s3)",required=True,enum=["database", "flat_files", "s3"]),
        "connection_id": fields.String(example="684aad3e20ef26522ff885f7", description="Unique identifier of the connection or file",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        List data catalogs
        This endpoint retrieves the data catalog (schemas, tables, files) from various data sources including databases, files, and S3 storage. Returns hierarchical structure of available data objects.
        
        **Request Body (JSON) - Database:**
        
        ```json
        {
            "source": "database",
            "connection_id": "database_connection_id"
        }
        ```
        
        **Request Body (JSON) - Files:**
        
        ```json
        {
            "source": "flat_files",
            "connection_id": "file_connection_id"
        }
        ```
        
        **Request Body (JSON) - S3:**
        
        ```json
        {
            "source": "s3",
            "connection_id": "s3-connection-id"
        }
        ```
        
        **Request Parameters:**
        * **source** (`str`): Data source type - "database", "flat_files", or "s3".
        * **connection_id** (`str`): Unique identifier of the connection or file to catalog.
        
        **Sample Response (Success - Database ):**
        
        ```json
        {
            "success": true,
            "dataCatalog": [
                {
                    "title": "public",
                    "value": "public",
                    "children": [
                        {
                            "title": "actor",
                            "value": "public.actor"
                        },
                        {
                            "title": "film",
                            "value": "public.film"
                        },
                        {
                            "title": "customer",
                            "value": "public.customer"
                        }
                    ]
                }
            ],
            "msg": "Data catalog fetched successfully from postgres."
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the catalog retrieval was successful.
        * **dataCatalog** (`array`): Hierarchical data structure containing:
          * **title** (`str`): Human-readable name of the schema/folder/file.
          * **value** (`str`): Full qualified name or path for referencing.
          * **children** (`array`): Nested objects (tables, sheets, files) within the parent.
        * **msg** (`str`): Descriptive message about the operation result.
        
        **Use Cases:**
        * Discover tables and schemas in database connections
        * Explore file contents and sheets in uploaded files
        * Navigate S3 bucket structure for data selection
        * Validate data source contents before processing
        * Build dynamic data selection interfaces

        """
        try:
            req_data = request.get_json()
            file_type = req_data.get("source")
            if file_type == 'database':  
                resp = ListCatalogsService().list_catalogs(req_data)
            elif file_type == 'flat_files':
                file_id = req_data.get("connection_id")
                resp = FileService().get_list_catalogs(file_id)
            elif file_type == 's3':
                resp = S3Service().list_catalogs(req_data)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred.", "dataCatalog": None}, 500

@data_connections_api.route('/connections')
class Connections(Resource): # pragma: no cover
    @token_required
    @data_connections_api.expect(rest_api.model('ConnectionTestModel', {
        "type": fields.String(example="test", description="Operation type (currently only 'test' is supported)",required=True),
        "connector": fields.String(example="postgres", description="Database connector type (postgres, mysql, snowflake, etc.)",required=True),
        "details": fields.Raw(example={"connection_id": "684aad3e20ef26522ff885f7"
        }, description="Connection details including connection ID or credentials", required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Test database connection
        This endpoint allows users to test the connectivity and validity of a database connection before using it for data operations.
        
        **Sample Request Body (JSON):**
        
        ```json
        {
            "type": "test",
            "connector": "postgres",
            "details": {
                "connection_id": "684aad3e20ef26522ff885f7"
            }
        }
        ```
        
        **Request Parameters:**
        * **type** (`str`): Operation type, currently only "test" is supported.
        * **connector** (`str`): Database connector type (postgres, mysql, snowflake, redshift, oracle, etc.).
        * **details** (`object`): Connection configuration, can contain:
          * **connection_id** (`str`): ID of saved connection to test, OR
          
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "msg": "Connection tested successfully"
        }

        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the connection test was successful.
        * **msg** (`str`): Detailed message about connection status or error details.
        
        **Supported Database Types:**
        * **RDBMS**: postgres, mysql, oracle, ms_sql_server
        * **Data Warehouses**: snowflake, redshift, firebird
        * **NoSQL**: cassandra, astra, couchbase
        * **Cloud Storage**: s3, google_sheets
        
        **Use Cases:**
        * Verify network connectivity to database servers
        * Validate connection parameters during setup
        
        """
        try:
            req_data = request.get_json()
            type = req_data.get("type")
            if type=="test": 
                resp = ConnectionService().test_connection(req_data, current_user)
                return resp


        except Exception as e: 
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred while testing the connection."}, 500


@pipeline_workflows_api.route('/data_loads')
class DataLoad(Resource):
    @token_required
    @pipeline_workflows_api.expect(rest_api.model('DataLoadModel', {
        "filesInfo": fields.List(fields.Raw(), 
                                example=[{
                                    "source": "file",
                                    "details": {
                                        "connection_id": "738706f1-a881-4e1b-8fa8-91c71239d1c7",
                                        "chat_id": "689dc7c61ae225256e16e7cf",
                                        "type": ".xlsx",
                                        "file_name": "demo"
                                    }
                                }],
                                description="Array of data sources to load into the job",
                                required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Load multiple data sources into job
        
        This endpoint loads various data sources (files, databases, S3) into a job for processing, supporting batch operations with detailed success/failure tracking for each source.

        **Sample Request Body (JSON):**

        **File Source Example:**
        ```json
        {
            "filesInfo": [
                {
                    "source": "file",
                    "details": {
                        "connection_id": "738706f1-a881-4e1b-8fa8-91c71239d1c7",
                        "chat_id": "689dc7c61ae225256e16e7cf",
                        "type": ".xlsx",
                        "file_name": "demo"
                    }
                }
            ]
        }
        ```

        **Request Parameters:**
        * **filesInfo** (`array`): List of data sources to load, each containing:
          * **source** (`str`): Data source type - "file", "database", or "s3"
          * **details** (`object`): Source-specific configuration parameters

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "message": "All Files Loaded",
            "files_uploaded": [
                "demo loaded Successfully."
            ],
            "files_failed": []
        }
        ```

        **Returns:**
        * **success** (`bool`): Overall operation success status
        * **message** (`str`): Summary message about the loading operation
        * **files_uploaded** (`array`): List of successfully loaded sources with status messages
        * **files_failed** (`array`): List of failed sources with error details

        **Use Cases:**
        * **Data Pipeline Setup**: Load multiple data sources for processing jobs
        * **ETL Operations**: Extract data from various sources into unified job
        * **Data Integration**: Combine file, database, and cloud storage data
        * **Batch Data Loading**: Efficiently load multiple sources simultaneously
        """
        req_data=request.get_json()
        user_id = str(self["_id"])
        files_uploaded = []
        files_failed = []
        try:
            with client._Database__client.start_session() as session:
                mongo_audit_runs = MongoFactory(client, "audit_runs", session)
                mongo_audit_usage = MongoFactory(client, "audit_usage", session)
                for file in req_data.get("filesInfo", []):
                        file["details"]["user_id"]=user_id
                        aod_audit_tracker: AuditTracker = AuditTracker(
                            audit_runs_collection=mongo_audit_runs,
                            audit_usage_collection=mongo_audit_usage,
                            run_context=ScheduleRunContext(
                                user_id=user_id,
                                chat_id=file["details"].get("chat_id", ""),
                                schedule_id="",
                                run_id="",
                                execution_type="llm"
                            )
                        )

                        if file.get("source")=="file":
                            response=session.with_transaction(
                                lambda s: DataLoadService(session, aod_audit_tracker).load_file_to_job(file),
                                read_concern=ReadConcern("local"),
                                write_concern=wc_majority,
                                read_preference=ReadPreference.PRIMARY,
                            )
                        elif file.get("source")=="database":
                            response=session.with_transaction(
                                lambda s: DataLoadService(session, aod_audit_tracker).load_database_to_job(file),
                                read_concern=ReadConcern("local"),
                                write_concern=wc_majority,
                                read_preference=ReadPreference.PRIMARY,
                            )
                        elif file.get("source")=="s3": 
                            response=session.with_transaction(
                                lambda s: DataLoadService(session, aod_audit_tracker).load_s3_file_to_job(file),
                                read_concern=ReadConcern("local"),
                                write_concern=wc_majority,
                                read_preference=ReadPreference.PRIMARY,
                            )
                        else:
                            response = [{"success": False, "message": "Invalid source type","files_failed":[],"files_uploaded":[]}]
                        files_failed.extend(response[0]["files_failed"])
                        files_uploaded.extend(response[0]["files_uploaded"])
                        if response[0]["success"]:
                            overall_success=True
                            overall_message="All Files Loaded"
                        else:
                            overall_success=False
                            overall_message="Few Files Failed to load." 
                overall_status_code = 200
                return {
                    "success": overall_success,
                    "message": overall_message,
                    "files_uploaded": files_uploaded,
                    "files_failed": files_failed
                }, overall_status_code
        except Exception as e:
            return {
                    "success": False,
                    "message": f"{e}",
                    "files_uploaded": [],
                    "files_failed": []
                }, 500


@file_management_api.route('/remove_file')
class RemoveFileFromChat(Resource):
    @token_required
    @file_management_api.expect(rest_api.model('RemoveFileModel', {
        "chat_id": fields.String(example="689b0f46218458a8922ab3ee", description="Chat session ID to remove the file from",required=True),
        "source_id": fields.String(example="88809a4e-2f96-43c2-a1dd-0da3ce9abf7b", description="Unique identifier of the file to remove from chat", required=True)
    }), validate=False)
    def delete(self, current_user):
        """
        Remove file from chat session
        This endpoint removes a specific file from a chat session's . The file is unloaded from the chat but remains in the user's file library.
        
        **Request Body (JSON):**
        
        ```json
        {
            "chat_id": "chat_id_123",
            "source_id": "source_id_123"
        }
        ```
        
        **Request Parameters:**
        * **chat_id** (`str`): Chat session ID from which to remove the file.
        * **source_id** (`str`): Unique identifier of the file to remove from the chat session.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "message": "File Deleted Successfully"
        }
        ```
        **Returns:**
        * **success** (`bool`): Indicates if the file removal was successful.
        * **message** (`str`): Descriptive message about the operation result.

        **Recovery:**
        * File can be re-added to the chat session anytime
        * Original file data and metadata remain intact
        * File is still available in the user's file library
        * No data loss occurs from this operation
        
        """
        req_data=request.get_json()
        try:
            with client._Database__client.start_session() as session:
                response, status_code = session.with_transaction(
                    lambda s: DataLoadService(session).remove_file_from_job(req_data),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )
            return response, status_code
                # return response, status_code
        except Exception as e:
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred while removing the file."}, 500

@pipeline_workflows_api.route('/execute')
class Execute(Resource):

    # @token_required
    @pipeline_workflows_api.expect(rest_api.model('ExecuteModel', {
        "type": fields.String(example="preview", description="Execution type: 'preview' for data preview or 'execute' for full execution",required=True,enum=["preview", "execute"]),
        "per_page": fields.Integer(example=10, description="Number of records per page (for preview type)",required=False),
        "page": fields.Integer(example=1, description="Page number for pagination (for preview type)",required=False),
        "preview_info": fields.List(fields.Raw(), example=[{"alias": "demo","source_id": "source_id_123"}],description="Array of data sources to preview or execute",required=True),
        "user_info": fields.Raw(example={"user_id": "user_id_123","chat_id": "chat_id_123"}, description="User and chat session information", required=True)
    }), validate=False)
    def post(self):
        """
        Execute data operations or preview data

        This endpoint provides dual functionality for data processing: generating data previews for exploration and executing complete data operations. It supports pagination for large datasets and handles multiple data sources in a single request.

        ### Execution Types:

        ### Preview Mode ("preview"):
        Generates a paginated preview of data without executing full transformations. Ideal for data exploration, validation, and understanding dataset structure before committing to full processing.

        ### Execute Mode ("execute"):
        Performs complete data processing operations including transformations, aggregations, and other pipeline tasks. This mode commits changes and produces final results.

        ### Request Body (JSON):

        ```json
        {
            "type": "preview",
            "per_page": 10,
            "page": 1,
            "preview_info": [
                {
                    "alias": "demo",
                    "source_id": "source_id_123"
                }
            ],
            "user_info": {
                "user_id": "user_id_123",
                "chat_id": "chat_id_123"
            }
        }
        ```
        ### Request Parameters:

        ### Core Parameters:
        * **type** (`str`): Execution type - "preview" for processing.
        * **preview_info** (`array`): List of data sources to process, each containing:
          * **alias** (`str`): User-friendly name for the data source.
          * **source_id** (`str`): Unique identifier of the data source.
        * **user_info** (`object`): User and session context.
          * **user_id** (`str`): Authenticated user identifier.
          * **chat_id** (`str`): Chat session where the operation is performed.

        ### Pagination Parameters (Preview Only):
        * **per_page** (`int`, optional): Number of records to return per page (default: 10).
        * **page** (`int`, optional): Page number for pagination (default: 1).

        ### Response (Success - Preview - 200):

        ```json
        {
            "success": true,
            "preview": [
                {
                    "_id": "source_id_123",
                    "alias": "demo",
                    "total_records": 1,
                    "total_records_dataframe": 1,
                    "columns": [
                        {
                            "name": "last_name",
                            "dataType": "object"
                        },
                        {
                            "name": "last_update",
                            "dataType": "datetime64[ns]"
                        }
                    ],
                    "data": [
                        {
                            "last_name": "S",
                            "last_update": "2025-05-25"
                        }
                    ]
                }
            ],
            "page": 1,
            "per_page": 10,
            "total_records": 1
        }
        ```

        ### Use Cases and Applications:

        ### Data Exploration:
        * **Schema Discovery**: Understand data structure and column types
        * **Data Quality Assessment**: Identify data issues and anomalies
        * **Sample Analysis**: Analyze representative data samples
        * **Validation**: Verify data loading and transformation logic
        """
        try:
            req_data = request.get_json()
            try:
                req_data = json.loads(req_data)
            except:
                pass
            with client._Database__client.start_session() as session:
                if req_data["type"]=="preview":
                    resp=session.with_transaction(
                        lambda s:ExecuteService(session).preview(req_data),
                        read_concern=ReadConcern("local"),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,
                    ) 
                    
                else:
                    resp=session.with_transaction(
                        lambda s:ExecuteService(session).execute(req_data),
                        read_concern=ReadConcern("local"),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,
                    ) 
                    
            return resp


        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred while Executing  the data."}, 500

@export_download_api.route('/export_config')
class ExportConfigResource(Resource):
    """
    Utkarsh Added for temp adding of export configurations
    """

    @token_required
    @export_download_api.expect(rest_api.model('ExportConfigModel', {
        "chat_id": fields.String(example="689d8f76632ede346edc6ee3", description="Chat session ID to configure export settings for",required=True),
        "configurations": fields.Raw(example={}, description="Export configuration parameters and settings",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Configure export settings for chat session
        
        This endpoint allows users to set up and update export configurations for a specific chat session, defining how data will be exported from the session.

        **Sample Request Body (JSON):**

        ```json
        {
            "chat_id": "689d8f76632ede346edc6ee3",
            "configurations": {}
        }
        ```

        **Request Parameters:**
        * **chat_id** (`str`): Chat session ID where export configuration will be applied
        * **configurations** (`object`): Export settings and parameters.

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "msg": "Export configuration updated"
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the configuration update was successful
        * **msg** (`str`): Confirmation message about the operation result

        **Use Cases:**
        * Configure automatic data export after processing
        * Set up recurring export schedules and formats
        * Define destination connections for processed data
        * Customize export formats for different business needs
        * Prepare data export configurations for scheduled jobs
        """
        try:
            req_data=request.get_json()
            user_id = str(self["_id"]) 
            resp = ExportConfigService().export_config(req_data, user_id) 
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred during export configuration."}, 500

@audit_billing_api.route('/audit/billing/explore')
class AuditUsageRoute(Resource):
    @token_required
    @rest_api.doc(params={
        'start_time': {'description': 'Start time for audit period in ISO format (YYYY-MM-DDTHH:MM)','type': 'string','required': True,'in': 'query','example': '2025-08-04T00:00'},
        'end_time': {'description': 'End time for audit period in ISO format (YYYY-MM-DDTHH:MM)','type': 'string','required': True,'in': 'query','example': '2025-08-04T23:59'}
    })
    def get(self, current_user):
        """
        Explore detailed audit usage
        This endpoint provides detailed audit information for billing and usage analysis within a specific time period. Allows filtering by various parameters to drill down into specific operations.
        
        **Query Parameters:**
        * **start_time** (`str`, required): Start time for audit period in ISO format (YYYY-MM-DDTHH:MM).
        * **end_time** (`str`, required): End time for audit period in ISO format (YYYY-MM-DDTHH:MM).
        
        **Example Request:**
        ```
        GET /audit/billing/explore?start_time=2025-08-04T00:00&end_time=2025-08-04T23:59
        ```
        
        **Response (Success - 200):**
        
        ```json
        {
            "Audits": [
                {
                    "Chat_id": "68903d916cec0939b9e71d50",
                    "Schedule_id": null,
                    "Run_id": null,
                    "mode": "pipeline",
                    "Total_run_cost": 0,
                    "run_start_time": "2025-08-04T05:30:23.231000",
                    "run_end_time": "2025-08-04T08:01:42.509000"
                },
                {
                    "Chat_id": "6890680fb05bf6d4881145a4",
                    "Schedule_id": "689068aab05bf6d4881145a8",
                    "Run_id": "manual__2025-08-04T08:00:42.123111+00:00",
                    "mode": "pipeline",
                    "Total_run_cost": 5,
                    "run_start_time": "2025-08-04T05:30:23.231000",
                    "run_end_time": "2025-08-04T08:01:42.509000"
                }
            ]
        }
        ```
        
        **Returns:**
        * **Audits** (`array`): List of detailed audit records, each containing:
          * **Chat_id** (`str`): Chat session identifier where the operation was performed.
          * **Schedule_id** (`str` or `null`): Schedule identifier if operation was scheduled.
          * **Run_id** (`str` or `null`): Unique run identifier for tracking specific executions.
          * **mode** (`str`): Execution mode (pipeline, manual, scheduled).
          * **Total_run_cost** (`int`): Cost or resource usage for the operation.
          * **run_start_time** (`str`): ISO timestamp when the operation started.
          * **run_end_time** (`str`): ISO timestamp when the operation completed.
        
        **Use Cases:**
        * Analyze resource usage patterns over time
        * Track costs for specific chat sessions or projects
        * Monitor scheduled job performance and costs
        * Generate detailed billing reports for users.
        
        """
        try:
            req_data={}
            user_id = str(self["_id"])

            req_data['chat_id'] = request.args.get('chat_id', None)
            req_data['schedule_id'] = request.args.get('schedule_id', None)
            req_data['run_id'] = request.args.get('run_id', None)
            req_data['mode'] = request.args.get('mode', None)
            req_data['start_time'] = request.args.get('start_time', None)
            req_data['end_time'] = request.args.get('end_time', None)

            if req_data['start_time'] is None or req_data['end_time'] is None:
                return {"success": False, "msg": "start_time and end_time are required parameters"}, 400
  
            resp = AuditUsage().get_audit(user_id, req_data)
            return resp

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred during get audit."}, 500

@audit_billing_api.route('/audit/billing/summary')
class BillingUsageRoute(Resource):
    @token_required
    @rest_api.doc(params={
        'summary_type': {
            'description': 'Type of summary aggregation (daily, weekly, monthly, yearly)',
            'type': 'string',
            'required': True,
            'in': 'query',
            'enum': ['daily', 'weekly', 'monthly', 'yearly'],
            'example': 'monthly'
        },
        'target_date': {
            'description': 'Target date for the summary in YYYY-MM-DD format',
            'type': 'string',
            'required': True,
            'in': 'query',
            'format': 'date',
            'example': '2025-08-11'
        }
    })
    def get(self, current_user):
        """
        Get billing usage summary
        This endpoint allows user to retrieve billing and usage summary information for a specified time period with different aggregation levels.
        
        **Query Parameters:**
        * **summary_type** (`str`): Type of summary aggregation. Available options: "daily", "weekly", "monthly", "yearly".
        * **target_date** (`str`): Target date for the summary in YYYY-MM-DD format (e.g., "2025-08-11").
        
        **Example Request:**
        ```
        GET /audit/billing/summary?summary_type=monthly&target_date=2025-08-11
        ```
        
        **Sample Response (Success - 200):**
        
        ```json
        {
            "user_id": "user_id_123",
            "summary_type": "monthly",
            "start_date": "2025-08-01 00:00:00",
            "end_date": "2025-09-01 00:00:00",
            "total_audit_cost": 68,
            "daily_details": [
                {
                    "day": 4,
                    "audit_cost": 40,
                    "detail_link": "/audit/billing/explore?start_time=2025-08-04T00:00&end_time=2025-08-04T23:59"
                },
                {
                    "day": 6,
                    "audit_cost": 28,
                    "detail_link": "/audit/billing/explore?start_time=2025-08-06T00:00&end_time=2025-08-06T23:59"
                }
            ],
            "_id": "(True, ObjectId('id_123'))"
        }
        ```
        
        **Returns:**
        * **user_id** (`str`): ID of the user for whom the billing summary is generated.
        * **summary_type** (`str`): Type of summary aggregation that was requested.
        * **start_date** (`str`): Start date and time of the billing period in YYYY-MM-DD HH:MM:SS format.
        * **end_date** (`str`): End date and time of the billing period in YYYY-MM-DD HH:MM:SS format.
        * **total_audit_cost** (`int`): Total cost/usage for the specified period.
        * **daily_details** (`array`): Breakdown of usage by day within the period:
          * **day** (`int`): Day of the month.
          * **audit_cost** (`int`): Cost/usage for that specific day.
          * **detail_link** (`str`): URL to get detailed breakdown for that day.
        * **_id** (`str`): Internal database identifier for the summary record.
        
        **Summary Types:**
        * **daily**: Shows usage for a single day
        * **weekly**: Shows usage for a week period
        * **monthly**: Shows usage for a month with daily breakdown
        * **yearly**: Shows usage for a year with monthly breakdown
        """
        try:
            req_data = {}
            user_id = str(self["_id"])

            req_data['summary_type'] = request.args.get("summary_type")
            req_data['target_date'] = request.args.get("target_date")
 
            resp = AuditUsage().get_billing_summary(user_id, req_data)
            return resp

        except Exception as e:  # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {"success": False, "msg": "An error occurred during billing summary."}, 500

@export_download_api.route('/download/<feather_id>')
class Download(Resource):
    """
    Downloads the exported file.
    """

    @token_required
    @rest_api.doc(params={
        'chat_id': {'description': 'Chat session ID where the file was exported','type': 'string','required': True,'in': 'query','example': '689d9e36e94776e1d0964844'}
    })
    def get(self, current_user, feather_id):
        """
        Download exported file
        
        This endpoint allows users to download files that have been exported from their data processing sessions using the unique feather ID and chat session context.

        **Path Parameter:**
        * **feather_id** (`str`): Unique identifier of the exported file to download

        **Query Parameters:**
        * **chat_id** (`str`): Chat session ID where the file was originally exported

        **Example Request:**
        ```
        GET /download/abc123def456?chat_id=689d9e36e94776e1d0964844
        ```

        **Response (Success - 200):**
        
        Returns the actual file content with appropriate headers for download. The response will include:
        * **Content-Type**: Based on file format (text/csv, application/json, etc.)
        * **Content-Disposition**: attachment; filename="exported_data.csv"
        * **File Content**: The actual exported data

        """
        try:
            chat_id = request.args.get('chat_id')
            resp = DownloadService().download_file(feather_id, chat_id)
            return resp

        except:
            return {
                "success": False,
                "text": "The file not found"
            }, 404
            
            
@airflow_scheduling_api.route('/dms', methods=['GET', 'POST', 'DELETE'])
class DMS(Resource):
    """
    Resource for DMS (Data Migration Service) related operations.
    """
    @token_required
    @Logger.generate
    @airflow_scheduling_api.expect(
        rest_api.model('DMSCreateScheduleModel', {
            "schedule_name": fields.String(
                required=True,
                description="Name of the schedule"
            ),
            "schedule_interval": fields.String(
                required=True,
                description="Interval to use for scheduling"
            ),
            "advanced_scheduling": fields.Raw(
                required=False,
                description="Advanced Scheduling details",
                example={}
            ),
            "notification": fields.Raw(
                required=False,
                description="Notification object",
                example={}
            ),
            "migration_details": fields.Raw(
                required=True,
                description="Details for migration",
                example={
                    "mode":"replace",
                    "source_parameters": {
                        "connection_id": "conn-123",
                        "table_name": "public.actor_src"
                    },
                    "destination_parameters": {
                        "connection_id": "conn-234",
                        "table_name": "public.actor_dest"
                    },
                    "primary_key": "actor_id",
                    "migration_type": "table-to-table"
                }
            )
        })
    )
    def post(self, current_user):
        """
        Create a DMS (Data Migration Service) schedule

        This endpoint provisions a DMS workflow that moves data between two
        saved connections via Airflow. The workflow creates a backing chat (if chat_id is not provided),
        stores the YAML, and registers a schedule that Airflow can execute.

        **Request Body (JSON):**

        ```json
        {
            "mode": "replace",
            "source_parameters": {
                "connection_id": "src-conn-id",
                "table_name": "public.source_table"
            },
            "destination_parameters": {
                "connection_id": "dest-conn-id",
                "table_name": "analytics.target_table"
            },
            "primary_key": "id",
            "migration_type": "table-to-table",
            "schedule_name": "Nightly migration",
            "schedule_interval": "daily",
            "user_id": "684aaaa4ae3f96339c3a4c12",
            "chat_id": "231aaaa4ae4436339c3a4c12",
            "advanced_scheduling": {},
            "notification": {},
            "migration_details": {
                "mode": "replace" # default mode for migration is replace
                "source_parameters": {
                    "connection_id": <connection_id>,
                    "table_name": public.actor_src
                },
                "destination_parameters": {
                    "connection_id": <connection_id>,
                    "table_name": public.actor_dest
                },
                "primary_key": "actor_id",
                "migration_type": "table-to-table",
                "query": "SELECT * FROM public.actor_src" # "query" parameter is only required for migration_type: 'custom-sql'
            }
        }
        ```

        **Request Parameters:**
        * **mode** (`str`, optional): merge, replace, or append. Defaults to `replace`.
        * **source_parameters.connection_id** (`str`, required): Source connection ID.
        * **source_parameters.table_name** (`str`, optional): Source table (required when migrating a table).
        * **destination_parameters.connection_id** (`str`, required): Destination connection ID.
        * **destination_parameters.table_name** (`str`, optional): Destination table name.
        * **primary_key** (`str`, optional): Primary key field to use; defaults to `id`.
        * **migration_type** (`str`, optional): `table-to-table`, `database-to-database`, or `custom-sql`. Defaults to `table-to-table`.
        * **schedule_name** (`str`, optional): Friendly name for the generated schedule.
        * **schedule_interval / advanced_scheduling** (`object`, optional): Cron or builder style schedule definition.
        * **notification** (`object`, optional): Notification settings for job completion.
        * **user_id** (`str`, required): Must match the authenticated user in the token.
        * **chat_id** (`str`, optional): Chat id for the DMS, if not passed, a new internal chat is created.
        * **migration_details** (object, required): Details for the DMS migration

        **Response (Success - 200):**

        ```json
        {
            "message": "Created DMS DAG successfully",
            "schedule_id": "689de0e36e892a99f5ff9568"
        }
        ```

        **Returns:**
        * **message** (`str`): Status of the DMS creation.
        * **schedule_id** (`str`): Identifier of the Airflow schedule that will execute the migration.

        """
        try:
            data = request.json
            # This endpoint would create a corresponding chat (if chat_id is not passsed), then populate the yaml inside it and then create a schedule
            user_id = data.get('user_id')
            if user_id != self["_id"]:
                raise ValueError(f"Invalid user id passed")
            chat_id = data.get('chat_id', None)
            advanced_scheduling = data.get("advanced_scheduling", {})
            # TODO: `scheduling_interval` key is kept for backward compatibility, we can remove this after DMS-DTS sync (#1685)
            if "scheduling_interval" in data:
                schedule_interval = data.get("scheduling_interval", None)
            else:
                schedule_interval = data.get("schedule_interval", None)
            schedule_name = data.get("schedule_name")
            execution_type = "pipeline" # Fixed for DMS for now
            notification = data.get("notification", {})
            run_engine_type = "dlt" # Fixed for DMS for now

            # Prepare migration details step
            input_migration_details = data.get("migration_details", {})

            def _normalise_increment_key(raw):
                """Return str | list[str] | None — never an empty string or non-string elements.

                Accepts:
                  - None / "" / []     → None
                  - "col1"             → "col1"       (single key, string)
                  - "col1,col2"        → ["col1", "col2"]
                  - ["col1"]           → "col1"       (single-element list unwrapped to str)
                  - ["col1", "col2"]   → ["col1", "col2"]
                  - ["col1", ""]      → "col1"        (blank entries stripped)

                Single-element lists are unwrapped to a bare string so the
                value stored in MongoDB is always `str` for one key and
                `list[str]` for multiple — consistent with what the migration
                engine expects and what the frontend sends for a single key.
                """
                if not raw:
                    return None
                if isinstance(raw, str):
                    raw = [k.strip() for k in raw.split(",") if k.strip()]
                if isinstance(raw, (list, tuple)):
                    cleaned = [str(k).strip() for k in raw if str(k).strip()]
                    if not cleaned:
                        return None
                    return cleaned[0] if len(cleaned) == 1 else cleaned
                return None


            migration_details = {
                "function": "data_migration",
                "mode": input_migration_details.get("mode", "replace"),
                "migration_type": input_migration_details.get("migration_type", "table-to-table"),
                "primary_key": input_migration_details.get("primary_key", None),
                "increment_key": _normalise_increment_key(input_migration_details.get("increment_key"))
            }

            # Attach source and destination parameters
            source_parameters = {}
            possible_source_keys = ["connection_id", "table_name", "connection", "file_id", "file_name"]
            for key in possible_source_keys:
                if key in input_migration_details["source_parameters"]:
                    source_parameters[key] = input_migration_details["source_parameters"][key]
            migration_details["source_parameters"] = source_parameters

            destination_parameters = {}
            possible_destination_keys = ["connection_id", "table_name", "connection"]
            for key in possible_destination_keys:
                if key in input_migration_details["destination_parameters"]:
                    destination_parameters[key] = input_migration_details["destination_parameters"][key]
            migration_details["destination_parameters"] = destination_parameters
            
            # We should keep a default primary key in case of "merge" mode
            if migration_details.get("mode") == "merge" and migration_details.get("primary_key") is None:
                migration_details["primary_key"] = "id"
            
            if migration_details.get("migration_type") == "custom-sql":
                query = data.get("migration_details", {}).get("query")
                assert query is not None, f"migration_type 'custom-sql' requires non-null query, received None"
                migration_details["query"] = query
            
            response = AirflowAPI().create_dms_dag(
                user_id=user_id,
                chat_id=chat_id,
                schedule_name=schedule_name,
                schedule_interval=schedule_interval,
                advanced_scheduling=advanced_scheduling,
                notification=notification,
                engine_type=run_engine_type,
                execution_type=execution_type,
                migration_details=migration_details
            )
            return response
        except Exception as e:
            logger.error(f"Failed to create DMS job: {e}", exc_info=True)
            return {"error": "Failed to create DMS job"}, 400
        
    @token_required
    @Logger.generate
    @airflow_scheduling_api.doc(
        params={
            'user_id': {
                'description': 'User id',
                'type': 'string',
                'required': True,
                'in': 'query',
                'example': 'user_id_123'
            },
            'schedule_id': {
                'description': 'Id of the specific DMS schedule user wants to fetch',
                'type': 'string',
                'required': False,
                'in': 'query',
                'example': 'schedule_id_123'
            }
        }
    )
    def get(self, current_user):
        """
        Get DMS schedules created for the user via query parameters.

        **Query Parameters:**
        * **user_id** (`str`, required): Owner user ID. Must match the token.
        * **schedule_id** (`str`, optional): Filter results to a specific schedule.
        """
        try:
            user_id = request.args.get("user_id")
            schedule_id = request.args.get("schedule_id")

            if not user_id:
                return {"success": False, "message": "user_id is required"}, 400

            if user_id != self["_id"]:
                raise ValueError("Invalid user id passed")

            return AirflowAPI().get_dms_schedule_info(user_id=user_id, schedule_id=schedule_id)
        except Exception as e:
            logger.error(f"Error fetching DMS schedule info: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "schedules": []
            }, 500
    
    @token_required
    @Logger.generate
    @airflow_scheduling_api.expect(
        rest_api.model('DMSDeleteScheduleModel', {
            "schedule_id": fields.String(
                required=True,
                description="Schedule Id to be deleted"
            ),
            "user_id": fields.String(
                required=True,
                description="User Id making this request"
            )
            }
        )
    )
    def delete(self, current_user):
        """
        This endpoint is used to delete the DMS schedule along with related data.
        
        **Request Body (JSON):**
        
        ```json
        {
            "schedule_id": "schedule-123",
            "user_id": "user-123"
        }
        ```
        
        **Response (Success - 200):**
        ```json
        {
            "message": "DMS schedule successfully deleted",
            "schedule_id": "schedule-123"
        }
        ```
        """
        try:
            data = request.json
            user_id = data.get("user_id", None)
            schedule_id=data.get("schedule_id", None)
            if user_id is None or schedule_id is None:
                raise ValueError(f"`user_id` and `schedule_id` are required fields")
            if user_id != self["_id"]:
                raise ValueError(f"Invalid user id passed")
            response = AirflowAPI().delete_dms_dag(
                user_id=user_id,
                schedule_id=data.get("schedule_id")
            )
            return response
        except ValueError as e:
            logger.error(f"Failed to delete DMS schedule: {e}", exc_info=True)
            return {"error": f"Failed to delete DMS JOB {e}"}, 400
        except Exception as e:
            logger.error(f"Failed to delete DMS schedule: {e}", exc_info=True)
            return {"error": "Failed to delete the DMS job"}, 500
        
    
@airflow_scheduling_api.route('/dag/<string:job_id>',methods=['PATCH'])
@airflow_scheduling_api.route('/dag',methods=['POST'])    
class DAG(Resource):
    """
    Resource for DAG-related operations (create, delete, get info).

    This class provides endpoints for managing Directed Acyclic Graphs (DAGs) in Airflow, 
    allowing for operations like creating, deleting, and retrieving information about specific DAGs.
    """
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGCreateModel', {
        "job_id": fields.String(example="job_id_123",description="Unique identifier for the job", required=True),
        "job_name": fields.String(example="Job 123", description="Display name for the job", required=True),
        "user_id": fields.String(example="user_id_123", description="User ID who owns the job", required=True),
        "schedule_interval": fields.String(example="weekly", description="Schedule frequency (weekly, daily, monthly, yearly, one)", required=True),
        "job_details": fields.Raw(example={"files_list": [{"alias": "demo","type": "xlsx","source_id": "2456c0bc-1ff2-4469-b95a-afa25f506f8a","_id": "738706f1-a881-4e1b-8fa8-91c71239d1c7"}],"type": "localstorage"}, description="Job configuration and file details", required=True),
        "engine_type": fields.String(example="spark", description="Processing engine type", required=False, enum=["spark", "dlt", "local"]),
        "schedule_name": fields.String(example="Test", description="Name for the schedule", required=False),
        "executionType": fields.String(example="pipeline", description="Type of execution", required=True),
        "replace_connections": fields.Raw(example={},description="Connection replacement mappings", required=False),
        "notification": fields.Raw(example={"active": False,"type": "email","details": {"to": None,"subject": None,"body": None}}, description="Notification configuration", required=False),
        "advance_scheduling": fields.Raw(example={"Frequency": "weekly","RepeatsEvery": 1,"StartDate": "2025-08-14","StartTime": "18:57:58","timeZone": "Asia/Calcutta","dateFormat": "DD/MM/YYYY hh:mm A","ends": "on","DaysofWeek": [],"EndDate": "2025-08-14","EndTime": "19:12:58"}, description="Advanced scheduling configuration", required=False),
        "should_create_v1_schedule": fields.Boolean(example=False, description="Create schedule in legacy (v1) format for backward compatibility", required=False)
    }), validate=False)
    @Logger.generate
    def post(self, current_user):
        """
        Create and schedule new DAG in Airflow
        
        This endpoint creates a new Directed Acyclic Graph (DAG) in Airflow with comprehensive scheduling and execution configuration for data processing workflows.

        **Request Body (JSON):**

        ```json
        {
            "job_id": "job_id_123",
            "job_name": "Job 123",
            "user_id": "user_id_123",
            "schedule_interval": "weekly",
            "job_details": {
                "files_list": [{......}],
                "type": "localstorage"
            },
            "engine_type": "spark",
            "schedule_name": "Test",
            "executionType": "pipeline",
            "replace_connections": {},
            "notification": {
                "active": false,
                "type": "email",
                "details": {
                    "to": null,
                    "subject": null,
                    "body": null
                }
            },
            "advance_scheduling": {.....}
        }
        ```

        **Request Parameters:**

        **Core Job Configuration:**
        * **job_id** (`str`): Unique identifier for the job/DAG
        * **job_name** (`str`): Human-readable name for the job
        * **user_id** (`str`): Owner/creator of the job
        * **executionType** (`str`): Type of execution workflow

        **Scheduling Configuration:**
        * **schedule_interval** (`str`): Schedule frequency - "weekly", "daily", "monthly", "yearly", "one" (run once)
        * **schedule_name** (`str`, optional): Named identifier for the schedule (required for scheduled jobs)
        * **advance_scheduling** (`object`, optional): Detailed scheduling parameters

        **Processing Configuration:**
        * **engine_type** (`str`, optional): Processing engine - "spark" (default), "dlt", "local"
        * **job_details** (`object`): Job configuration including file lists and processing details
        * **replace_connections** (`object`, optional): Connection replacement mappings

        **Notification Setup:**
        * **notification** (`object`, optional): Email/webhook notification configuration

        **Response (Success - 200):**

        ```json
        {
            "message": "Scheduled Test schedule for the job Job 1231144 successfully",
            "job_id": "689dd74ba8d86686f91541b9",
            "run_id": "manual__2025-08-14T13:13:07.885251+00:00",
            "local": true,
            "schedule_id": "689de0e36e892a99f5ff9568",
            "engine_type": "spark",
            "cron_expression": "57 18 * *0"
        }
        ```

        **Returns:**
        * **message** (`str`): Success message with schedule details
        * **job_id** (`str`): Unique identifier of the created job
        * **run_id** (`str`): Initial run identifier
        * **local** (`bool`): Whether job runs locally or on cluster
        * **schedule_id** (`str`): Unique identifier for the schedule
        * **engine_type** (`str`): Configured processing engine
        * **cron_expression** (`str`): Generated cron expression for scheduling

        **Use Cases:**
        * **Automated Data Processing**: Schedule regular ETL operations
        * **Report Generation**: Automated business report creation
        * **Data Synchronization**: Regular data updates between systems
        * **Analytics Workflows**: Scheduled analytical computations
        * **Data Quality Monitoring**: Regular data validation and quality checks
        """
        try:
            data = request.json
            job_id = data.get('job_id')
            user_id = data.get('user_id')
            job_name = data.get('job_name')
            advanced_scheduling = data.get("advance_scheduling",{})
            logger.info(data)
            logger.info(job_name)
            schedule_interval = data.get('schedule_interval')
            job_details = data.get('job_details', {})
            schedule_name = data.get('schedule_name')
            executionType = data.get('executionType', 'pipeline')
            replace_connections=data.get('replace_connections',{})
            notification = data.get('notification', {})
            run_engine_type = data.get('engine_type', 'spark')  # Default to 'spark' if not provided
            should_create_v1_schedule = data.get('should_create_v1_schedule', False)

            # Extract export_format only for localstorage type
            export_format = data.get('export_format', 'csv') if job_details.get('type') == 'localstorage' else None

            if run_engine_type not in ['spark', 'dlt']:
                return {"error": f"Invalid engine_type {run_engine_type}, allowed: spark, dlt"}, 400
            
            if not job_id or not user_id or not schedule_interval or not executionType:
                required_params = {
                    'job_id': job_id,
                    'user_id': user_id,
                    'schedule_interval': schedule_interval,
                    'executionType': executionType,
                }

                # if "Schedule" is triggered instead of "Run now" schedule name is also necessary
                if not (schedule_interval == "once" or schedule_interval is None):
                    required_params["schedule_name"] = schedule_name

                missing_params = [param for param, value in required_params.items() if not value]
                logger.error(f"Missing required parameters - {','.join(missing_params)}", exc_info=True)
                return {"error": f"Missing required parameters - {','.join(missing_params)}"}, 400

            resp = AirflowAPI().create_dag(
                job_id, user_id, job_name,schedule_interval, advanced_scheduling,
                job_details,schedule_name,executionType, run_engine_type,
                replace_connections=replace_connections, notification=notification,
                should_create_v1_schedule=should_create_v1_schedule,export_format=export_format
            )
            return resp
        except Exception as e:
            logger.error(f"Failed to Create job: {e}", exc_info=True)
            return {"error": "Failed to Create job"}, 400
    @token_required
    def delete(self, current_user, job_id):
        """
        Delete a DAG in Airflow -
        Endpoint to delete an existing Directed Acyclic Graph (DAG) based on the provided job ID.
        :param job_id: Job ID of the DAG to be deleted. Type - String
        :return: Response. Type - JSON Formatted String. Contains either DAG deletion confirmation or an error message.
        """
        try:
 
            resp = AirflowAPI().delete_dag(job_id)
            return resp

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }, 404
    @token_required
    def get(self, current_user, job_id):
        """
        Retrieve DAG Information -
        Endpoint to get information about an existing Directed Acyclic Graph (DAG) based on the provided job ID.
        :param job_id: Job ID of the DAG to get information about. Type - String
        :return: Response. Type - JSON Formatted String. Contains DAG information or an error message.
        """
        try:
            resp = AirflowAPI().get_dag_info(job_id) 
            return resp

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }, 404
    
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGPauseModel', {
    "is_paused": fields.Boolean(example=False,description="Pause state - true to pause DAG, false to unpause/resume DAG", required=True)}), validate=False)
    def patch(self, current_user, job_id):
        """
        Pause or unpause DAG execution
        
        This endpoint allows you to pause or resume a Directed Acyclic Graph (DAG) execution. Pausing a DAG prevents it from being scheduled for new runs, while unpausing resumes normal scheduling.

        **Path Parameter:**
        * **job_id** (`str`): Unique identifier of the DAG to pause/unpause

        **Request Body (JSON):**

        ```json
        {
            "is_paused": false
        }
        ```

        **Request Parameters:**
        * **is_paused** (`bool`): Pause state for the DAG
        * `true`: Pause the DAG (stop scheduling new runs)
        * `false`: Unpause/resume the DAG (allow normal scheduling)

        **Response (Success - Unpaused - 200):**

        ```json
        {
            "success": true,
            "message": "Unpaused DAG successfully."
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the pause/unpause operation was successful
        * **message** (`str`): Confirmation message about the operation performed

        """
        try:
            req_data=request.json
            resp = AirflowAPI().pause_dag(job_id, req_data)
            return resp

        except Exception as e:
            return {
                "success": False,
                "text": str(e)
            }, 404


@airflow_scheduling_api.route('/list/runs')
class DAGRuns(Resource):
    """
    Resource for getting information about DAG runs.

    This class provides an endpoint for fetching details of all runs of Directed Acyclic Graphs (DAGs) in Airflow.
    It allows users to get a comprehensive view of the execution status and history of various DAGs.
    """
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGRunsListModel', {
        "user_id": fields.String(example="684aaaa4ae3f96339c3a4c12", description="User ID to retrieve DAG runs for",required=True)
    }), validate=False)
    def post(self, _):
        """
        Retrieve comprehensive DAG runs and scheduling information

        This endpoint provides a complete overview of all Directed Acyclic Graph (DAG) runs and their associated scheduling configurations for a specific user. DAGs represent automated data processing workflows that are scheduled and executed by Apache Airflow. This endpoint returns detailed information about each DAG's current state, execution history, scheduling parameters, data sources, destinations, and notification settings.

        **Request Body (JSON):**
        ```json
        { "user_id": "user_id_123", "page": 1, "per_page": 10, "schedule_name": ["sch1", "sch2"], "job_name": ["job1", "job2"] }
        ```

        **Request Fields:**
        * `user_id` (string): Unique identifier of the user.
        * `page` (int): Page number for pagination.
        * `per_page` (int): Page size for pagination.
        * `schedule_name` (array): List of schedule names to be filtered. This is optional.
        * `job_name` (array): List of job names to be filtered. This is optional.

        **Sample Response (Success – 200):**
        ```json
        {
        "dags": [
            {
            "dag_display_name": "68b6ed4e064a8e23681663",
            "dag_id": "68b6ed4e064a8e23681663",
            "is_active": true,
            "is_paused": true,
            "next_dagrun": null,
            "next_dagrun_create_after": null,
            "next_dagrun_data_interval_end": null,
            "next_dagrun_data_interval_start": null,
            "owners": ["airflow"],
            "schedule_interval": { "__type": "CronExpression", "value": "57 18 * * 0" },
            "tags": [
                {"name": "local:True"},
                {"name": "job_name:Job 2"},
                {"name": "schedule_name:Test"},
                {"name": "engine_type:spark"},
                {"name": "user_id:68b6d4e69349b8c6ac9e"}
            ],
            "timetable_description": "At 18:57, only on Sunday",
            "local": true,
            "job_name": "Job 2",
            "schedule_name": "Test",
            "starts_on": "2025-09-02T18:57:21+05:30",
            "schedule_id": "68b6ed4e064a8e2368141663",
            "cron_expression": "57 18 * * 0",
            "meta_schedule_version": 2,
            "job_details": {
                "configuration": [],
                "files_list": [
                {
                    "alias": "demo",
                    "type": "xlsx",
                    "source_id": "4848a986-778f-4107-ba3f-e24407b09584",
                    "_id": "05015ba9-f23c-4414-a4a1-0e3e57ba7b93",
                    "connection_type": "file",
                    "connection_alias": "demo"
                }
                ],
                "export_files_list": [
                {
                    "alias": "demo",
                    "type": "xlsx",
                    "source_id": "4848a986-778f-4107-ba3f-e24407b09584",
                    "_id": "05015ba9-f23c-4414-a4a1-0e3e57ba7b93"
                }
                ],
                "destination": [
                { "destination": "localstorage", "source_id": "4848a986-778f-4107-ba3f-e24407b09584" }
                ],
                "advanced_scheduling": {
                "Frequency": "weekly",
                "RepeatsEvery": 1,
                "StartDate": "2025-09-02",
                "StartTime": "18:57:21",
                "timeZone": "Asia/Calcutta",
                "dateFormat": "DD/MM/YYYY hh:mm A",
                "ends": "on",
                "DaysofWeek": [],
                "EndDate": "2025-09-02",
                "EndTime": "19:12:21"
                },
                "schedule_interval": "57 18 * * 0",
                "engine_type": "spark",
                "notification": {
                "active": false,
                "type": "email",
                "details": { "to": null, "subject": null, "body": null }
                },
                "replace_connections": {}
            }
            }
            // ...more DAG objects...
        ],
        "page": 1,
        "per_page": 10,
        "total_records": 10
        }
        ```

        **Response Fields:**

        **Top-level:**
        * `dags` (array): List of DAG definition objects for the user.
        * `page` (int): Current page number.
        * `per_page` (int): Page size.
        * `total_records` (int): Total DAGs available for the query.

        **DAG object (`dags[]`):**
        * **Core DAG Properties**
        * `dag_id` (string): Unique internal id of the DAG.
        * `dag_display_name` (string): Human-readable name shown in UI.
        * `description` (string|null): Optional description.
        * `owners` (string[]): Owners listed on the DAG.
        * `file_token` (string): Signed token that references the DAG file for UI download.
        * `fileloc` (string): Absolute path to DAG file.
        * **Execution Status & Control**
        * `is_active` (boolean): DAG registered/active.
        * `is_paused` (boolean): Scheduling paused flag.
        * `has_import_errors` (boolean): Parse/import errors present.
        * `has_task_concurrency_limits` (boolean): Per-task concurrency limits configured.
        * `last_parsed_time` (ISO-8601 string): Last scheduler parse.
        * `max_active_runs` (int) / `max_active_tasks` (int): Concurrency limits.
        * `max_consecutive_failed_dag_runs` (int): Auto-pause threshold.
        * **Scheduling Information**
        * `schedule_interval` (object): Timetable descriptor.
            * `__type` (string): e.g., `CronExpression`.
            * `value` (string): Cron expression.
        * `cron_expression` (string): Cron form of the schedule (mirror of `schedule_interval.value`).
        * `timetable_description` (string): Human-readable schedule.
        * `next_dagrun` / `next_dagrun_create_after` / `next_dagrun_data_interval_start` / `next_dagrun_data_interval_end` (string|null): Upcoming run info.
        * `schedule_name` (string): User-defined label for this schedule.
        * `starts_on` (ISO-8601 string): Schedule activation timestamp.
        * `schedule_id` (string): Internal schedule identifier.
        * `meta_schedule_version` (int): Version of the schedule metadata schema/config.2 for new schedule 1 for old schedules.  
        * **Job Configuration**
        * `job_name` (string): Friendly job name.
        * `local` (boolean): Runs on local infra when true.
        * `engine_type` (string): Processing engine (e.g., `spark`, `dlt`).
        * **Tags**
        * `tags[].name` (string): Annotative tags such as `engine_type:spark`, `schedule_name:Test`.
        * **Job Details (`job_details`)**
        * `configuration` (array): Engine-specific settings.
        * `files_list` (array): Input sources (files/tables/connections).
        * `export_files_list` (array): Artifacts exported after processing.
        * `destination` (array): Output targets for processed data.
        * `advanced_scheduling` (object): High-level schedule builder fields:
            * `Frequency` (string): daily/weekly/monthly/yearly.
            * `RepeatsEvery` (int): Interval multiplier.
            * `StartDate`/`StartTime` (string): Start boundary.
            * `EndDate`/`EndTime` (string): End boundary.
            * `timeZone` (string): IANA tz.
            * `DaysofWeek` (array): For weekly schedules.
            * `dateFormat` (string): Display format used in UI.
            * `ends` (string): e.g., `on`, `never`.
        * `schedule_interval` (string): Cron expression (string form).
        * `notification` (object): Delivery config for alerts.
            * `active` (boolean), `type` (string), `details.to|subject|body`.
        * `replace_connections` (object): Map for connection alias replacement.

        **Use Cases & Business Applications:**
        * Monitor health/status of automated data workflows.
        * Verify source/destination mappings and schedules.
        * Audit and inventory all scheduled jobs for a user.
        """
        
        try:
            data=request.get_json()
            user_id=data["user_id"]
            if self["_id"] != user_id:
                logger.error(f"Payload user id {user_id} is not same as token user id {self['_id']}")
                raise ValueError("Invalid user id in payload")
            resp = AirflowAPI().get_dag_runs(data)
            return resp

        except Exception as e:
            logger.error(f"Failed to return list of runs {e}")
            return {
                "success": False,
                "message": str(e)
            }, 404

        
@airflow_scheduling_api.route('/dag_search_filters/<string:user_id>')
class DagSearchFilters(Resource):
    """
    Resource for getting all the tags from DAGs.

    This class provides an endpoint for fetching all the tags of Directed Acyclic Graphs (DAGs) in Airflow.
    It is used for filtering job names and schedule names of DAGs.
    """
    @token_required
    @rest_api.doc(params={
        'user_id': {'description': 'Unique identifier of the user','type': 'string','required': True,'in': 'query'}
    })
    def get(self, current_user, user_id):
        """
        Get the schedule names and job names from all the schedules of a specific user.
        This endpoint allows user to retrieve schedule names and job names from all the schedules created by the user using `user_id`.
        
        **URL Parameter:**
        * **user_id** (`str`): Unique identifier of the user.

        **Returns:**
        * **success** (`bool`): Indicates if the schedule names and job names retrieval was successful.
        * **dag_search_filters** (`dict`): Contains the available filters based on the user's schedules. Includes:
            - **schedule_names** (`List[str]`): List of schedule names associated with the user's DAGs.
            - **job_names** (`List[str]`): List of job names defined within the user's DAGs.
        * **message** (`str`): Descriptive message about the operation result.
        """
        try:
            resp = AirflowAPI().get_dag_search_filters(user_id)
            return resp

        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500

@airflow_scheduling_api.route('/schedule')
class Schedule(Resource):
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('SchedulePatchModel', {
        "schedule_id": fields.String(required=True,description="Identifier of the schedule to edit",example="68cd0106abb6f3801332cee5"),
        "configurations": fields.Raw(description="Engine-specific settings",example={}),
        "schedule_interval": fields.String(description='e.g. "once" | "weekly" | "cron" | cron string',example="weekly"),
        "job_details": fields.Raw(description="Inline job details (only top-level, no extra models)",example={"files_list": []}),
        "schedule_name": fields.String(description="Human-friendly schedule name",example="Test"),
        "engine_type": fields.String(description='Processing engine (optional): "spark" or "dlt"',example="spark"),
        "replace_connections": fields.Raw(description="Connection alias replacements",example={}),
        "notification": fields.Raw(description='Notification config',example={"active": False,"type": "email","details": {"to": None, "subject": None, "body": None}}),
        "advanced_scheduling": fields.Raw(description="Builder-style schedule config",
            example={
                "Frequency": "weekly",
                "RepeatsEvery": 1,
                "StartDate": "2025-09-19",
                "StartTime": "12:51:02",
                "timeZone": "Asia/Calcutta",
                "dateFormat": "DD/MM/YYYY hh:mm A",
                "ends": "on",
                "DaysofWeek": ["Wednesday"],
                "EndDate": "2025-09-19",
                "EndTime": "13:06:02"
            }
        )
    }), validate=False)
    def patch(self, _):
        """
        Edit information for a schedule

        Endpoint that updates one or more mutable fields of an existing schedule.

        ### Sample Request Body

        **Change schedule timing** (returns regenerated cron)
        ```json
        {
            "schedule_id": "68cd0106abb6f3801332cee5",
            "configurations": {},
            "schedule_interval": "weekly",
            "job_details": { "files_list": [] },
            "schedule_name": "Test",
            "engine_type": "spark",
            "replace_connections": {},
            "notification": {
                "active": false,
                "type": "email",
                "details": { "to": null, "subject": null, "body": null }
            },
            "advanced_scheduling": {
                "Frequency": "weekly",
                "RepeatsEvery": 1,
                "StartDate": "2025-09-19",
                "StartTime": "12:51:02",
                "timeZone": "Asia/Calcutta",
                "dateFormat": "DD/MM/YYYY hh:mm A",
                "ends": "on",
                "DaysofWeek": ["Wednesday"],
                "EndDate": "2025-09-19",
                "EndTime": "13:06:02"
            }
            }
        ```
        ### Request Parameters:

        * `schedule_id` (`string`): Identifier of the schedule to edit.
        * `schedule_name` (`string`)
        * `schedule_interval` (`string | object`): User choice (e.g., `"once"` / `"weekly"` / `"cron"`) or a structured object your generator accepts.
        * `advanced_scheduling` (`object`): Builder-style schedule config (Frequency, RepeatsEvery, StartDate/Time, EndDate/Time, DaysofWeek, timeZone, etc.).
        * `configurations` (`object`): Engine-specific settings (passed through to DAG conf).
        * `replace_connections` (`object`): Map of connection alias replacements.
        * `notification` (`object`): `{ "active": bool, "type": "email", "details": { "to": "...", "subject": "...", "body": "..." } }`
        * `export_files_list` (`array`): Files to export after job completes.
        * `type` (`string`): Source/destination type (e.g., `"localstorage"`).
        * `engine_type` (`string`): **`spark`** or **`dlt`**.
        * `execution_type` (`string`): **`pipeline`** or **`code`**.
        * `meta_schedule_version` (`number`): Only used when upgrading to new schedule.

        **Cron regeneration**
        * If you change **`schedule_interval`** or **`advanced_scheduling`**, the server computes a new cron and returns it as **`cron_expression`** in the response.
      
        ### Sample Response (Success – 200)

        ```json
        {
        "success": true,
        "msg": "Successfully updated Schedule",
        "cron_expression": "51 12 * * 3"
        }
        ```
        """
        try:
            data = request.get_json()
            schedule_id = data.get("schedule_id", None)
            if schedule_id is None:
                raise ValueError("schedule_id is required field")
            
            data.pop("schedule_id")
            
            with client._Database__client.start_session() as session:
                resp = session.with_transaction(
                    lambda s:AirflowAPI(session).edit_schedule(schedule_id, data, self["_id"]),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )
                return resp
                
        except Exception as e:
            logger.error(f"Failed to update schedule {e}")
            return {
                "success": False,
                "message": str(e)
            }, 500
  
@airflow_scheduling_api.route('/dag/info/<string:job_id>')    
class DAGInfo(Resource):
    """
    Resource for getting detailed information about a specific DAG.

    This class offers an endpoint for fetching detailed information about a Directed Acyclic Graph (DAG) in Airflow,
    identified by its job ID. It's useful for obtaining specific details such as configuration, schedule, and current status of a particular DAG.
    """
    @token_required
    def get(self, current_user, job_id):
        """
            Retrieve comprehensive DAG information with execution history and task details

            This endpoint provides complete details about a specific Directed Acyclic Graph (DAG) including basic configuration, execution history (DAG runs), and individual task definitions.

            This comprehensive view enables deep analysis of data pipeline structure, performance, and execution patterns.

            Response Type - JSON Formatted String that contains detailed information about the specified DAG or an error message.

            ## Path Parameter:

            **job_id** (`str`): Unique identifier of the DAG/job to retrieve detailed information for.

            ## Example Request:

            ```
            GET /dag/info/68b91f9f14db60086fc2883
            ```
            **Sample Response (Success - 200):**
            ```json
            {
            "basic_info": {
                "dag_display_name": "68b91f9f14db60086fc2883",
                "dag_id": "68b91f9f14db60086fc2883",
                "default_view": "grid",
                "file_token": "<FILE_TOKEN_PLACEHOLDER>",
                "fileloc": "/airflow/dags/68b91f9f14db60086fc2883.py",
                "has_import_errors": false,
                "is_active": true,
                "is_paused": true,
                "last_parsed_time": "2025-09-19T11:49:56.315716+05:30",
                "max_active_runs": 16,
                "max_active_tasks": 16,
                "owners": ["airflow"],
                "schedule_interval": { "__type": "CronExpression", "value": "56 10 * * 0" },
                "tags": [
                {"name": "local:True"},
                {"name": "schedule_name:Test"},
                {"name": "job_name:Job 174"},
                {"name": "engine_type:spark"},
                {"name": "user_id:67c147a17004e4c8aaf4d2"}
                ],
                "timetable_description": "At 10:56, only on Sunday",
                "local": true,
                "job_name": "Job 174"
            },
            "dag_runs": {
                "dag_runs": [],
                "page": 1,
                "per_page": 10,
                "total_entries": 0
            },
            "tasks": {
                "tasks": [
                {
                    "task_id": "get_run_id",
                    "operator_name": "PythonOperator",
                    "downstream_task_ids": ["submit_spark_app"],
                    "start_date": "2025-09-04T10:56:38+05:30",
                    "end_date": "2025-09-04T11:11:38+05:30",
                    "retries": 0.0,
                    "retry_delay": { "__type": "TimeDelta", "days": 0, "seconds": 300, "microseconds": 0 },
                    "trigger_rule": "all_success",
                    "ui_color": "#ffefeb"
                },
                {
                    "task_id": "submit_spark_app",
                    "operator_name": "SparkSubmitOperator",
                    "downstream_task_ids": [],
                    "start_date": "2025-09-04T10:56:38+05:30",
                    "end_date": "2025-09-04T11:11:38+05:30",
                    "retries": 0.0,
                    "retry_delay": { "__type": "TimeDelta", "days": 0, "seconds": 300, "microseconds": 0 },
                    "trigger_rule": "all_success",
                    "ui_color": "#FF9933"
                }
                ],
                "total_entries": 2
            }
            }
            ```

            ### Field-by-field explanations

            **Top-level**
            - `basic_info` (object): High-level metadata describing the DAG definition.
            - `dag_runs` (object): Pagination block for historical/available DAG runs.
            - `tasks` (object): Definition-time metadata for tasks within the DAG.

            **basic_info (object)**
            - `dag_display_name` (string): Human-friendly identifier shown in the UI (same as `dag_id`).
            - `dag_id` (string): Unique DAG identifier used internally by Airflow.
            - `default_view` (string): Default UI tab to open for the DAG (e.g., `grid`, `graph`).
            - `description` (string|null): Free-text description set on the DAG.
            - `file_token` (string): Signed token referencing the DAG file path for downloads in the UI.
            - `fileloc` (string): Absolute path to the Python file defining the DAG.
            - `has_import_errors` (boolean): Whether import errors were detected when parsing the DAG.
            - `has_task_concurrency_limits` (boolean): True if per-task concurrency limits are configured.
            - `is_active` (boolean): True if the DAG is considered active (registered and parseable).
            - `is_paused` (boolean): True if the DAG is paused (won’t be scheduled automatically).
            - `is_subdag` (boolean): True if this DAG is a sub-DAG (legacy).
            - `last_expired` (string|null): Last time tasks/runs were auto-expired (if enabled).
            - `last_parsed_time` (string, ISO-8601): Timestamp when the scheduler last parsed the DAG file.
            - `last_pickled` (string|null): When the DAG was last serialized/pickled (legacy).
            - `max_active_runs` (integer): Max concurrent active runs allowed for this DAG.
            - `max_active_tasks` (integer): Max concurrent active tasks allowed across this DAG.
            - `max_consecutive_failed_dag_runs` (integer): Failure threshold for backfill/scheduler features (if set).
            - `next_dagrun` (string|null): Next scheduled run execution date (if any).
            - `next_dagrun_create_after` (string|null): Next time the scheduler will create a run.
            - `next_dagrun_data_interval_start` / `next_dagrun_data_interval_end` (string|null): Data interval boundaries for the next run (timetables).
            - `owners` (string[]): Owners (emails/usernames) listed on the DAG.
            - `pickle_id` (string|null): Serialized DAG id (legacy serialization).
            - `root_dag_id` (string|null): Root DAG id when using sub-DAGs (legacy).
            - `schedule_interval` (object): Scheduling rule.
            - `__type` (string): Type discriminator (e.g., `CronExpression`).
            - `value` (string): Cron expression or humanized schedule definition.
            - `scheduler_lock` (string|null): Internal scheduler lock state (if applicable).
            - `tags` (array of objects): Arbitrary tags attached to the DAG.
            - `name` (string): Tag value (e.g., `engine_type:spark`, `job_name:Job 174`).
            - `timetable_description` (string): Human-readable schedule, derived from timetable/cron.
            - `local` (boolean): Custom flag in your payload indicating local environment context.
            - `job_name` (string): Custom label for the job associated with this DAG.

            **dag_runs (object)**
            - `dag_runs` (array): List of DAG run objects (empty in your sample).
            - `page` (integer): Current page number.
            - `per_page` (integer): Page size (runs per page).
            - `total_entries` (integer): Total count of DAG runs available.

            **tasks (object)**
            - `tasks` (array): Array of task definitions present in the DAG.
            - `class_ref` (object): Operator class reference.
                - `class_name` (string): Operator class (e.g., `PythonOperator`, `SparkSubmitOperator`).
                - `module_path` (string): Python import path for the operator.
            - `depends_on_past` (boolean): If true, each task instance depends on previous run’s instance.
            - `downstream_task_ids` (string[]): Task ids that depend on this task.
            - `end_date` (string, ISO-8601): Task-level end boundary (optional/configured).
            - `execution_timeout` (object|null): Timeout config for task execution.
            - `extra_links` (array): Extra clickable links exposed by the operator in the UI.
            - `is_mapped` (boolean): True if task is dynamically mapped (Task Mapping feature).
            - `operator_name` (string): Short operator name shown in the UI.
            - `owner` (string): The task owner.
            - `params` (object): Runtime parameters available to the task.
            - `pool` (string): Name of the pool used to limit concurrency.
            - `pool_slots` (number): Number of slots this task consumes from the pool.
            - `priority_weight` (number): Scheduler priority weight.
            - `queue` (string): Celery/Kubernetes queue name (executor-dependent).
            - `retries` (number): Number of retries allowed on failure.
            - `retry_delay` (object): Delay between retries.
                - `__type` (string): Usually `TimeDelta`.
                - `days` (integer), `seconds` (integer), `microseconds` (integer): Components of delay.
            - `retry_exponential_backoff` (boolean): Use exponential backoff between retries.
            - `start_date` (string, ISO-8601): Task-level start boundary (optional/configured).
            - `task_display_name` (string): UI-friendly display label for the task.
            - `task_id` (string): Unique id of the task within the DAG.
            - `template_fields` (string[]): Fields that support Jinja templating for this operator.
            - `trigger_rule` (string): Rule to trigger this task (e.g., `all_success`, `all_done`).
            - `ui_color` (string, hex): Background color for task node in UI.
            - `ui_fgcolor` (string, hex): Foreground (text) color for task node in UI.
            - `wait_for_downstream` (boolean): If true, waits for downstream in previous runs before executing.
            - `weight_rule` (string): Rule for calculating priority weight (`downstream`, `upstream`, `absolute`).


            ## Response Structure Overview:

            The response is organized into three main sections providing comprehensive DAG analysis:

            ### 1. Basic Info Section:
            Contains fundamental DAG configuration and metadata

            ### 2. DAG Runs Section:
            Historical execution data showing past and current runs

            ### 3. Tasks Section:
            Individual task definitions and their execution parameters

            ## Use Cases and Applications:

            ### Pipeline Analysis and Optimization:
            * Analyze task dependencies and execution flow
            * Identify bottlenecks through task execution times
            * Optimize resource allocation using pool and priority settings
            * Review retry strategies and failure handling

            ### Execution Monitoring:
            * Track DAG run history and success rates
            * Monitor data processing windows and intervals
            * Analyze execution patterns and performance trends
        """

        try:
            query_params = request.args.to_dict()
            resp = AirflowAPI().get_dag_info(job_id, query_params)
            return resp

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }, 404


@airflow_scheduling_api.route('/airflow/stream_log')
class DAGStreamLog(Resource):
    """
    Resource for retrieving logs of a specific DAG.

    This class offers an endpoint for accessing the log details of a Directed Acyclic Graph (DAG) in Airflow,
    identified by its job ID. It's particularly useful for debugging and monitoring purposes, allowing users
    to track the execution and identify any issues within a specific DAG run.
    """
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGStreamLogModel', {
        "job_id": fields.String(example="689dafa85fb83a6335abd3d5", description="Unique identifier of the job/DAG to retrieve logs for", required=True),
        "dag_run_id": fields.String(example="manual__2025-08-14T09:43:29.281819+00:00",description="Specific DAG run ID to stream logs from",required=True),
        "engine_type": fields.String(example="spark", description="Processing engine type for the job",required=False,enum=["spark", "dlt", "local"])
    }), validate=False)
    @Logger.generate
    def post(self, current_user):
        """
        Stream DAG execution logs
        
        This endpoint provides real-time streaming access to execution logs for specific DAG runs, essential for monitoring, debugging, and troubleshooting data pipeline executions.

        **Request Body (JSON):**

        ```json
        {
            "job_id": "689dafa85fb83a6335abd3d5",
            "dag_run_id": "manual__2025-08-14T09:43:29.281819+00:00",
            "engine_type": "spark"
        }
        ```

        **Request Parameters:**
        * **job_id** (`str`): Unique identifier of the job/DAG to retrieve logs for
        * **dag_run_id** (`str`): Specific DAG run identifier for targeted log streaming
        * **engine_type** (`str`, optional): Processing engine type - "spark", "dlt" (default: "spark")

        **Response (Success – 200, `text/event-stream`):**
        - The response is a **Server-Sent Events** stream. Each message is delivered as lines:
          ```
          data: <log text chunk>\n
          ```
        - The stream starts with:
          ```
          data: ----Streaming logs for the run----\n
          ```
        - When the task completes (detected by `Marking task as SUCCESS/FAILED`), the server emits:
          ```
          event: finished\n
          data: -----End of log streaming----\n
          ```
          then closes the connection.

        **Response Example :**
        ```
        data: ----Streaming logs for the run----\n
        data: [2025-09-19T12:46:58.398+0530] INFO - Executing <Task(SparkSubmitOperator): run_now_job_task>...\n
        data: [2025-09-19T12:47:24.340+0530] INFO - Marking task as SUCCESS.\n
        event: finished\n
        data: -----End of log streaming----\n
        ```

        **Use Cases:**
        * **Real-time Monitoring**: Watch job execution progress live
        * **Debugging**: Identify and troubleshoot execution failures
        * **Performance Analysis**: Monitor resource usage and optimization opportunities
        * **Compliance**: Track data processing activities for audit purposes
        * **Alert Integration**: Monitor for specific error patterns or conditions

        """
        try:
            req_data = request.get_json()
            logger.info(req_data)
            job_id=req_data.get("job_id", "")
            dag_run_id= req_data.get("dag_run_id", None)
            engine_type = req_data.get("engine_type", "spark")
            if not dag_run_id:
                return {
                    "sucess": False,
                    "message": "Required parameter `dag_run_id` is missing"
                }, 400

            return AirflowAPI(None).stream_dag_log(job_id, dag_run_id,engine_type)

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }, 404


@airflow_scheduling_api.route('/airflow/log')
class DAGLog(Resource):
    """
    Resource for retrieving logs of a specific DAG.

    This class offers an endpoint for accessing the log details of a Directed Acyclic Graph (DAG) in Airflow,
    identified by its job ID. It's particularly useful for debugging and monitoring purposes, allowing users
    to track the execution and identify any issues within a specific DAG run.
    """
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGLogModel', {
        "job_id": fields.String(example="689d89ef71ab1f6c41f2574a", description="Unique identifier of the job/DAG to retrieve logs",required=True),
        "dag_run_id": fields.String(example="c0d98cbb-3991-4051-99e0-3bfd2baba1e8", description="Specific DAG run ID to fetch logs from",required=True),
        "engine_type": fields.String(example="spark", description="Engine type for the job",required=False,enum=["spark", "dlt"])
    }), validate=False)
    @Logger.generate
    def post(self, current_user):
        """
        Retrieve DAG execution logs
        
        This endpoint fetches complete execution logs for specific DAG runs, providing detailed information about task execution, Spark operations, and system activities for debugging and monitoring purposes.

        **Sample Request Body (JSON):**

        ```json
        {
            "job_id": "689d89ef71ab1f6c41f2574a",
            "dag_run_id": "c0d98cbb-3991-4051-99e0-3bfd2baba1e8",
            "engine_type": "spark"
        }
        ```

        **Request Parameters:**
        * **job_id** (`str`): Unique identifier of the job/DAG to retrieve logs for
        * **dag_run_id** (`str`): Specific DAG run identifier for targeted log retrieval
        * **engine_type** (`str`, optional): Processing engine type - "spark", "dlt" (default: "spark")


        **Response (Success - 200):**

        Returns complete log content as text, including:
        * **Airflow Task Execution**: Task lifecycle, dependencies, and execution status
        * **System Information**: Container details, resource usage, and environment variables
        * **Error Details**: Exception traces and failure information when applicable

        **Use Cases:**
        * **Debugging**: Identify root causes of job failures
        * **Performance Analysis**: Monitor execution times and resource usage
        * **Data Validation**: Verify data processing operations and results
        * **System Monitoring**: Track infrastructure health and capacity
        * **Audit Trail**: Maintain complete record of data processing activities
        """
        try:
            req_data = request.get_json()
            logger.info(req_data)
            job_id=req_data["job_id"]
            dag_run_id= req_data["dag_run_id"]  
            engine_type = req_data.get("engine_type", "spark")
            resp, status = AirflowAPI().get_dag_log(job_id,dag_run_id,engine_type)
            return resp, status

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }, 404

@llm_code_generation_api.route('/completion')
class LangchainCompletionAPI(Resource):
    
    @token_required
    @llm_code_generation_api.expect(rest_api.model('LangchainCompletionModel', {
        "input_text": fields.String(example="add a column abc", description="Natural language instruction for data operation",required=True),
        "chat_id": fields.String(example="689d950aa0aa07bf10527337", description="Chat session ID for conversation context",required=True),
        "user_id": fields.String(example="684aaaa4ae3f96339c3a4c12", description="User ID for the request",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Process natural language data operations using LLM
        
        Converts natural language instructions into executable data operations using Large Language Models through LangChain framework.

        **Request Body (JSON):**

        ```json
        {
            "input_text": "add a column abc",
            "chat_id": "689d950aa0aa07bf10527337",
            "user_id": "684aaaa4ae3f96339c3a4c12"
        }
        ```

        **Request Parameters:**
        * **input_text** (`str`): Natural language instruction for data operation
        * **chat_id** (`str`): Chat session ID for conversation context
        * **user_id** (`str`): User identifier for tracking

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "event": {
                "user_id": "684aaaa4ae3f96339c3a4c12",
                "chat_id": "689d950aa0aa07bf10527337",
                "messages": [
                    {
                        "event": "bot",
                        "message_id": "835bf561-df66-4cd4-9e77-af20d3ce0021",
                        "message": "**Task:** Adding a new column named 'abc' to the dataset.\\n\\n**Result:** `Successfully added column(s) abc with default value None.`",
                        "timestamp": 1755157792.514984,
                        "export": false,
                        "stage": "final",
                        "details": {
                            "refresh": true
                        }
                    }
                ]
            }
        }
        ```

        **Returns:**
        * **success** (`bool`): Processing success status
        * **event** (`object`): Conversation event with results and message history

        **Use Cases:**
        * Interactive data exploration with natural language
        * Business user-friendly data operations
        * Rapid data transformation prototyping
        """
        try:
            data = request.get_json()
            input_text = data['input_text']
            user_id = data['user_id']
            chat_id = data['chat_id']
            message_id = str(uuid.uuid4())
            dt = datetime.now(timezone.utc) 
            utc_time = dt.replace(tzinfo=timezone.utc) 
            timestamp = utc_time.timestamp() 
            data_to_insert = {
                "user_id": user_id,
                "chat_id": chat_id,
                "messages":[{ "event" : "user","message_id" : message_id,
                "message": input_text,
                "timestamp": timestamp,
                "stage" : "initial",
                "details":{}}]
            }
             # Check if a document with the given user_id and chat_id already exists
            
            with client._Database__client.start_session() as session:
                session.with_transaction(
                    lambda s:MongoLangchain(MongoConnector().client,"langchain",session).create_or_update(data = data_to_insert),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            session.end_session()
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s:LangchainService(session).processs(input_text,user_id,chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp
    
        except LangchainServiceException as e:
            # Handle custom service exceptions with proper error response and status code
            logger.error(f"LangchainServiceException: {e.error_response}")
            return e.error_response, e.status_code

        except Exception as e:
            return {
                "success": False,
                "msg": str(e)
            }, 404


@data_connections_api.route('/get_columns')
class GetColumns(Resource):

    @token_required
    @data_connections_api.expect(rest_api.model('GetColumnsModel', {
        "source": fields.String(example="database", description="Data source type (database, flat_files, s3)",required=True,enum=["database", "flat_files", "s3"]),
        "connection_id": fields.String(example="684aad3e20ef26522ff885f7", description="Unique identifier of the connection",required=True),
        "catalog": fields.String(example="public.actor", description="Table/file specification (schema.table for database, file path for others)",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Get column information from data sources
        
        This endpoint retrieves column names and metadata from databases, files, and cloud storage for schema discovery and data pipeline development.

        **Sample Request Body (JSON):**

        ```json
        {
            "source": "database",
            "connection_id": "684aad3e20ef26522ff885f7",
            "catalog": "public.actor"
        }
        ```

        **Request Parameters:**
        * **source** (`str`): Data source type - "database", "flat_files", or "s3"
        * **connection_id** (`str`): Unique identifier of the established connection
        * **catalog** (`str`): Specific table/file path:
          * Database: "schema.table" (e.g., "public.actor")
          * Files: Sheet name or file identifier
          * S3: Full object path (e.g., "data/sales_2024.csv")

        **Sample Response (Success - 200):**

        ```json
        {
            "success": true,
            "columns": [
                "actor_id",
                "first_name",
                "last_name",
                "last_update"
            ],
            "msg": "Columns fetched successfully from database."
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if column retrieval was successful
        * **columns** (`array`): List of column names in the data source
        * **msg** (`str`): Operation result message

        **Use Cases:**
        * Schema discovery for new data sources
        """
        try:
            req_data=request.json
            resp = ListCatalogsService().list_columns(req_data)
            return resp

        except:
            return {
                "success": False,
                "text": "The file not found"
            }, 404

@pipeline_workflows_api.route('/run_pipeline')
class ReRunPipeline(Resource):
    @token_required
    @pipeline_workflows_api.expect(rest_api.model('RunPipelineModel', {
        "mode": fields.String(example="yaml", description="Execution mode for the pipeline",required=True,enum=["yaml"]),
        "dry_run": fields.Boolean(example=True, description="Whether to run in preview mode without making changes",required=False),
        "chat_id": fields.String(example="689db69b15c12b6c3191f672", description="Chat session ID where the pipeline should execute",required=True),
        "details": fields.Raw(example={"value": "-   function: read_files\n    id: 199d8798-5905-4d07-b654-9559fc42d404\n    output:\n        dataframe_alias: demo\n        source_id: 346efd63-8ba4-414c-b45a-96d94a480c95\n    parameters:\n        file_id: 738706f1-a881-4e1b-8fa8-91c71239d1c7\n        file_name: demo\n    status: PASS\n"
        }, description="Pipeline configuration details in YAML or Python format", required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Execute data processing pipeline
        
        This endpoint executes data processing pipelines in YAML mode, with support for dry-run testing to preview results without making permanent changes.

        **Request Body (JSON):**

        ```json
        {
            "mode": "yaml",
            "dry_run": true,
            "chat_id": "chat_id_123",
            "details": {
                "value": "-   function: read_files\\n    id: 199d8798-5905-4d07-b654-9559fc42d404\\n    output:\\n        dataframe_alias: demo\\n        source_id: 346efd63-8ba4-414c-b45a-96d94a480c95\\n    parameters:\\n        file_id: 738706f1-a881-4e1b-8fa8-91c71239d1c7\\n        file_name: demo\\n    status: PASS\\n"
            }
        }
        ```

        **Request Parameters:**
        * **mode** (`str`): Execution mode - "yaml" for declarative pipelines or "python" for custom scripts
        * **dry_run** (`bool`, optional): If true, previews results without making permanent changes (default: false)
        * **chat_id** (`str`): Chat session ID where the pipeline should execute
        * **details** (`object`): Pipeline configuration containing:
          * **value** (`str`): YAML pipeline definition or Python code for execution

        **Response (Success - Dry Run - 200):**

        ```json
        {
            "success": true,
            "message": "Successfully Ran Pipeline"
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if pipeline execution was successful
        * **message** (`str`): Execution result message

        **Use Cases:**
        * **Pipeline Development**: Test and refine data processing workflows
        * **Business Logic Implementation**: Convert requirements to executable pipelines
        * **Automated Processing**: Execute predefined data transformation workflows
        * **Educational Tool**: Learn data processing through declarative configuration
        """
        try:
            req_data=request.json
            chat_id = req_data.get("chat_id")
            dry_run = req_data.get("dry_run", False)
            pipeline = req_data.get("details", {}).get("value", '[]')
            
            if pipeline is None or pipeline=='':
                pipeline='[]'
            if not dry_run:
                pipeline=None
            executiontype=req_data.get("mode")
            if executiontype=="yaml":
                # In dry_run mode: preview data is returned and changes are not written to database
                if dry_run:
                    with client._Database__client.start_session() as session:
                        success, message=session.with_transaction(
                            lambda s:ReRunService(session).dry_run(chat_id, pipeline),
                            read_concern=ReadConcern("local"),
                            write_concern=wc_majority,
                            read_preference=ReadPreference.PRIMARY,
                        )
                    response = {"success":success, "message":message}
                else:
                    with client._Database__client.start_session() as session:
                        success, message, data =session.with_transaction(
                            lambda s:ReRunService(session).pipeline(chat_id, pipeline),
                            read_concern=ReadConcern("local"),
                            write_concern=wc_majority,
                            read_preference=ReadPreference.PRIMARY,
                        )
                    response = {"success":success, "message":message, "data": data}
                return response, 200
            elif executiontype=="python":
                 return {"success":success, "text":"Need to Implement"}, 200
            
            else:
                raise Exception("Invalid Type")
                

        except Exception as e:
            return {
                "success": False,
                "message": f"Unable to execute Error: {e}"
            }, 404


@export_download_api.route('/download_file')
class Download(Resource):
    """
    Downloads the exported file.
    """

    @token_required
    @export_download_api.expect(rest_api.model('DownloadFileModel', {
        "job_id": fields.String(example="689dafc15fb83a6335abd3d8", description="Unique identifier of the job/schedule that generated the file",required=True),
        "dag_run_id": fields.String(example="manual__2025-08-14T09:43:29.281819+00:00", description="DAG run ID that produced the output file",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Download job output file
        
        This endpoint allows users to download output files generated by specific job executions (DAG runs) using the job ID and DAG run ID.

        **Request Body (JSON):**

        ```json
        {
            "job_id": "689dafc15fb83a6335abd3d8",
            "dag_run_id": "manual__2025-08-14T09:43:29.281819+00:00"
        }
        ```

        **Request Parameters:**
        * **job_id** (`str`): Unique identifier of the scheduled job/workflow that generated the output
        * **dag_run_id** (`str`): Specific DAG run identifier that produced the file (includes execution timestamp)

        **Response (Success - 200):**
        
        Returns the actual CSV file content with download headers:
        * **Content-Type**: text/csv
        * **Content-Disposition**: attachment; filename="[dag_run_id].csv"
        * **File Content**: The processed data in CSV format

        **Use Cases:**
        * Download results from scheduled data processing jobs
        * Retrieve output from manual DAG executions
        * Access processed data for offline analysis
        * Export job results for sharing
        """
        try:
            _user_id = str(self['_id'])
            data=request.get_json()
            schedule_id=data["job_id"]
            run_id=data["dag_run_id"]
            
            path = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, _user_id, "output", schedule_id, run_id)
            
            logger.info(f"Looking for files in: {path}")
            files = os.listdir(path)
            logger.info(f"Files found: {files}")

            file_name = None
            for file in files:
                if file.startswith("part-"):
                    file_name = file
                    break

            # Check if any matching files were found
            if file_name:
                # Get the full path of the file
                full_path = os.path.join(path, file_name)
                
                # Detect file format from extension
                file_extension = os.path.splitext(file_name)[1].lower()
                logger.info(f"File found: {file_name}, Extension: {file_extension}")
                
                # Set MIME type and download name based on file extension
                if file_extension == '.xlsx':
                    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    download_name = f"{run_id}.xlsx"

                elif file_extension == '.json':
                    mimetype = "application/json"
                    download_name = f"{run_id}.json"
                    
                else:
                    # Default to CSV (including .csv files and unknown extensions)
                    mimetype = "text/csv"
                    download_name = f"{run_id}.csv"

                # Use the same send_file logic that works for CSV
                resp = send_file(os.path.abspath(full_path), download_name=download_name, as_attachment=True, mimetype=mimetype)
                return resp
            else:
                raise Exception("The file not found")
                
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {
                "success": False,
                "text": f"{e}"
            }, 404

@file_management_api.route('/rename_file_cache')
class RenameFileCache(Resource):
   @token_required
   @file_management_api.expect(rest_api.model('RenameFileCacheModel', {
        "source_id": fields.String(example="source_id_123", description="Unique identifier of the cached file to rename",required=True),
        "new_file_name": fields.String(example="new_file_name", description="New name for the cached file",required=True),
        "chat_id": fields.String(example="chat_id_123",  description="Chat session ID where the file is cached",required=True)
    }), validate=False)
   def post(self,current_user):
       """
        Rename cached file
        This endpoint allows users to rename a file that is currently cached within a specific chat session. This updates the file alias in the chat context without affecting the original file.
        
        **Request Body (JSON):**
        
        ```json
        {
            "source_id": "source_id_123",
            "new_file_name": "new_file_name",
            "chat_id": "chat-id_123"
        }
        ```
        
        **Request Parameters:**
        * **source_id** (`str`): Unique identifier of the cached file to rename.
        * **new_file_name** (`str`): New name/alias for the cached file within the chat context.
        * **chat_id** (`str`): Chat session ID where the file is currently cached.
        
        **Response (Success - 200):**
        
        ```json
        {
            "success": true,
            "message": "File renamed successfully."
        }
        ```
    
        **Returns:**
        * **success** (`bool`): Indicates if the file rename operation was successful.
        * **message** (`str`): Descriptive message about the operation result.
        
        """
       try:
            req_data = request.get_json()
            source_id = req_data.get("source_id")
            new_file_name = req_data.get("new_file_name")
            chat_id = req_data.get("chat_id")
            with client._Database__client.start_session() as session:
                resp=session.with_transaction(
                    lambda s: FileServiceCache(session).rename_file(source_id, new_file_name, chat_id),
                    read_concern=ReadConcern("local"),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,
                )   
            return resp
        #    response = FileServiceCache.rename_file(source_id, new_file_name)
        #    return response
       except ValueError as e:
           logger.error(str(e), exc_info=True)
           return {"success": False, "msg": str(e)}, 400
       except Exception as e:
           logger.error(f"Error: {e}", exc_info=True)
           return {"success": False, "msg": "Internal server error"}, 500

@file_management_api.route('/cwf')
class ChangeCWFFILE(Resource):
   @token_required
   @file_management_api.expect(rest_api.model('ChangeCWFModel', {
        "chat_id": fields.String(example="chat_id_123", 
                                description="Unique identifier of the chat session",
                                required=True),
        "source_id": fields.String(example="source_id_123", 
                                  description="Unique identifier of the file to set as current working file",
                                  required=True)
    }), validate=False)
   def post(self,current_user):
       """
        Change current working file
        This endpoint allows user to set a specific file as the current working file (CWF) for a chat session. The current working file is the primary file that will be used for data operations and analysis within the chat context.
        
        **Request Body (JSON):**
        
        ```json
        {
            "chat_id": "chat_id_123",
            "source_id": "source_id_123"
        }
        ```
        
        **Request Parameters:**
        * **chat_id** (`str`): Unique identifier of the chat session where the working file should be changed.
        * **source_id** (`str`): Unique identifier of the file to set as the current working file.
        
        **Example Response (Success):**
        
        ```json
        {
            "success": true,
            "msg": "2017 Order Data is the current working file."
        }
        ```
        
        **Returns:**
        * **success** (`bool`): Indicates if the current working file change was successful.
        * **msg** (`str`): Descriptive message about the operation result, including the name of the new current working file.
        
        **Current Working File (CWF) Functionality:**
        * Sets the primary file for data operations in a chat session
        * All subsequent data analysis commands will default to this file
        * Only one file can be the current working file per chat session
        * User must have access to both the chat session and the file
        * File must be already uploaded and accessible to the user
        
        **Use Cases:**
        * Switch between different datasets in the same chat session
        * Set initial working file when starting data analysis
        * Change focus from one dataset to another during analysis
        """
       try:
            req_data = request.get_json()
            source_id = req_data.get("source_id")
            chat_id = req_data.get("chat_id")
            user_id = req_data.get("user_id", str(self["_id"]))
            resp = ChangeCWF().current_working_file(chat_id, user_id, source_id) 
            return resp
       except Exception as e:
           return {"success": False, "msg": "Failed to Change, Please try changing it by chat."}, 500


@airflow_scheduling_api.route('/trigger_dag')
class DAGTrigger(Resource):
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGTriggerModel', {
        "dag_id": fields.String(example="68906c61b05bf6d4881145b2", description="Unique identifier of the DAG to trigger manually",required=True)
    }), validate=False)
    def post(self,current_user):
        """
        Manually trigger DAG execution

        This endpoint allows users to manually trigger the execution of a specific Directed Acyclic Graph (DAG) outside of its regular schedule. This is useful for testing, immediate data processing needs, or running ad-hoc data pipeline executions.

        Manual DAG triggering bypasses the normal scheduling mechanism and immediately queues a DAG for execution. This creates a new DAG run with a "manual" run type, allowing users to process data on-demand without waiting for the next scheduled execution.

        ### Request Body (JSON):

        ```json
        {
            "dag_id": "68906c61b05bf6d4881145b2"
        }
        ```

        ### Request Parameters:
        * **dag_id** (`str`): Unique identifier of the DAG to trigger. This must be an existing, active DAG that the user has permission to execute.

        ### Response (Success ):

        ```json
        {
            "success": true,
            "message": "DAG triggered successfully"
        }
        ```

        ### Returns:
        * **success** (`bool`): Indicates if the DAG trigger operation was successful.
        * **message** (`str`): Descriptive message about the operation result.
        * **text** (`str`): Error message in case of failure.

        ### Prerequisites for Triggering:
        * **DAG Must Exist**: The specified dag_id must correspond to an existing DAG
        * **DAG Must Be Active**: The DAG's is_active flag must be true
        * **DAG Must Not Be Paused**: The DAG's is_paused flag must be false
        * **User Permissions**: User must have execution rights for the DAG
        * **Resource Availability**: Sufficient execution slots must be available
        """
        data = request.json
        try:
            resp = AirflowAPI().trigger_dag(data)
            return resp

        except Exception as e:
            return {
                "success": False,
                "text": str(e)
            }, 404

@airflow_scheduling_api.route('/get_dag_run_status')
class DAGRunStatus(Resource):
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('DAGRunStatusModel', {
        "dag_run_id": fields.String(example="manual__2025-08-14T09:43:29.281819+00:00", description="Specific DAG run ID to fetch state for", required=True),
        "dag_id": fields.String(example="68906c61b05bf6d4881145b2", description="DAG identifier. Optional, defaults to run_now_dag when omitted", required=False)
    }), validate=False)
    def post(self, current_user):
        """
        Get DAG run state for a specific run

        Accepts a DAG run identifier and optional DAG identifier; returns the state for that run.
        
        ### Request Body (JSON):

        ```json
        { "dag_run_id": "manual__2025-08-14T09:43:29.281819+00:00", "dag_id": "68906c61b05bf6d4881145b2" }
        ```

        ### Request Parameters:
        * **dag_run_id** (`str`): Specific DAG run identifier to fetch status for.
        * **dag_id** (`str`, optional): DAG identifier. If omitted, defaults to `run_now_dag`.

        ### Response (Success )

        ```json
        {
            "success": true, "dag_id": "run_now_dag", "dag_run_id": "manual__2025-08-14T09:43:29.281819+00:00", "state": "success"
        }
        ```

        ### Returns:
        * **success** (`bool`): Indicates if the DAG trigger operation was successful.
        * **dag_id** (`str`): Unique identifier of the DAG.
        * **dag_run_id** (`str`): run id of the DAG.
        * **state** (`str`): State of the DAG run. Can be one of "queued", "running", "success", "failed"
        * **message** (`str`): Descriptive message about the operation result. Returned in case of failure.
        """
        try:
            data = request.get_json()
            resp = AirflowAPI().get_dag_run_status(data)
            return resp
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@airflow_scheduling_api.route('/airflow/delete')         
class Airflow(Resource):
    @token_required
    @airflow_scheduling_api.expect(rest_api.model('AirflowScheduleDeleteModel', {
        "schedule_ids": fields.List(fields.String(), example=["689069abb05bf6d4881145ac"], description="Array of schedule IDs to be deleted",required=True)
    }), validate=False)
    def delete(self,current_user):
        """
        Delete multiple Airflow schedules

        Endpoint to delete an existing schedule based on the provided schedule ID and any errors encountered during the process.

        Schedule deletion permanently removes DAG definitions from Airflow, stopping all future executions and cleaning up associated metadata. This operation is irreversible and should be used carefully, typically when data pipelines are no longer needed or need to be completely rebuilt.

        ### Request Body (JSON):

        ```json
        {
            "schedule_ids": ["689069abb05bf6d4881145ac"]
        }
        ```

        ### Request Parameters:
        **schedule_ids** (`array`): List of schedule/DAG IDs to be deleted. Each ID should be a valid UUID string representing an existing schedule.

        ### Response (Success - 200):

        ```json
        {
            "success": [
                "689069abb05bf6d4881145ac"
            ],
            "errors": []
        }
        ```
        ### Returns:
        * **success** (`array`): List of schedule IDs that were successfully deleted.
        * **errors** (`array`): List of schedule IDs that failed to delete with error details.

        ### Use Cases and Applications:

        ### Development Lifecycle Management:
        * Remove obsolete or deprecated data pipelines
        * Clean up test and development schedules
        * Retire pipelines after business process changes
        * Consolidate duplicate or redundant workflows

        ### Prerequisites and Validation:

        ### Security Requirements:
        * **User Authentication**: Valid authentication token required
        * **Permission Validation**: User must have delete permissions for each schedule
        * **Ownership Verification**: Users can only delete their own schedules
        * **Access Control**: Role-based access controls enforced
        """
        try:
            payload = request.json  
            resp = AirflowAPI().delete_schedule(payload)
            return resp

        except Exception as e:
            return {
                "success": False,
                "text": str(e)
            }, 404

@llm_code_generation_api.route('/pyspark/generate')
class PySparkResource(Resource):
    @token_required
    @llm_code_generation_api.expect(rest_api.model('PySparkGenerateModel', {
        "user_text": fields.String(example="print(\"hello\")", description="Natural language instruction or code snippet for PySpark generation",required=True),
        "chat_id": fields.String(example="689d950aa0aa07bf10527337", description="Chat session ID for conversation context",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Generate PySpark code from natural language instructions
        
        This endpoint converts natural language instructions or code snippets into optimized PySpark code using AI-powered code generation.

        **Sample Request Body (JSON):**

        ```json
        {
            "user_text": "print(\"hello\")",
            "chat_id": "689d950aa0aa07bf10527337"
        }
        ```

        **Request Parameters:**
        * **user_text** (`str`): Natural language instruction or code snippet for PySpark code generation
        * **chat_id** (`str`): Chat session ID to maintain conversation context

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "code": generated_pyspark_code,
            "message": "Pyspark code generated successfully"
        }
        ```
        **Returns:**
        * **success** (`bool`): Indicates if code generation was successful
        * **code** (`str`): Generated PySpark code ready for execution
        * **message** (`str`): Confirmation message about the generation

        """
        try:
            req_data = request.get_json()
            user_text = req_data.get("user_text")
            chat_id = req_data.get("chat_id")
            user_id = str(self["_id"])
            
            data_to_insert = {
                "user_id": user_id,
                "chat_id": chat_id,
                "messages":[]
            }
             # Check if a document with the given user_id and chat_id already exists
            MongoLangchain(MongoConnector().client,"langchain", None).create_or_update(data = data_to_insert)
            resp = PySparkCodeGenerator(chat_id, None).invoke_chain(user_text)

            return resp
            
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500


@llm_code_generation_api.route('/pyspark/reset')
class PySparkResource(Resource):
    @token_required
    @llm_code_generation_api.expect(rest_api.model('PySparkResetModel', {
        "chat_id": fields.String(example="chat_id_123", description="Chat session ID to reset PySpark context for",required=True)
    }), validate=False)
    def post(self, current_user):
        """
        Reset PySpark code generation context
        
        This endpoint resets the PySpark code generation context for a specific chat session, clearing conversation history and reinitializing the LLM chain for fresh code generation.

        **Request Body (JSON):**

        ```json
        {
            "chat_id": "chat_id_123"
        }
        ```

        **Request Parameters:**
        * **chat_id** (`str`): Chat session ID where the PySpark context should be reset

        **Response (Success - 200):**

        ```json
        {
            "success": true,
            "message": "Reset Successful"
        }
        ```

        **Returns:**
        * **success** (`bool`): Indicates if the reset operation was successful
        * **message** (`str`): Confirmation message about the reset operation

        **Use Cases:**
        * Start fresh PySpark code generation 
        * Clear context when switching to different data processing tasks
        * Reset after completing a data analysis workflow
        * Initialize clean state for new team members or sessions
        """
        try:
            req_data = request.get_json()
            chat_id = req_data.get("chat_id")
            user_id = str(self["_id"])
            data_to_insert = {
                "user_id": user_id,
                "chat_id": chat_id,
                "messages":[]
            }
            MongoLangchain(MongoConnector().client,"langchain", None).create_or_update(data = data_to_insert)
            resp = PySparkCodeGenerator(chat_id, None).reset_chain()
            return resp
            
        except Exception as e: # pragma: no cover
            return {"success": False, "msg": str(e)}, 500


