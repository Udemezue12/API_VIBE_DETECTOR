from transformers import pipeline


class MLClassifier:

    def __init__(self):

        self.classifier = pipeline(
            "text-classification",
            model="microsoft/codebert-base"
        )

    def predict(self, code):

        result = self.classifier(code[:512])

        return result