import streamlit as st
import pandas as pd
import string

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Complaint Intelligence System", layout="wide")

st.title("📊 Customer Complaint Intelligence System")

# -----------------------
# Sample Dataset
# -----------------------
data = {
    "complaint": [
        "Payment failed but money deducted",
        "App is crashing again and again",
        "Delivery is very late",
        "Received damaged product",
        "Refund not processed yet",
        "Login issue, unable to access account",
        "Wrong item delivered",
        "Payment issue again, very frustrated"
    ],
    "category": [
        "Payment Issue",
        "Technical Issue",
        "Delivery Issue",
        "Product Issue",
        "Payment Issue",
        "Technical Issue",
        "Product Issue",
        "Payment Issue"
    ],
    "urgency": [
        "High",
        "Medium",
        "Low",
        "Medium",
        "High",
        "High",
        "Medium",
        "High"
    ]
}

df = pd.DataFrame(data)

# -----------------------
# Preprocessing (NO NLTK)
# -----------------------
stop_words = {
    "is","the","and","a","an","to","of","in","on","for","with","again","very"
}

def preprocess(text):
    text = text.lower()
    text = "".join([c for c in text if c not in string.punctuation])
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

df["clean_text"] = df["complaint"].apply(preprocess)

# -----------------------
# Vectorization
# -----------------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["clean_text"])

# -----------------------
# Models
# -----------------------
cat_model = LogisticRegression()
cat_model.fit(X, df["category"])

urg_model = LogisticRegression()
urg_model.fit(X, df["urgency"])

# -----------------------
# Prediction Function
# -----------------------
def predict_complaint(text):
    clean = preprocess(text)
    vec = vectorizer.transform([clean])
    
    category = cat_model.predict(vec)[0]
    urgency = urg_model.predict(vec)[0]
    
    if urgency == "High":
        action = "Immediate escalation 🚨"
    elif urgency == "Medium":
        action = "Handle within 24 hours ⏳"
    else:
        action = "Normal processing ✅"
    
    return category, urgency, action, vec

# -----------------------
# Similar Complaints
# -----------------------
def find_similar(vec):
    similarities = cosine_similarity(vec, X)
    idx = similarities.argsort()[0][-3:][::-1]
    return df["complaint"].iloc[idx]

# -----------------------
# UI
# -----------------------
user_input = st.text_area("✍️ Enter Customer Complaint")

if st.button("Analyze Complaint"):
    if user_input.strip() == "":
        st.warning("Please enter a complaint")
    else:
        category, urgency, action, vec = predict_complaint(user_input)

        col1, col2, col3 = st.columns(3)

        col1.metric("Category", category)
        col2.metric("Urgency", urgency)
        col3.metric("Suggested Action", action)

        st.subheader("🔁 Similar Complaints")
        similar = find_similar(vec)

        for s in similar:
            st.write("•", s)

# -----------------------
# Dataset Viewer (optional)
# -----------------------
with st.expander("📂 View Training Data"):
    st.dataframe(df)