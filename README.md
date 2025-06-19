# MediTrends

**MediTrends** is a web application that helps users explore health-related discussions across Reddit. It uses natural language processing and relevance-ranking to surface meaningful posts based on user queries.

---

## Features

* Search Reddit for medical discussions using keywords or symptoms
* ML-enhanced semantic search for improved result relevance
* Trending topic suggestions based on recent queries
* Clean, responsive frontend built with Tailwind CSS
* Flask-based backend with modular architecture

---

## Repository Structure

meditrends/
  backend/    *Python Flask API*
    app.py
    config.py
    reddit\_client.py
    search\_engine.py
    …
  frontend/    *Static frontend (HTML, Tailwind CSS, JavaScript)*
    index.html
  .gitignore

---

## Getting Started

### Backend Setup

1. Navigate to the backend folder: `cd backend`
2. Create and activate a virtual environment:

   * `python -m venv venv`
   * `venv\Scripts\activate` (on Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file in the backend folder with the following entries:
   REDDIT\_CLIENT\_ID=your\_reddit\_client\_id
   REDDIT\_CLIENT\_SECRET=your\_reddit\_client\_secret
   REDDIT\_USER\_AGENT=MediTrends/0.1 (by u/your\_reddit\_username)
5. Start the backend server: `python app.py`
   The API will be available at [http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)

### Frontend Setup

1. Navigate to the frontend folder: `cd frontend`
2. Launch a static development server: `python -m http.server 3000`
3. Open the frontend in your browser at [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## API Endpoints

* **GET /api/search**
  Query parameters:
    • q – search term or phrase
    • limit – number of results to return
    • sort – relevance or date
  Example: `/api/search?q=headache&limit=5&sort=relevance`

* **GET /api/trending**
  Query parameter:
    • limit – number of topics to return
  Example: `/api/trending?limit=5`
