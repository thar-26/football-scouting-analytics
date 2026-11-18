\# Football Scouting \& Market Intelligence Dashboard



A data-driven player scouting system

analytics department. Find undervalued players, analyse performance metrics, 

identify similar players in cheaper markets, and generate automated scouting reports.



\---



\## What it does



\*\*Undervalued Player Finder\*\*

Surfaces players performing above their market value using per-90 metrics 

and opportunity scoring — the core of FCM's transfer philosophy. Click any 

player to instantly see their full profile.



\*\*Player Profile\*\*

Deep dive into any player across 47,000+ in the database. Radar charts, 

career stats, contract info, and market valuation in one view.



\*\*Similar Player Finder\*\*

Input any player and find statistically similar alternatives in cheaper 

markets using cosine similarity across key performance features.



\*\*Scouting Report Generator\*\*

Auto-generates a professional scouting report with strengths, weaknesses, 

value assessment, and a SIGN / MONITOR / PASS recommendation.



\---



\## How to run



```bash

git clone https://github.com/thar-26/football-scouting-analytics

cd football-scouting-analytics

pip install pandas numpy plotly streamlit scikit-learn

```



Download the dataset from Kaggle:

https://www.kaggle.com/datasets/davidcariboo/player-scores



Place all CSV files in the project folder, then:



```bash

streamlit run app.py

```



\---



\## Data



47,000+ players · 616,000+ valuations · 1.8M appearances

Source: Transfermarkt via Kaggle (davidcariboo/player-scores)



\---







\---



\## Stack

Python · Pandas · Plotly · Streamlit · Scikit-learn

