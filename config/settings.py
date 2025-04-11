import os
from distutils.util import strtobool
from dotenv import load_dotenv

# Create .env file path.
#dotenv_path = os.path.join('..', '.env')

# Load file from the path.
load_dotenv()

EMAIL = os.getenv('EMAIL', None)
PASSWORD = os.getenv('PASSWORD', None)
MODELNAME = os.getenv('MODELNAME', None)
