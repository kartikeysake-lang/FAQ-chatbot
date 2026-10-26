# FAQ-chatbot
A simple customer service chatbot built with Python that answers questions about shipping, returns, and warranties. It cleans and tokenizes user text, then matches it to a dataset using TF-IDF vectorization and cosine similarity.

Tech Stack
Language: Python 3

NLP Processing: NLTK (for tokenization, stopword removal, and lemmatization)

Matching & Similarity: scikit-learn (TfidfVectorizer and cosine_similarity)

Frontend: HTML, CSS, and JavaScript

Project File Structure
chatbot.py: Core processing logic and terminal mode.

app.py: Web server for the browser interface.

faqs.json: Question and answer dataset file.

index.html: Client-side chat user interface.

requirements.txt: Python package dependency list.

run.bat: Windows shortcut to launch the web interface.

run_cli.bat: Windows shortcut to run the terminal mode.

Installation & Setup Steps
Clone the repository:

Bash
git clone https://github.com/your-username/faq-chatbot.git
cd faq-chatbot
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Web Interface: Run python app.py, then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

Terminal Mode: Run python chatbot.py.
