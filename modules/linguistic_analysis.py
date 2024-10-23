from transformers import BertTokenizer, BertModel
import torch
import spacy
import re

class LinguisticAnalysis:
    def __init__(self):
        # Load pre-trained models
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.nlp = spacy.load("en_core_web_sm")

    def get_bert_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze()

    def analyze_syntax(self, text):
        doc = self.nlp(text)
        syntax_features = {
            "POS_tags": [token.pos_ for token in doc],
            "Dependency_tags": [token.dep_ for token in doc],
            "Subject-Verb_Agreement": [],
            "Missing_Articles": [],
        }
        for token in doc:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                if token.tag_ in ["NN", "NNS"] and token.head.tag_ not in ["VBZ", "VBP"]:
                    syntax_features["Subject-Verb_Agreement"].append(f"Issue: {token.text} -> {token.head.text}")
            if token.pos_ == "NOUN" and token.i > 0 and doc[token.i - 1].pos_ != "DET":
                syntax_features["Missing_Articles"].append(f"Missing article before: {token.text}")
        return syntax_features

    def extract_code_patterns(self, text):
        variable_pattern = r"\b[a-zA-Z_]\w*\b"
        function_pattern = r"\bdef\s+\w+\b"
        variables = re.findall(variable_pattern, text)
        functions = re.findall(function_pattern, text)
        return {"variables": variables, "functions": functions, "doc_style": "pythonic" if "def " in text else "unknown"}

    def identify_origin_from_syntax(self, syntax_results):
        if len(syntax_results['Missing_Articles']) > 0 and len(syntax_results['Subject-Verb_Agreement']) > 0:
            return "Chinese-origin"
        elif "can to" in syntax_results['Subject-Verb_Agreement']:
            return "Russian-origin"
        else:
            return "Unknown"
