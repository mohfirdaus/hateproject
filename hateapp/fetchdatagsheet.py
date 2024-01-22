import gspread
from .models import Berita, Komentar
import os

def authenticate_google_sheets(service_account_key_path, spreadsheet_key):
    gc = gspread.service_account(filename=service_account_key_path)
    worksheet = gc.open_by_key(spreadsheet_key).sheet1
    return worksheet

def fetch_and_update_data():
    # Get the path of the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the absolute path to the service account file
    service_account_key_path = os.path.join(current_directory, 'finalproject-410112-1bb240f718e7.json')

    # Replace with your Google Sheets spreadsheet key
    spreadsheet_key = '1u8vQ1-2NKcAIScOZ3nrQNirRfBw8gsxsYBlk-g03rNY'

    worksheet = authenticate_google_sheets(service_account_key_path, spreadsheet_key)

    # Get all comments along with their related news (Berita) data
    komentar_data = Komentar.objects.select_related('berita').values()

    # Create header
    header = list(komentar_data[0].keys())

    # If the spreadsheet is empty, add the header
    if worksheet.row_count == 0:
        worksheet.append_row(header)

    # Add comment data to the Google Sheets
    for komentar in komentar_data:
        row_data = [str(komentar[field]) for field in header]
        worksheet.append_row(row_data)

    print('Data successfully updated to Google Sheets')

if __name__ == "__main__":
    fetch_and_update_data()