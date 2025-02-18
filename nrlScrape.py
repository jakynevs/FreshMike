from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
import os

load_dotenv()

# Retrieve credentials path from the environment variable
creds_path = os.getenv("GOOGLE_SHEET_CREDENTIALS")

if creds_path is None:
    raise Exception("Google credentials path not set in environment variables")


def write_to_google_sheet(game_list, sheet):
    print("Writing to google sheet...")

    # Prepare data for batch insertion
    all_data = [
        [
            gameDict["dateTime"],
            gameDict["home_team"],
            gameDict["away_team"],
            gameDict["home_score"],
            gameDict["away_score"],
            gameDict["total_points"],
            gameDict["home_first_half"],
            gameDict["away_first_half"],
            gameDict["home_second_half"],
            gameDict["away_second_half"],
        ]
        for gameDict in game_list
    ]

    # Insert all data below the header starting from row
    sheet.insert_rows(all_data, 2)
    print("Data written to Google Sheet.")


def scrape_and_paste():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.route(
            "**/*",
            lambda route: (
                route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font"]
                else route.continue_()
            ),
        )
        url = "https://www.flashscore.co.uk/rugby-league/australia/nrl/results/"
        page.goto(url)

        # Define the scope (access level)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Path to your service account key file
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

        # Authorize and connect
        client = gspread.authorize(creds)

        # Open Google Sheet by its name or by the URL
        sheet = client.open("NRL Data").worksheet("Test")

        last_update = sheet.acell("A2").value
        last_update_obj = datetime.strptime(last_update, "%d/%m/%y")
        end_of_preseason_obj = datetime.strptime("01/03/25", "%d/%m/%y")

        try:
            page.click("#onetrust-reject-all-handler")
        except:
            pass  # If no banner, skip

        # Get the content of the page
        content = page.content()

        soup = BeautifulSoup(content, "html.parser")

        games = soup.find_all("div", class_="event__match")
        game_list = []

        for game in games:
            # Extract game details
            game_date = datetime.strptime(
                f"{game.contents[2].text[:5]}.{datetime.now().year}", "%d.%m.%Y"
            ).strftime("%d/%m/%y")

            game_date_obj = datetime.strptime(game_date, "%d/%m/%y")

            if (
                game_date_obj <= last_update_obj
                or game_date_obj <= end_of_preseason_obj
            ):
                print("No new games to add.")
                break

            game_data = [g.text for g in game.contents[3:11]]  # Extract all at once

            gameDict = {
                "dateTime": game_date,
                "home_team": game_data[0],
                "away_team": game_data[1],
                "home_score": game_data[2],
                "away_score": game_data[3],
                "total_points": int(game_data[2]) + int(game_data[3]),
                "home_first_half": game_data[4],
                "away_first_half": game_data[5],
                "home_second_half": game_data[6],
                "away_second_half": game_data[7],
            }
            game_list.append(gameDict)

        if game_list:
            write_to_google_sheet(game_list, sheet)

        # Close the WebDriver
        browser.close()


if __name__ == "__main__":
    print("FreshMikeScript is running...")
    scrape_and_paste()
    print("FreshMikeScript finished.")
