This project implements a 'Newton–Raphson'–based root finder for 'arbitrary-degree polynomials' using a 'Horner-evaluated polynomial' and its analytical derivative.  
It’s an educational numerical methods project with a simple interactive interface, an optional plot, and a guardrail to stop after 15 seconds.

---

What it does

- Accepts any polynomial degree ≥ 2
- Accepts coefficients interactively (highest degree first)
- Plots the polynomial curve for a quick visual
- Uses 'Newton–Raphson' iteration to find a 'real root' from a user-provided initial guess
- Gathers 'unique roots' discovered until:
  - it finds as many unique roots as `degree`, or
  - 15 seconds elapse (safety timeout)
- Prints roots rounded to 4 decimal places

---

Tech Stack

- Python 3.8+
- `numpy`, `matplotlib`

---

How to Run (CLI)

```bash
# 1) Create environment (optional)
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run
python main.py
