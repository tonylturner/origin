import re
from sklearn.feature_extraction.text import CountVectorizer
import logging

class FeatureExtractor:
    def extract_code_patterns(self, text):
        variable_pattern = r"\b[a-zA-Z_]\w*\b"
        function_pattern = r"\bdef\s+\w+\b"
        variables = re.findall(variable_pattern, text)
        functions = re.findall(function_pattern, text)
        return {
            "variables": variables,
            "functions": functions,
            "doc_style": "pythonic" if "def " in text else "unknown",
        }

    def extract_ngrams(self, text, n=2):
        if not text or len(text.split()) < n:
            return []

        vectorizer = CountVectorizer(ngram_range=(n, n), analyzer="word", stop_words="english")

        try:
            X = vectorizer.fit_transform([text])
            return vectorizer.get_feature_names_out()
        except ValueError as e:
            logging.warning(f"Skipping n-grams extraction due to empty vocabulary: {e}")
            return []
