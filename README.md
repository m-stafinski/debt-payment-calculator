# Debt Payment Calculator
 A simple and interactive debt payment calculator built with Python and Streamlit. This project allows users to input various debt parameters (e.g., principal, interest rate, payment amount) and visualize their repayment schedule, helping them strategize their debt management.

## Streamlit Demo

[https://debt-payment-calculator.streamlit.app/](https://debt-payment-calculator.streamlit.app/)

## Getting Started

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

**Install dependencies:**

```bash
pip install -r requirements.txt
```
or
```bash
pip install streamlit streamlit-tags
```

---

## Usage

After installation, launch the Streamlit app:


```bash
streamlit run debt_calc.py
```

This will open the calculator in your web browser. You can then interact with the input fields and view the results.

### Sidebar

Fill all necessary information about you loan.

Payment Holiday - is a short-term pause from your monthly payments

### Main Window

Fill all necessary information about:
- addtional principle payment
    - for example if you would like to make an additional lump sum payment of 10 000 in March 2026, then add **2026-03,10000**
- adjustable rate
    - for example if your adjustable rate have increased by +0,25% in March 2026, then add **2026-04,0.0025**. You should provide the month when the change will have an impact on the interest rate.
    In case of decrease use minus sign **2026-04,-0.0025**.
- short term
    - for example if you would like to short the term of the loan by 5 years (60 months), then add **2026-03,60**. Make sure that the value will be **positive** months number of the period.

#### Metrics

- Total Interest - how much insterests you will pay for loan

- Payoff Date - date when loan will be fully paid

- Sum of Additional Payments - payment you have provided previously

- Percent of Additional Payments - how much did you paid by addtional payments. Example you have 250 000 to pay, 150 000 you paid by addtional payments (60%), 100 000 you pain within installements (40%)

#### Charts

- Overall sum of interests you will pay and how much principle is left

- Changes for monthly installement.
    - If you change in settings 
    - [ ] Show % of principle in installement
    - Then it will show what is the percentage of principle in the installement.

#### Tables

- Details about all monthly installements after all calculations

- The same information without calculations of addtional payment and short term (the adjustble rate changes will be calculated)

#### Disclaimer
This debt calculator (the "Tool") is provided for informational and educational purposes only.


