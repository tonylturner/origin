from transformers import BertTokenizer, BertModel
import torch
import spacy
import re
from sklearn.feature_extraction.text import CountVectorizer
from langdetect import detect
import logging
from spacy.cli import download
from spacy.util import get_package_path


class LinguisticAnalysis:
    def __init__(self):
        # Required models for spaCy
        self.required_spacy_models = ["en_core_web_sm", "zh_core_web_sm"]
        self.ensure_spacy_models_installed()

        # Load pre-trained models
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased")
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_zh = spacy.load("zh_core_web_sm")

    def ensure_spacy_models_installed(self):
        """
        Ensure required spaCy models are installed. Download them if missing.
        """
        for model in self.required_spacy_models:
            try:
                # Check if the model is already installed
                get_package_path(model)
                logging.info(f"spaCy model '{model}' is already installed.")
            except OSError:
                # If not installed, download it
                logging.warning(f"spaCy model '{model}' not found. Downloading...")
                try:
                    download(model)
                    logging.info(f"spaCy model '{model}' downloaded successfully.")
                except Exception as e:
                    logging.error(f"Failed to download spaCy model '{model}': {e}")
                    raise

    def get_bert_embeddings(self, text):
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=128
        )
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze()

    def analyze_syntax(self, text):
        # Manually handle common phrases (e.g., "Initial commit")
        if text.lower() in ["initial commit", "first commit"]:
            language = "en"
        else:
            language = detect(text)

        logging.info(f"Detected language: {language}")

        # Load appropriate language model based on detected language
        if language == "zh":
            doc = self.nlp_zh(text)
        else:
            doc = self.nlp_en(text)

        syntax_features = {
            "POS_tags": [token.pos_ for token in doc],
            "Dependency_tags": [token.dep_ for token in doc],
            "Subject-Verb_Agreement": [],
            "Missing_Articles": [],
            "Repetitive_Phrases": 0,
            "Complex_Sentences": 0,
        }

        for token in doc:
            if language == "en":
                # Detect subject-verb agreement issues
                if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                    if token.tag_ in ["NN", "NNS"] and token.head.tag_ not in ["VBZ", "VBP"]:
                        syntax_features["Subject-Verb_Agreement"].append(
                            f"Issue: {token.text} -> {token.head.text}"
                        )

                # Detect missing articles
                if token.pos_ == "NOUN" and token.i > 0 and doc[token.i - 1].pos_ != "DET":
                    syntax_features["Missing_Articles"].append(
                        f"Missing article before: {token.text}"
                    )

            # Detect complex sentences
            if token.dep_ == "advcl" or token.dep_ == "ccomp":
                syntax_features["Complex_Sentences"] += 1

        # Detect repetitive phrases (common in machine translations or non-native texts)
        repetitive_phrases = re.findall(r"\b(\w+)\b(?=.*\b\1\b)", text)
        syntax_features["Repetitive_Phrases"] = len(repetitive_phrases)

        return syntax_features

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
        # Ensure the text is not empty or too short for n-grams extraction
        if not text or len(text.split()) < n:
            return []

        vectorizer = CountVectorizer(ngram_range=(n, n), analyzer='word', stop_words='english')

        try:
            X = vectorizer.fit_transform([text])
            return vectorizer.get_feature_names_out()
        except ValueError as e:
            # If the vocabulary is empty or contains only stop words, handle the exception
            logging.warning(f"Skipping n-grams extraction due to empty vocabulary: {e}")
            return []

    def identify_origin_from_syntax(self, syntax_results):
        score = 0

        # Missing articles are common in some non-native English texts
        if len(syntax_results["Missing_Articles"]) > 0:
            score += 1

        # Subject-verb agreement issues
        if len(syntax_results["Subject-Verb_Agreement"]) > 0:
            score += 2

        # Repetitive phrases (indicator of non-native English or machine translation)
        if syntax_results["Repetitive_Phrases"] > 0:
            score += 2

        # Complex sentence structures (indicator of over-formal or translated text)
        if syntax_results["Complex_Sentences"] > 2:
            score += 2

        # Final evaluation based on score
        if score >= 5:
            return "Possible machine-translated text"
        elif score >= 3:
            return "Likely non-native English speaker"

        return "Unknown"

    def classify_text(self, text):
        embeddings = self.get_bert_embeddings(text).numpy().reshape(1, -1)
        syntax_features = self.analyze_syntax(text)
        combined_features = list(embeddings[0]) + [
            len(syntax_features["Missing_Articles"]),
            len(syntax_features["Subject-Verb_Agreement"]),
            syntax_features["Repetitive_Phrases"],
            syntax_features["Complex_Sentences"],
        ]
        return self.identify_origin_from_syntax(syntax_features)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analysis = LinguisticAnalysis()
    result = analysis.classify_text("创建Huawei_LiteOS_Kernel项目，初始提交代码及开发指导文档")
    print(f"Classification result: {result}")
