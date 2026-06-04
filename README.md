# 📈 Smart Trade Dashboard – Advanced Copy-Trading Architecture

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0-success?logo=django)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)
![Chart.js](https://img.shields.io/badge/Charts-Chart.js-orange?logo=chartdotjs)
![License](https://img.shields.io/badge/License-MIT-green)

Smart Trade Dashboard is a enterprise-grade, high-performance copy-trading simulation platform architected with Python/Django and real-time client-side interactive rendering. Inspired by tier-1 crypto exchanges like **BingX** and **Bitget**, this ecosystem models advanced internal ledger management, real-time matrix analytics, risk vectoring, and algorithmic trader replication protocols.

This repository demonstrates advanced full-stack capabilities, showcasing secure transaction structures, data concurrency handling, and sleek cyberpunk-themed data visualizations.

---

## 🎨 System Previews & Interface Showcase

Here is a comprehensive breakdown of the core operational windows across the application interface:

| Admin Vector Controls & Root Override | Premium Verified Trader Profile |
|:---:|:---:|
| <img src="assets/1.png" alt="Admin Control Grid" width="430"> | <img src="assets/2.png" alt="Verified Trader View" width="430"> |
| *Admin sub-system enabling live graph manipulation via draggable vector handles.* | *The premium matrix view accessible by regular users featuring historical nodes.* |

| User Performance Analytics | Allocation & Link Protocol Modal |
|:---:|:---:|
| <img src="assets/3.png" alt="Performance Analytics" width="430"> | <img src="assets/4.png" alt="Investment Protocol" width="430"> |
| *Responsive, animated timeline evolution charts rendering real-time ROI tracking.* | *Secure execution engine calculating proportional investment bounds before link initialization.* |

| Global Market Monitor | Financial Transaction History |
|:---:|:---:|
| <img src="assets/5.png" alt="Market Grid" width="430"> | <img src="assets/6.png" alt="Ledger Management" width="430"> |
| *Dynamic asset tracking panel managing manual percentage offsets on spot market tickers.* | *Immutable transaction logs capturing all approved, pending, and rejected system deposits.* |

| Investor Portfolio Status | Cyberpunk System Settings Panel |
|:---:|:---:|
| <img src="assets/7.png" alt="User Ledger Status" width="430"> | <img src="assets/8.png" alt="Core Global Control" width="430"> |
| *Real-time position trackers rendering active copier equity pools and cumulative PnL metrics.* | *Global parameter console managing corporate assets, system wallets, and minimum load capacities.* |

---

## 🚀 Core Engine Architectural Highlights

### ⚡ Mathematical PnL Persistence Logic
When investors top up an existing active copy-trading slot, adding capital blindly alters the arithmetic basis of their ongoing returns. This engine implements a **Proportional Scaling Adjustment Protocol**. Upon deposit modification, the backend intercepts the current `entry_roi` alongside the lead trader’s instantaneous performance vectors:
* Calculates current percentage change relative to baseline vectors.
* Computes an inverse mathematical adjustment factor:
  $$\text{Adjustment Factor} = 1 + \left(\frac{\Delta \text{ROI}}{100}\right)$$
* Modifies the underlying investment principal dynamically so that front-end yield formulas remain completely coherent and uniform without distorting historical profit tracking.

### 🔒 Concurrency Control & Thread Safety
To prevent double-spend vectors, multi-request lag exploitations, or race-conditions while settlement procedures execute (e.g., stopping copy tasks or applying liquidations), the system forces row-level database locks utilizing Django’s raw database interception layer:
```python
User.objects.select_for_update().get(id=request.user.id)

```

This guarantees an isolated state operation inside a `transaction.atomic()` context block until calculations are fully committed to the global ledger.

### 📊 Matrix Visualization Overlay (Admin vs Investor UI)

Rather than displaying a rigid layout, the front-end features an adaptive canvas system utilizing `Chart.js` combined with a responsive vector manipulation layer (`chartjs-plugin-dragdata`):

* **Admin-Root Mode:** Grants direct manipulation arrays. Administrators can drag nodes across a strict constraint grid ($-100\%$ to $+1000\%$). Saving the chart transmits the absolute raw sequence into a unified Django `JSONField` while continuously adapting the final `roi_30d` index automatically.
* **Investor Mode:** Locks drag physics completely. Restructures vectors into custom data slices over a localized state machine ($1\text{D}$, $7\text{D}$, $30\text{D}$) accompanied by smooth ease-out transitions and neon glowing cyber-gradients.

---

## ⚙️ Technical Blueprint & Stack Components

* **Core Framework:** Python 3.12+ / Django 6.0.1 (Strictly decoupled architecture utilizing layered application wrappers).
* **Asynchronous Integration & Price Ingestion:** Native abstract services interface connecting seamlessly with dynamic crypto data endpoints.
* **Frontend Infrastructure:** Semantic HTML5 modules wrapped inside high-performance responsive flexgrids, vanilla ES6 JavaScript engines handling secure AJAX token streams.
* **Data Persistence Engine:** Structured schema design configured for immediate PostgreSQL deployment (SQLite fallback provided for decoupled local debugging environments).

---

## 📁 Repository Directory Blueprint

```plaintext
smart-trade-dashboard/
│
├── apps/
│   ├── trading/         # Handles position links, PnL math, and lead vector overrides
│   ├── accounts/        # Manages session controls, tracking protocols, and permissions
│   └── transactions/    # Controls global accounting ledger structures and validations
│
├── core/                # System core configurations and security settings
├── static/              # Production asset compilations (CSS variables, Cyberpunk UI scripts)
├── templates/           # Split layout modules (granular admin views / clean investor dashboards)
├── manage.py
├── requirements.txt
└── .gitignore

```

---

## 🧩 Quick-Start Infrastructure Setup

### 1️⃣ Obtain Local Environment

```bash
git clone [https://github.com/MohammadSalkhorde/smart-trade-dashboard.git](https://github.com/MohammadSalkhorde/smart-trade-dashboard.git)
cd smart-trade-dashboard

```

### 2️⃣ Isolate Virtual Environment

```bash
python -m venv venv
# Activation wrapper on Windows environments
venv\Scripts\activate
# Activation wrapper on UNIX/macOS environments
source venv/bin/activate

```

### 3️⃣ Ingest Platform Prerequisites

```bash
pip install -r requirements.txt

```

### 4️⃣ Map Structural Relations

```bash
python manage.py makemigrations
python manage.py migrate

```

### 5️⃣ Boot Local Host Node

```bash
python manage.py runserver

```

The node will bind actively to your loopback address. Direct your browser agent to: **`http://127.0.0.1:8000/`**

---

## 📄 Licensing

Distributed under the **MIT License**. Check the root license configuration bundle for precise implementation rights.

---

## 💼 Developer Credentials & Technical Vector

**Mohammad Salkhorde** *Python / Django Back-End Engineer & Software Architect*

* **GitHub:** [github.com/MohammadSalkhorde](https://github.com/MohammadSalkhorde)
* **LinkedIn:** [linkedin.com/in/mohammad-salkhorde-a13767385](https://www.linkedin.com/in/mohammad-salkhorde-a13767385)
* **Professional Portfolio:** [mohammad-salkhorde.ir](https://mohammad-salkhorde.ir)
* **Direct Network Access:** m.salkhorde444@gmail.com