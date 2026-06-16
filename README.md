# 🍞 Mutti's Bakery – Production System

[![Python Lint](https://github.com/Alinazari507/mutti-bakery-system/actions/workflows/lint.yml/badge.svg)](https://github.com/Alinazari507/mutti-bakery-system/actions/workflows/lint.yml)

A professional-grade, containerized backend system for **Mutti's Bakery** – designed to digitalize and scale traditional recipes with industrial precision.

> **Scenario**: Mutti's Backstube is expanding from 1 to 4 locations. This system replaces a flour‑dusty paper binder with a secure, scalable, and auditable digital solution.

---

## ✨ Key Features

- **Unit Normalisation (FR‑03)** – Converts cups, tablespoons, pinches, etc., to grams using Mutti's own measurement table.
- **Smart Scaling (FR‑06, FR‑07)** – Scales any recipe from 10 to 1,000 portions. Applies **non‑linear rules** (e.g., salt cap at 1.5× for batches > 500).
- **Precision Rounding (FR‑08)** – Quantities are rounded to 0.5g, 5g, or 10g steps for practical kitchen use.
- **Role‑Based Access Control (FR‑11)** – Three roles: **Admin (Mutti)** , **Manager**, and **Baker**. Only Mutti can approve recipes.
- **Version History** – Every recipe change is stored as a new version (never deleted, only archived).
- **Cost Calculation** – Automatically computes total production cost per batch based on ingredient prices.
- **Audit Logging** – Every action (login, scaling, approval, errors) is logged to `logs/app.log`.
- **Emergency Break‑Glass (CONF‑02)** – Two managers can temporarily gain admin privileges using PINs (alice/1234, bob/5678).
- **High Performance (NFR‑01)** – In‑memory caching ensures scaling results are returned in < 2ms (simulated).
- **Docker Containerisation** – Runs anywhere, eliminates "it works on my machine" excuses.

---

## 🏗️ Project Structure

mutti-bakery-personal/
├── .github/
│ └── workflows/
│ └── lint.yml # CI/CD pipeline (Flake8)
├── data/
│ ├── conversions.json # Mutti's measured conversion table
│ └── recipes.json # Recipe storage with versioning
├── logs/
│ └── app.log # Audit trail
├── src/
│ ├── auth.py # RoleType & User (RBAC)
│ ├── ingredient.py # Ingredient entity + normalisation
│ ├── recipe.py # Recipe, Versioning, Scaling, Cost
│ ├── break_glass.py # Emergency access protocol
│ ├── cache.py # Scaling cache (NFR-01)
│ └── main.py # CLI menu & orchestration
├── tests/ # (Ready for unit tests)
├── venv/ # Python virtual environment
├── .gitignore
├── Dockerfile
├── README.md
├── UAT_Protocol.md # Formal sign‑off document
├── requirements.txt
└── setup.sh # Automated environment setup
text


---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Alinazari507/mutti-bakery-system.git
cd mutti-bakery-system

2. Local Development (with venv)
bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (if any)
pip install -r requirements.txt   # (currently empty, but prepared)

# Run the application
python src/main.py

3. Using the Setup Script (optional)
bash

chmod +x setup.sh
./setup.sh

4. Run with Docker (Production Mode)
bash

# Build the image
docker build -t muttis-bakery .

# Run interactively (required for user input)
docker run -it --rm muttis-bakery

🧪 Testing & Quality Assurance

    Analogue Test Plan – 5 critical test cases (whiteboard) covering scaling, non‑linear rules, ambiguity blocking, normalisation, and rounding.

    Bug Hunting – Used VSCode Debugger to catch an injected logical error (screenshot included in assets).

    CI/CD Pipeline – GitHub Actions runs flake8 on every push, ensuring code quality.

    UAT Protocol – A formal sign‑off document (UAT_Protocol.md) is prepared for stakeholder acceptance.

🛠️ Technology Stack
Component	Technology
Language	Python 3.11
Containerisation	Docker CE
CI/CD	GitHub Actions (Flake8)
Data Storage	JSON (lightweight, editable by Mutti)
Version Control	Git + GitHub
Debugging	VSCode Debugger
👥 Contributors

    Mohammad Ali Nazari (Alinazari507)

📜 License

This project is developed for educational purposes as part of the Dualis Institut curriculum.
📄 UAT Sign‑Off

The system has passed all technical and functional tests. The formal User Acceptance Test Protocol can be found in UAT_Protocol.md, ready for Mutti's signature.