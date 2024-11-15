import nltk

# Function to check if a model exists
def model_exists(model_name):
    try:
        nltk.data.find(model_name)
        return True
    except LookupError:
        return False

# Ensure the necessary models are downloaded
def setup_nltk_data(force_download=False):
    models = {
        "tokenizers/punkt": "punkt",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
        "chunkers/maxent_ne_chunker": "maxent_ne_chunker",
        "corpora/words": "words",
        "corpora/treebank": "treebank",
        "taggers/maxent_treebank_pos_tagger": "maxent_treebank_pos_tagger",
    }

    for model_path, model in models.items():
        if force_download or not model_exists(model_path):
            print(f"Downloading '{model}' to the default NLTK path...")
            nltk.download(model)
        else:
            print(f"DEBUG: NLTK model '{model}' already installed.")

# Example usage of the function with a force update parameter
if __name__ == "__main__":
    from config.argument_parser import parse_args  # Import argument parser for handling --update-nltk

    args = parse_args()
    force_download = getattr(args, "update_nltk", False)  # Check if --update-nltk was passed
    setup_nltk_data(force_download=force_download)

    # Print the paths being used by NLTK to verify the correct path is set
    print("NLTK paths being used:", nltk.data.path)
