**NRL Web Scraping Program**
This is a web scraping program that collects data on all NRL games from Flashscore, starting from the last game recorded in a private Google Sheet. The program is designed to help a professional gambler by automatically updating weekly results for use in a predictive model.

***Features:***
Scrapes NRL game data from Flashscore.
Tracks and records games since the last entry in a private Google Sheet (can be modified for personal use).
Provides updated results each week to support betting model predictions.
***Usage:***
Set up the required dependencies with pip install -r requirements.txt.
Replace the service account JSON credentials with your own in the script.
Change the Google Sheet name in the script (NRL Data) to your own if necessary.
Run the script using python nrlScrape.py.
The data will be added to your Google Sheet for future reference.
***Note:***
This script currently works with a private Google Sheet. You can modify the sheet name and credentials to adapt it for personal use.
