import logging
from modules.embeddings import Embeddings
from modules.syntax_analysis import SyntaxAnalyzer
from modules.feature_extraction import FeatureExtractor

class LinguisticAnalysis:
    def __init__(self):
        self.embeddings = Embeddings()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.feature_extractor = FeatureExtractor()

    def classify_text(self, text):
        # Generate embeddings
        embeddings = self.embeddings.get_bert_embeddings(text).numpy().reshape(1, -1)

        # Analyze syntax
        syntax_features = self.syntax_analyzer.analyze_syntax(text)

        # Combine features for classification
        combined_features = list(embeddings[0]) + [
            len(syntax_features["Missing_Articles"]),
            len(syntax_features["Subject-Verb_Agreement"]),
            syntax_features["Repetitive_Phrases"],
            syntax_features["Complex_Sentences"],
        ]

        return self.identify_origin_from_syntax(syntax_features)

    def identify_origin_from_syntax(self, syntax_results):
        score = 0

        # Scoring logic
        if len(syntax_results["Missing_Articles"]) > 0:
            score += 1
        if len(syntax_results["Subject-Verb_Agreement"]) > 0:
            score += 2
        if syntax_results["Repetitive_Phrases"] > 0:
            score += 2
        if syntax_results["Complex_Sentences"] > 2:
            score += 2

        if score >= 5:
            return "Possible machine-translated text"
        elif score >= 3:
            return "Likely non-native English speaker"

        return "Unknown"

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analysis = LinguisticAnalysis()
    result = analysis.classify_text("创建Huawei_LiteOS_Kernel项目，初始提交代码及开发指导文档")
    print(f"Classification result: {result}")
