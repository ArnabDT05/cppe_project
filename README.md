# 📡 Telecom Network Analytics Dashboard

![Dashboard Preview](telecom-dashboard/public/vite.svg) 

A **Real-Time Telecom Network Analytics Dashboard** designed to monitor live phone call telemetry, identify struggling cell towers, and use Machine Learning to predict call drops before they happen. 

This project simulates a live mobile network environment and provides an interactive, terminal-grade command center for network engineers.

## ✨ Key Features
- **Real-Time Data Generation**: A Python background thread that constantly simulates live phone call traffic, assigning random cell towers, signal strengths, and timestamps every second.
- **Machine Learning Predictor**: An integrated **Random Forest Classifier** trained to predict whether a phone call will drop based on real-time signal strength (dBm) and time of day.
- **Live React Dashboard**: A dense, auto-refreshing UI that features:
  - **Minute-by-Minute Heartbeat**: Tracks the moving average of network signal strength.
  - **Signal Quality Distribution**: Groups active calls into Excellent, Good, Fair, and Critical buckets.
  - **Top At-Risk Towers**: A live leaderboard of the worst-performing cell towers to prioritize maintenance.
- **Continuous Integration (CI)**: Fully automated **Jenkins** pipeline that triggers on GitHub pushes to test the Python backend and compile the optimized React frontend.

## 🛠️ Technology Stack
- **Backend**: Python 3, Flask, Pandas
- **Machine Learning**: Scikit-Learn (Random Forest)
- **Frontend**: React 19, Vite, Chart.js
- **DevOps**: Jenkins (Automated CI Pipeline), Git

---

## 🚀 How to Run Locally

### 1. Start the Python Backend
The backend serves the live API and handles the Machine Learning predictions.

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask API
python3 api.py
```
*The API will start running on `http://127.0.0.1:5000`*

### 2. Start the React Frontend
Open a **new terminal window** to start the dashboard.

```bash
# Navigate to the frontend directory
cd telecom-dashboard

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
*The dashboard will be available at `http://localhost:5173`*

---

## 📂 Project Structure
```text
cppe_project/
├── api.py                  # Main Flask server and live data aggregator
├── model.py                # Random Forest ML model training script
├── generate_data.py        # Generates historical dataset (telecom_data.csv)
├── rf_model.pkl            # Serialized Machine Learning model
├── Jenkinsfile             # CI Pipeline configuration for auto-builds
└── telecom-dashboard/      # React + Vite frontend application
    ├── src/
    │   ├── App.jsx         # Main dashboard grid and layout
    │   ├── App.css         # Clean light-mode design system
    │   └── ...charts       # Chart.js components for data visualization
```

## 🔄 Jenkins CI Pipeline
This repository is configured with a Declarative Jenkins Pipeline. On every push to the `main` branch, Jenkins automatically:
1. Provisions a fresh environment.
2. Installs Python and Node.js dependencies.
3. Validates backend Python scripts for syntax errors.
4. Compiles the React application into an optimized production build.

---
*Created for academic presentation and demonstration purposes.*
