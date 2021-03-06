import os
from tempfile import mkdtemp
uploadFolderPath = os.path.abspath("") + "\\CodeJudge\\uploads"
if not os.path.exists(uploadFolderPath):
        os.makedirs(uploadFolderPath)
        
UPLOAD_FOLDER = uploadFolderPath
SECRET_KEY = "Test"

SQLALCHEMY_DATABASE_URI = 'sqlite:///database/database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# configure session to use filesystem (instead of signed cookies)
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"

MAX_CONTENT_LENGTH = 1 * 1024 * 1024
