# -*- coding: utf-8 -*-
"""102203195_text_summarization_assignment .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10b6bo-64eXfS-VccCOcnV2YURMw5s4hf
"""

import numpy as np
import pandas as pd
from transformers import pipeline
from sklearn.preprocessing import MinMaxScaler

bart_model = pipeline("summarization", model="facebook/bart-large-cnn")  # BART
t5_model = pipeline("summarization", model="t5-small")  # T5
pegasus_model = pipeline("summarization", model="google/pegasus-xsum")  # Pegasus
gpt_model = pipeline("text-generation", model="gpt2")  # GPT-3.5 (placeholder for GPT-4)
bertsum_model = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")  # BERTSUM (closest equivalent)
xlnet_model = pipeline("summarization", model="xlnet-base-cased")  # XLNet
matchsum_model = pipeline("summarization", model="google/pegasus-multi_news")  # MatchSum (closest equivalent)

# Sample Text for Summarization
texts = [
    "Thapar Institute offers a course on Predictive Statistics. Students learn regression analysis, time-series forecasting, and machine learning techniques. The course emphasizes hands-on projects and real-world applications.",
    "Machine learning is an important component of Predictive Statistics. It involves algorithms that learn patterns from data and make predictions. Techniques like regression, classification, and clustering are widely used.",
    "Predictive Statistics is a field that combines statistical methods and machine learning to analyze data and make predictions. It is widely used in finance, healthcare, and marketing for decision-making.",
    "Data preprocessing is a crucial step in Predictive Statistics. It involves cleaning, transforming, and organizing data to ensure accurate predictions. Techniques like normalization and feature engineering are commonly used.",
    "Thapar Institute provides students with hands-on projects in Predictive Statistics. These projects involve real-world datasets and help students apply theoretical concepts to practical problems."
]

# Function to Summarize Text Using a Model
def summarize_text(text, model, max_length=50, min_length=25):
    if model == gpt_model:
        # GPT-3.5 is a text-generation model, so we use it for abstractive summarization
        summary = model(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['generated_text']
    else:
        # Other models are summarization-specific
        summary = model(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
    return summary

# Summarize Texts Using All Models
summaries = []
for text in texts:
    summaries.append([
        summarize_text(text, bart_model),
        summarize_text(text, t5_model),
        summarize_text(text, pegasus_model),
        summarize_text(text, gpt_model),
        summarize_text(text, bertsum_model),
        summarize_text(text, xlnet_model),
        summarize_text(text, matchsum_model)
    ])

# Convert Summaries to a DataFrame for Better Visualization
model_names = ["BART", "T5", "Pegasus", "GPT-3.5", "BERTSUM", "XLNet", "MatchSum"]
df_summaries = pd.DataFrame(summaries, columns=model_names)

# Add Original Text Column
df_summaries.insert(0, "Original Text", texts)

# Print Summaries
print("Summaries Generated by Different Models:")
print(df_summaries.to_string(index=False))

!pip install sentence-transformers
from sentence_transformers import SentenceTransformer

import numpy as np
import pandas as pd
from transformers import pipeline
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cosine

# Load a pre-trained sentence transformer model
sentence_model = SentenceTransformer('all-mpnet-base-v2') # You can choose a different model if needed

# Compute Decision Matrix
decision_matrix = []
for i, text in enumerate(texts):
    row = []
    for j, model in enumerate([bart_model, t5_model, pegasus_model, gpt_model, bertsum_model, xlnet_model, matchsum_model]):
        summary = summaries[i][j]
        # Criterion 1: Summary Length (shorter is better)
        length_score = len(summary)

        # Criterion 2: Similarity to Original Text (higher is better) - Using sentence-transformers
        text_embedding = sentence_model.encode([text])[0]
        summary_embedding = sentence_model.encode([summary])[0]
        similarity_score = 1 - cosine(text_embedding, summary_embedding)

        # Criterion 3: Readability (higher is better, approximated by summary length)
        readability_score = 1 / (1 + len(summary))  # Inverse of length
        row.append([length_score, similarity_score, readability_score])
    decision_matrix.append(row)

decision_matrix = np.array(decision_matrix)

# Normalize Decision Matrix
scaler = MinMaxScaler()
normalized_matrix = scaler.fit_transform(decision_matrix.reshape(-1, 3)).reshape(decision_matrix.shape)

# Define Weights for Criteria
weights = np.array([0.4, 0.4, 0.2])  # Weights for length, similarity, readability

# Apply TOPSIS
def apply_topsis(matrix, weights):
    weighted_matrix = matrix * weights
    ideal_solution = np.max(weighted_matrix, axis=(0, 1))
    anti_ideal_solution = np.min(weighted_matrix, axis=(0, 1))
    distance_from_ideal = np.sqrt(np.sum((weighted_matrix - ideal_solution) ** 2, axis=2))
    distance_from_anti_ideal = np.sqrt(np.sum((weighted_matrix - anti_ideal_solution) ** 2, axis=2))
    closeness = distance_from_anti_ideal / (distance_from_ideal + distance_from_anti_ideal)
    return closeness

# Compute TOPSIS Scores
topsis_scores = apply_topsis(normalized_matrix, weights)

# Rank Models Based on TOPSIS Scores
model_rankings = np.argsort(-topsis_scores.mean(axis=0))  # Sort in descending order

"""if custom weights"""

# Print Results
print("\nTOPSIS Scores for Each Model:")
for i, model in enumerate(model_names):
    print(f"{model}: {topsis_scores.mean(axis=0)[i]:.4f}")

print("\nRanking of Models (Best to Worst):")
for i, rank in enumerate(model_rankings):
    print(f"{i + 1}. {model_names[rank]} (Score: {topsis_scores.mean(axis=0)[rank]:.4f})")

"""If equal weights"""

weightss = np.array([1, 1, 1])

# Apply TOPSIS
def apply_topsis(matrix, weightss):
    weighted_matrix = matrix * weightss
    ideal_solution = np.max(weighted_matrix, axis=(0, 1))
    anti_ideal_solution = np.min(weighted_matrix, axis=(0, 1))
    distance_from_ideal = np.sqrt(np.sum((weighted_matrix - ideal_solution) ** 2, axis=2))
    distance_from_anti_ideal = np.sqrt(np.sum((weighted_matrix - anti_ideal_solution) ** 2, axis=2))
    closeness = distance_from_anti_ideal / (distance_from_ideal + distance_from_anti_ideal)
    return closeness

# Compute TOPSIS Scores
topsis_scores = apply_topsis(normalized_matrix, weightss)

# Rank Models Based on TOPSIS Scores
model_rankings = np.argsort(-topsis_scores.mean(axis=0))  # Sort in descending order

# Print Results
print("\nTOPSIS Scores for Each Model:")
for i, model in enumerate(model_names):
    print(f"{model}: {topsis_scores.mean(axis=0)[i]:.4f}")

print("\nRanking of Models (Best to Worst):")
for i, rank in enumerate(model_rankings):
    print(f"{i + 1}. {model_names[rank]} (Score: {topsis_scores.mean(axis=0)[rank]:.4f})")