import pandas as pd
import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from datasets import Dataset
import logging
import os
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import DataLoader
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_metrics(pred):
    """Compute metrics for evaluation."""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

class NewsCredibilityTrainer:
    def __init__(self, model_name="distilbert-base-uncased", output_dir="model_output"):
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(current_dir, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.model_name = model_name
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,  # Binary classification: credible vs not credible
            problem_type="single_label_classification"
        )
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def prepare_dataset(self, data_path: str):
        """Prepare the dataset for training."""
        # Get the full path to the training data
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_data_path = os.path.join(current_dir, "training_data", data_path)
        
        # Read the CSV file
        df = pd.read_csv(full_data_path)
        
        # Balance the dataset
        credible_df = df[df['label'] == 1]
        not_credible_df = df[df['label'] == 0]
        
        # Take equal number of samples from each class
        min_samples = min(len(credible_df), len(not_credible_df))
        balanced_df = pd.concat([
            credible_df.sample(min_samples, random_state=42),
            not_credible_df.sample(min_samples, random_state=42)
        ])
        
        # Split into train and validation sets
        train_df, val_df = train_test_split(balanced_df, test_size=0.2, random_state=42, stratify=balanced_df['label'])
        
        # Convert to HuggingFace datasets
        train_dataset = Dataset.from_pandas(train_df)
        val_dataset = Dataset.from_pandas(val_df)
        
        # Tokenize the datasets
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
        
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)
        
        # Set format for PyTorch
        train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
        val_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
        
        return train_dataset, val_dataset

    def train(self, train_dataset, val_dataset):
        """Train the model."""
        # Create data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=10,  # Increased epochs
            per_device_train_batch_size=8,  # Reduced batch size for better stability
            per_device_eval_batch_size=8,
            warmup_steps=1000,  # Increased warmup steps
            weight_decay=0.01,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=50,
            save_steps=50,
            eval_steps=50,
            learning_rate=2e-5,  # Added learning rate
            gradient_accumulation_steps=4,  # Added gradient accumulation
            fp16=torch.cuda.is_available()  # Enable mixed precision if GPU available
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
            data_collator=data_collator
        )
        
        # Train the model
        logger.info("Starting training...")
        trainer.train()
        
        # Save the model and tokenizer
        final_model_dir = os.path.join(self.output_dir, "final_model")
        self.model.save_pretrained(final_model_dir)
        self.tokenizer.save_pretrained(final_model_dir)
        logger.info(f"Model saved to {final_model_dir}")
        
        # Evaluate on validation set
        eval_results = trainer.evaluate()
        logger.info(f"Validation results: {eval_results}")

def main():
    # Initialize trainer
    trainer = NewsCredibilityTrainer()
    
    # Prepare dataset
    train_dataset, val_dataset = trainer.prepare_dataset("training_data.csv")
    
    # Train model
    trainer.train(train_dataset, val_dataset)

if __name__ == "__main__":
    main() 