import os
import nltk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the path to /data/nltk directory using the NLTK_DATA environment variable from the .env file
nltk_data_path = os.path.abspath(os.getenv('NLTK_DATA', './data/nltk'))

# Ensure the /data/nltk directory exists (relative to the project root)
os.makedirs(nltk_data_path, exist_ok=True)

# Clear existing paths in nltk's search path list to ensure only the correct paths are used
nltk.data.path.clear()
nltk.data.path.append(nltk_data_path)  # Add the correct path for NLTK data

# Ensure the necessary models are downloaded to /data/nltk
def setup_nltk_data(force_download=False):
    model = 'all'  # Using 'all' collection for now
    
    try:
        # Check if 'all' models are already downloaded
        if force_download:
            raise LookupError(f"Forcing download of {model}")
        nltk.data.find('tokenizers/punkt', paths=[nltk_data_path])  # As an example of existing models check
        print(f"DEBUG: NLTK model '{model}' already installed.")
    except LookupError:
        # Download the 'all' collection if not found or forced
        print(f"Downloading {model} model to {nltk_data_path}...")
        nltk.download(model, download_dir=nltk_data_path)

# Example usage of the function with a force update parameter
if __name__ == "__main__":
    from config.argument_parser import parse_args  # Import argument parser for handling --update-nltk
    
    args = parse_args()
    force_download = getattr(args, 'update_nltk', False)  # Check if --update-nltk was passed
    setup_nltk_data(force_download=force_download)

    # Print the paths being used by NLTK to verify the correct path is set
    print("NLTK paths being used:", nltk.data.path)
