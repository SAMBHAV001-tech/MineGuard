# MineGuard – Rockfall Prediction System

MineGuard is a real-time rockfall monitoring and risk-prediction system built using:
- **Python (FastAPI)** for backend
- **HTML, CSS, JS, Chart.js, Tailwind** for frontend
- Custom lightweight **AI risk-scoring logic** 

---

## 🚀 Overview

MineGuard continuously reads:
- Vibration
- Displacement
- Pore pressure
- Temperature, humidity, rainfall, wind speed

Using a custom **threshold + weighted scoring model**, MineGuard predicts:
- **Low risk**
- **Medium risk**
- **High risk**

Everything works fully standalone — **no paid APIs and no LLMs involved**.

---

MineGuardAI/
├── mineguard_backend/ # FastAPI service
│ ├── app/
│ ├── data/
│ ├── scripts/
│ ├── venv/ (ignored)
│ ├── requirements.txt
│ └── Dockerfile
│
├── mineguard_frontend/
│ └── Mineguard/
│ ├── public/
│ ├── src/
│ ├── script.js
│ ├── style.css
│ ├── index.html
│ └── package.json
│
└── README.md


Both backend and frontend stay inside a single main repository, clean and organized.

---

## 🧠 AI Model (Simple, Local, No API)

MineGuard uses a custom rule-based AI model:

- Reads vibration, displacement, pore pressure  
- Reads temperature, humidity, rainfall  
- Applies weighted logic  
- Calculates a **final normalized risk score**
- Maps it to **Low / Medium / High**

> Note: This is NOT a machine learning model.  
> It is deterministic, explainable, and lightweight.

---

## 🌟 Features

- Real-time vibration graph (updates every 5 seconds)
- Weather data auto-refresh
- Live sensor readings (vibration, displacement, pore pressure)
- AI-based risk prediction with color gradient bars
- Auto-alert banners for HIGH/MEDIUM/LOW risk  
- Coordinate-based risk calculation  
- Clean UI with Tailwind + Lucide icons  

---

## 🖥️ Frontend Technologies

- HTML5 + Tailwind CSS  
- Chart.js (dynamic vibration graph)
- Vanilla JavaScript  
- Lucide icons  
- Responsive layout  

---

## 🔧 Backend Technologies

- Python FastAPI  
- UVicorn  
- requests  
- Custom risk engine  
- Modular endpoints  
- Render-ready deployment  

---

## 🚀 Running the Backend

cd mineguard_backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Backend runs at:

http://127.0.0.1:8000

## 🚀 Running the Frontend
cd mineguard_frontend/Mineguard
npm install
npm run dev


Frontend runs at:

http://localhost:5173/

## 🌐 Deployment

Backend is deployed on Render.
Frontend is deployed on Vercel.

Live at: https://mine-guard-50que895k-sambhav-das-projects.vercel.app/

## 🤝 Contributors

> Sambhav Das, 
> Soumit Sen,
> Soumyajeet Satapathy

## 📜 License

This project is open for learning & research use.



