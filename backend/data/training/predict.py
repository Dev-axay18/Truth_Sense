import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCredibilityPredictor:
    def __init__(self, model_dir="model_output/final_model"):
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, model_dir)
        
        # Load the model and tokenizer
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.model.eval()  # Set to evaluation mode
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        logger.info(f"Model loaded from {model_path}")
        logger.info(f"Using device: {self.device}")

    def predict(self, text: str) -> dict:
        """Predict the credibility of a news article."""
        # Prepare the input
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1)
            confidence = probabilities[0][prediction].item()
        
        return {
            "is_credible": bool(prediction.item()),
            "confidence": confidence,
            "credibility_score": float(probabilities[0][1].item())  # Probability of being credible
        }

def main():
    # Initialize predictor
    predictor = NewsCredibilityPredictor()
    
    # Example news articles to test
    test_articles = [
        {
            "title": "Breaking: Major Scientific Discovery",
            "content": "Scientists at a leading research institution have made a groundbreaking discovery that could revolutionize our understanding of quantum physics. The peer-reviewed study, published in Nature, has been verified by multiple independent research teams."
        },
        {
            "title": "Shocking: Aliens Contact Earth",
            "content": "Anonymous sources claim that extraterrestrial beings have made contact with world leaders. The story went viral on social media after being shared by several popular conspiracy theory channels."
        }
    ]
    
    # Test each article
    for article in test_articles:
        text = f"Title: {article['title']}\nContent: {article['content']}"
        result = predictor.predict(text)
        
        print("\nArticle:", article['title'])
        print("Credibility:", "Credible" if result['is_credible'] else "Not Credible")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Credibility Score: {result['credibility_score']:.2%}")

if __name__ == "__main__":
    main() 