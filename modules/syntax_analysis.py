import spacy
import re
from langdetect import detect

class SyntaxAnalyzer:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_zh = spacy.load("zh_core_web_sm")

    def analyze_syntax(self, text):
        # Detect the language of the text
        language = "en" if text.lower() in ["initial commit", "first commit"] else detect(text)

        # Load the appropriate spaCy model based on language
        doc = self.nlp_zh(text) if language == "zh" else self.nlp_en(text)

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

        # Detect repetitive phrases
        repetitive_phrases = re.findall(r"\b(\w+)\b(?=.*\b\1\b)", text)
        syntax_features["Repetitive_Phrases"] = len(repetitive_phrases)

        return syntax_features
