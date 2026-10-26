import json
import re
import string

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set()
    
    try:
        lemmatizer = WordNetLemmatizer()
    except Exception:
        lemmatizer = None
except ImportError:
    nltk = None
    stop_words = set()
    lemmatizer = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Default fallback stop words if NLTK corpus is not downloaded
if not stop_words:
    stop_words = {
        "a", "about", "after", "again", "all", "am", "an", "and", "any", "are",
        "as", "at", "be", "because", "been", "before", "being", "below", "between",
        "both", "but", "by", "can", "did", "do", "does", "doing", "for", "from",
        "further", "had", "has", "have", "he", "her", "here", "him", "how", "i",
        "if", "in", "into", "is", "it", "its", "me", "more", "most", "my", "no",
        "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our",
        "out", "over", "she", "should", "so", "some", "such", "than", "that",
        "the", "their", "then", "there", "these", "they", "this", "those",
        "through", "to", "too", "under", "until", "up", "very", "was", "we",
        "were", "what", "when", "where", "which", "while", "who", "whom", "why",
        "will", "with", "you", "your"
    }


def preprocess_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    
    tokens = text.split()
    
    cleaned_tokens = []
    for word in tokens:
        if word not in stop_words and len(word) > 1:
            if lemmatizer:
                try:
                    word = lemmatizer.lemmatize(word)
                except Exception:
                    pass
            cleaned_tokens.append(word)

    return " ".join(cleaned_tokens)


class FAQBot:
    def __init__(self, data_path="faqs.json", threshold=0.2):
        self.threshold = threshold
        self.faqs = []
        self.questions_processed = []
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        
        self.load_data(data_path)

    def load_data(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        self.questions_processed = [
            preprocess_text(item["question"]) for item in self.faqs
        ]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions_processed)

    def get_answer(self, user_query):
        cleaned_query = preprocess_text(user_query)
        
        if not cleaned_query.strip():
            return {
                "answer": "Please enter a valid question.",
                "matched_question": None,
                "score": 0.0
            }

        query_vector = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        best_index = similarities.argmax()
        best_score = float(similarities[best_index])

        if best_score >= self.threshold:
            matched = self.faqs[best_index]
            return {
                "answer": matched["answer"],
                "matched_question": matched["question"],
                "score": round(best_score, 2)
            }
        else:
            return {
                "answer": "Sorry, I don't have an answer for that. Please try rephrasing or contact support.",
                "matched_question": None,
                "score": round(best_score, 2)
            }


if __name__ == "__main__":
    bot = FAQBot()
    print("FAQ Chatbot initialized. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Bot: Bye!")
                break

            response = bot.get_answer(user_input)
            print(f"Bot: {response['answer']}")
            if response["matched_question"]:
                print(f"     (Matched FAQ: \"{response['matched_question']}\" | Score: {response['score']})")
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
