# 🧠 Customer Complaint Intelligence System

An AI-powered NLP project that automatically analyzes, categorizes, and routes customer complaints.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Category Detection** | Payment, Delivery, Technical, Customer Service, Product Quality, Returns, Account |
| **Urgency Detection** | Critical / High / Medium / Low based on keywords & sentiment |
| **Sentiment Analysis** | Positive / Neutral / Negative via TextBlob |
| **Key Issue Extraction** | Detects order numbers, recurring issues, legal threats, churn risk |
| **Smart Labeling** | Multi-label tags: financial-impact, churn-risk, recurring, loyal-customer |
| **Auto Reply Generation** | Suggests a professional reply per complaint type |
| **Dashboard** | Plotly charts — category distribution, urgency pie, confidence scatter |
| **Batch Upload** | Upload CSV, analyze all complaints, download results |
| **History & Filtering** | Filter by category, urgency, sentiment |

---

## 🛠 Setup

### 1. Clone / Download the project
```bash
cd complaint_system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📁 Project Structure

```
complaint_system/
├── app.py              # Main Streamlit UI (4 pages)
├── nlp_engine.py       # NLP logic: categorization, urgency, sentiment
├── data_manager.py     # JSON-based complaint storage
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── complaints_db.json  # Auto-created on first run
```

---

## 🧠 NLP Concepts Used

- **Multi-label classification** — keyword-based category matching
- **Sentiment analysis** — TextBlob polarity scoring
- **Rule-based NLP** — regex patterns for entity extraction
- **Topic modeling** (extendable with LDA/sklearn)
- **Urgency scoring** — weighted keyword detection

---

## 📊 Example Output

```yaml
Category:         Payment Issue
Urgency:          High
Sentiment:        Negative
Confidence:       87%
Action:           Process refund, send apology voucher
Department:       Finance & Billing
SLA:              4 hours
Labels:           payment-issue, financial-impact, churn-risk
```

---

## 📈 Extending the Project

- Replace keyword rules with a **fine-tuned BERT classifier** (HuggingFace)
- Add **LDA topic modeling** for unseen complaint types
- Connect to a **real CRM** (Zendesk, Freshdesk API)
- Add **email integration** to auto-respond
- Train on real complaint datasets (e.g., Amazon reviews, Twitter customer support)

---

## 📄 License
MIT — Free to use for academic & commercial projects.
