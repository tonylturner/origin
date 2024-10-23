import os
import nltk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the path to /data/nltk directory using the NLTK_DATA environment variable from the .env file
nltk_data_path = os.path.abspath(os.getenv("NLTK_DATA", "./data/nltk"))

# Ensure the /data/nltk directory exists (relative to the project root)
os.makedirs(nltk_data_path, exist_ok=True)

# Clear existing paths in nltk's search path list to ensure only the correct paths are used
nltk.data.path.clear()
nltk.data.path.append(nltk_data_path)  # Add the correct path for NLTK data


# Function to check if a model exists in the specified path
def model_exists(model_name, base_path):
    try:
        nltk.data.find(model_name, paths=[base_path])
        return True
    except LookupError:
        return False


# Ensure the necessary models are downloaded to /data/nltk
def setup_nltk_data(force_download=False):
    models = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt": "punkt_tab",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger_eng",
        "chunkers/maxent_ne_chunker": "maxent_ne_chunker",
        "chunkers/maxent_ne_chunker": "maxent_ne_chunker_tab",
        "corpora/words": "words",
        "corpora/treebank": "treebank",
        "taggers/maxent_treebank_pos_tagger": "maxent_treebank_pos_tagger",
    }

    for model_path, model in models.items():
        if force_download or not model_exists(model_path, nltk_data_path):
            print(f"Downloading '{model}' to {nltk_data_path}...")
            nltk.download(model, download_dir=nltk_data_path)
        else:
            print(f"DEBUG: NLTK model '{model}' already installed.")


# Example usage of the function with a force update parameter
if __name__ == "__main__":
    from config.argument_parser import (
        parse_args,
    )  # Import argument parser for handling --update-nltk

    args = parse_args()
    force_download = getattr(
        args, "update_nltk", False
    )  # Check if --update-nltk was passed
    setup_nltk_data(force_download=force_download)

    # Print the paths being used by NLTK to verify the correct path is set
    print("NLTK paths being used:", nltk.data.path)
