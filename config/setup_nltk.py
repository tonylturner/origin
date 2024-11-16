import nltk
import logging


def model_exists(model_name):
    """
    Check if the specified NLTK model or resource is already available.

    Args:
        model_name (str): Path of the NLTK model/resource to check.

    Returns:
        bool: True if the model/resource exists, False otherwise.
    """
    try:
        nltk.data.find(model_name)
        return True
    except LookupError:
        return False


def setup_nltk_data(force_download=False):
    """
    Ensure all required NLTK data is installed. Optionally force re-download.

    Args:
        force_download (bool): If True, re-download all models even if they exist.
    """
    models = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
        "taggers/averaged_perceptron_tagger_eng": "averaged_perceptron_tagger_eng",
        "chunkers/maxent_ne_chunker": "maxent_ne_chunker",
        "chunkers/maxent_ne_chunker_tab": "maxent_ne_chunker_tab",
        "corpora/words": "words",
        "corpora/treebank": "treebank",
        "taggers/maxent_treebank_pos_tagger": "maxent_treebank_pos_tagger",
    }

    for model_path, model in models.items():
        if force_download or not model_exists(model_path):
            logging.info(f"Downloading NLTK model/resource: '{model}'...")
            try:
                nltk.download(model)
                logging.info(f"NLTK model/resource '{model}' downloaded successfully.")
            except Exception as e:
                logging.error(f"Failed to download NLTK model/resource '{model}': {e}")
        else:
            logging.debug(f"NLTK model/resource '{model}' is already installed.")

    # Validate all paths for debugging purposes
    logging.info("NLTK data validation complete.")
    logging.info("Current NLTK paths: %s", nltk.data.path)


if __name__ == "__main__":
    from config.argument_parser import parse_args  # Import argument parser for handling --update-nltk

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Parse command-line arguments
    args = parse_args()

    # Determine if models should be forcefully downloaded
    force_download = getattr(args, "update_nltk", False)

    # Setup NLTK data
    setup_nltk_data(force_download=force_download)

    # Print paths being used for further confirmation
    logging.info("NLTK paths being used: %s", nltk.data.path)
