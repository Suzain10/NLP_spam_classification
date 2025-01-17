# -*- coding: utf-8 -*-
"""NLP_P1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HUJfp-8qji8iLKKK41n4qxNyzTXpfFRc
"""

import pandas as pd
import numpy as np
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from imblearn.over_sampling import SMOTE
from gensim.models import Word2Vec

# Seed for reproducibility
np.random.seed(42)

# Load and preprocess the dataset
df = pd.read_csv('spam.csv', encoding='ISO-8859-1')
df.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], inplace=True)  # Drop unnecessary columns
df.rename(columns={'v1': 'Result', 'v2': 'Message'}, inplace=True)  # Rename columns for clarity

# Display dataset info and distribution of labels
print(df.info())
print(df['Result'].value_counts())

# Download NLTK stopwords for text preprocessing
nltk.download('stopwords')

# Text preprocessing: Cleaning, stemming, and removing stopwords
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
corpus = []
for message in df['Message']:
    review = re.sub('[^a-zA-Z]', ' ', message)  # Remove non-alphabetic characters
    review = review.lower().split()  # Convert to lowercase and split into words
    review = [ps.stem(word) for word in review if word not in stop_words]  # Stem and remove stopwords
    corpus.append(' '.join(review))  # Join words back into a single string

# Encode labels: Convert 'spam'/'ham' to 1/0
y = pd.get_dummies(df['Result'], drop_first=True).values.ravel()

# Vectorize and split data using CountVectorizer
cv = CountVectorizer(max_features=2500)
X_cv = cv.fit_transform(corpus).toarray()
X_train_cv, X_test_cv, y_train_cv, y_test_cv = train_test_split(X_cv, y, test_size=0.2, random_state=10)

# Apply SMOTE with sampling strategy 0.2 for CountVectorizer
smote = SMOTE(sampling_strategy=0.2, random_state=42)
X_train_cv_res, y_train_cv_res = smote.fit_resample(X_train_cv, y_train_cv)

# Train and evaluate Naive Bayes model using CountVectorizer features
model_cv = MultinomialNB()
model_cv.fit(X_train_cv_res, y_train_cv_res)
y_pred_cv = model_cv.predict(X_test_cv)

print("CountVectorizer with SMOTE (0.2):")
print(f"Accuracy: {accuracy_score(y_test_cv, y_pred_cv)}")
print(classification_report(y_test_cv, y_pred_cv))
print("\n" + "="*50 + "\n")

# Vectorize and split data using TfidfVectorizer
tv = TfidfVectorizer(max_features=2500)
X_tv = tv.fit_transform(corpus).toarray()
X_train_tv, X_test_tv, y_train_tv, y_test_tv = train_test_split(X_tv, y, test_size=0.2, random_state=10)

# Apply SMOTE with sampling strategy 0.25 for TfidfVectorizer
smote = SMOTE(sampling_strategy=0.25, random_state=42)
X_train_tv_res, y_train_tv_res = smote.fit_resample(X_train_tv, y_train_tv)

# Train and evaluate Naive Bayes model using TfidfVectorizer features
model_tv = MultinomialNB()
model_tv.fit(X_train_tv_res, y_train_tv_res)
y_pred_tv = model_tv.predict(X_test_tv)

print("TfidfVectorizer with SMOTE (0.25):")
print(f"Accuracy: {accuracy_score(y_test_tv, y_pred_tv)}")
print(classification_report(y_test_tv, y_pred_tv))
print("\n" + "="*50 + "\n")

# TF-IDF with bi-grams
tfidf_ngram_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=2500)
X_tfidf_ngram = tfidf_ngram_vectorizer.fit_transform(corpus).toarray()
X_train_tfidf_ngram, X_test_tfidf_ngram, y_train_tfidf_ngram, y_test_tfidf_ngram = train_test_split(X_tfidf_ngram, y, test_size=0.2, random_state=10)

# Apply SMOTE with sampling strategy 0.25 for TF-IDF with bi-grams
smote = SMOTE(sampling_strategy=0.25, random_state=42)
X_train_tfidf_ngram_res, y_train_tfidf_ngram_res = smote.fit_resample(X_train_tfidf_ngram, y_train_tfidf_ngram)

# Train and evaluate Naive Bayes model using TF-IDF bi-grams features
model_tfidf_ngram = MultinomialNB()
model_tfidf_ngram.fit(X_train_tfidf_ngram_res, y_train_tfidf_ngram_res)
y_pred_tfidf_ngram = model_tfidf_ngram.predict(X_test_tfidf_ngram)

print("TF-IDF with N-grams and SMOTE (0.25):")
print(f"Accuracy: {accuracy_score(y_test_tfidf_ngram, y_pred_tfidf_ngram)}")
print(classification_report(y_test_tfidf_ngram, y_pred_tfidf_ngram))
print("\n" + "="*50 + "\n")

# Train Word2Vec model
sentences = [review.split() for review in corpus]
w2v_model = Word2Vec(sentences, vector_size=100, window=5)

# Create feature vectors by averaging word vectors for each message
def get_feature_vector(message, model):
    words = message.split()
    word_vectors = [model.wv[word] for word in words if word in model.wv]
    if word_vectors:
        return np.mean(word_vectors, axis=0)
    else:
        return np.zeros(model.vector_size)

X_w2v = np.array([get_feature_vector(message, w2v_model) for message in corpus])

# Split the data
X_train_w2v, X_test_w2v, y_train_w2v, y_test_w2v = train_test_split(X_w2v, y, test_size=0.2, random_state=10)

# Apply SMOTE with sampling strategy 0.3 for Word2Vec features
smote = SMOTE(sampling_strategy= 0.3, random_state=42)
X_train_w2v_res, y_train_w2v_res = smote.fit_resample(X_train_w2v, y_train_w2v)

# Train and evaluate RandomForestClassifier model using Word2Vec features
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train_w2v_res, y_train_w2v_res)
y_pred_w2v = rf_model.predict(X_test_w2v)

print("Word2Vec with SMOTE (0.3):")
print(f"Accuracy: {accuracy_score(y_test_w2v, y_pred_w2v)}")
print(classification_report(y_test_w2v, y_pred_w2v))

