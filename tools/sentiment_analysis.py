from textblob import TextBlob
from crewai.tools import BaseTool

class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = ("Analyzes the sentiment of text "
                       "to ensure positive and engaging communication.")

    def _run(self, text: str) -> str:
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity

        if sentiment_polarity > 0:
            return "positive"
        elif sentiment_polarity < 0:
            return "negative"
        else:
            return "neutral"