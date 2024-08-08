import re
from django.shortcuts import render
from .models import Komentar
import numpy as np
import requests

model_path = "model"
tokenizer_path = "tokenizer"

API_URL = "https://api-inference.huggingface.co/models/sidaus/hatespeech-commentnews-large-ind-2"
headers = {"Authorization": "Bearer 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"}

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

def send_query_with_wait_for_model(payload):
    try:
        return requests.post(API_URL, headers=headers, json={"inputs": payload, "options": {"wait_for_model": True}}).json()
    except Exception as e:
        if "Rate limit reached" in str(e.args[0]):
            print("eh miskin")

def prediction(request, berita_id):
    komentar_list = Komentar.objects.filter(berita__id=berita_id)

    for komentar in komentar_list:
        # Preprocess the comment text
        preprocessed_text = cleansing(komentar.isi_komentar)
        print(preprocessed_text)

        # Send the query to the Inference API
        data = send_query_with_wait_for_model(preprocessed_text)
        print(data)

        # Assuming the model returns a list of results for each sentence
        result = data[0][0]  # Assuming the model outputs a single result for each input

        # Print the result (adjust as needed)
        print(f"Generated Sentence: {preprocessed_text}")
        print(f"Model Output: {result}")
        print("-" * 40)

        # Save the prediction & probabilities to the Komentar model
        # probabilities = torch.nn.functional.softmax(torch.tensor(result["logits"]), dim=-1).cpu().detach().numpy()
        # probabilities = np.max(probabilities)
        # predicted_class = torch.argmax(torch.tensor(result["logits"])).item()
        # class_labels = ["Non-Hate", "Hate"]
        # predicted_label = class_labels[predicted_class]
        
        probabilities = result['score']
        predicted_label = result['label']

        label_mapping = {'LABEL_0': 'Non-Hate', 'LABEL_1': 'Hate'}
        predicted_label = label_mapping.get(predicted_label, predicted_label)

        komentar.probabilitas = probabilities
        komentar.prediksi = predicted_label
        komentar.save()

    # Set 'stop' attribute in the request object
    request.stop_prediction = True

    return render(request, 'detail_berita.html')