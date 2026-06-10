# Fake Instagram Account Detector

A machine learning-powered web application designed to identify fake or inauthentic Instagram accounts. This project has been migrated from an initial Streamlit prototype into a robust, full-stack web application featuring a dedicated API and an interactive frontend.

## 🚀 Project Overview

Social media platforms are increasingly populated by automated bots and fake accounts. This tool leverages an Artificial Neural Network (ANN) trained on profile attributes (such as follower/following ratio, profile picture presence, account age, and bio length) to accurately predict the legitimacy of an account. 

By migrating to a dedicated API architecture, the prediction model is now decoupled from the UI, allowing for faster inferences, better scalability, and seamless integration with modern frontend frameworks.

## ✨ Features

* **Machine Learning Integration:** Utilizes a trained Neural Network for high-accuracy predictions.
* **RESTful API Backend:** The model is wrapped in a dedicated API for modular data handling.
* **Modern Web Interface:** A responsive frontend allowing users to easily input profile metrics and receive real-time analysis.
* **Scalable Architecture:** Clean separation of concerns between the ML inference engine and the user interface.

## 🛠️ Tech Stack

**Frontend:**
* [React]
* [Tailwind CSS / Other styling]

**Backend & ML API:**
* [FastAPI]
* Python 3.x
* [TensorFlow / PyTorch / Scikit-learn] 
* Pandas & NumPy for data preprocessing

## ⚙️ Local Installation & Setup

To run this project locally, you will need to start both the backend API and the frontend application.

### Prerequisites
* Node.js & npm (for frontend)
* Python 3.8+ (for backend and ML model)

### 1. Clone the Repository
```bash
git clone [https://github.com/vidhan-tiwari/fake_account_detector.git](https://github.com/vidhan-tiwari/fake_account_detector.git)
cd fake_account_detector
