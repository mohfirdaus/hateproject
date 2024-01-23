import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from django.shortcuts import render
from .models import Komentar
import numpy as np
from pathlib import Path

# Function to remove emojis from a text
def remove_emojis(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Function to remove repeated punctuation marks from a text
def remove_repeated_punctuation(text):
    return re.sub(r'([!.,;?])\1+', r'\1', text)

def cleansing(text):
    text = str(text)

    # Remove emojis
    text = remove_emojis(text)

    # Convert to lowercase
    text = text.lower()

    # Remove repeated punctuation marks
    text = remove_repeated_punctuation(text)

    # Add spaces around non-alphabetic and non-numeric characters
    text = re.sub(r'([^a-zA-Z0-9 ])', r' \1 ', text)

    # Remove unwanted characters
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)

    # Remove extra spaces
    text = re.sub(r'\s{2,}', ' ', text)

    return text

def prediction(request, berita_id, model_path, tokenizer_path):
    komentar_list = Komentar.objects.filter(berita__id=berita_id)

    # Load the tokenizer and model from local paths
    tokenizer = AutoTokenizer.from_pretrained(Path(tokenizer_path))
    model = AutoModelForSequenceClassification.from_pretrained(Path(model_path))

    for komentar in komentar_list:
        # Preprocess the comment text
        preprocessed_text = cleansing(komentar.isi_komentar)

        # Tokenize the comment input
        inputs = tokenizer(preprocessed_text, return_tensors="pt")

        # Make the prediction
        with torch.no_grad():
            outputs = model(**inputs)
            print(outputs)
        
        # Menghitung probabilitas menggunakan softmax
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().detach().numpy()
        probabilities = np.max(probabilities)
        print(probabilities)

        # Get the predicted class
        predicted_class = torch.argmax(outputs.logits).item()

        # Define the class labels
        class_labels = ["Non-Hate", "Hate"]

        # Get the predicted label
        predicted_label = class_labels[predicted_class]

        # Save the prediction & probabilites to the Komentar model
        komentar.probabilitas = probabilities
        komentar.prediksi = predicted_label
        komentar.save()
    
    # Set 'stop' attribute in the request object
    request.stop_prediction = True

    return render(request, 'detail_berita.html')