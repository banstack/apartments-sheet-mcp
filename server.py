import os
from datetime import datetime
from operator import add

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Required Google APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
SHEET_NAME = os.environ.get("SHEET_NAME", "NYC Apartment Listings")

# Initialize the MCP server — this is the object Claude talks to
mcp = FastMCP("nyc-apartment-tracker")


# Get Google Sheet
def get_sheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


@mcp.tool()
def saveListing(
    address: str,
    neighborhood: str,
    price: str,
    beds_baths: str,
    url: str,
    broker_email: str = "",
    notes: str = "",
) -> str:
    """Save a new apartment listing to the specified Google Sheet"""
    try:
        # TODO: Add duplicate check
        sheet = get_sheet()

        # Duplicate check
        existing = sheet.get_all_records()
        for row in existing:
            if (
                address.lower() in row["Address"].lower()
                or row["Address"].lower() in address
            ):
                return (
                    f"Duplicate found : '{row['Address']} is already saved\n"
                    f"Use update_listing to make changes, or confirm you want to save anyway."
                )
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [
            address,
            neighborhood,
            price,
            beds_baths,
            url,
            "New",  # default status
            broker_email,
            notes,
            timestamp,
        ]
        # Append to row
        sheet.append_row(row)
        return f"Saved: {address} ({neighborhood}) at {price}"
    except Exception as e:
        return f"Error saving listing: {str(e)}"


@mcp.tool()
def get_listings(
    neighborhood: str = "",
    status: str = "",
) -> str:
    """Get apartment listings. Optionally filter by neighborhood or status"""

    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()

        if neighborhood:
            rows = [
                r for r in rows if neighborhood.lower() in r["Neighborhood"].lower()
            ]
        if status:
            rows = [r for r in rows if status.lower() in r["Status"].lower()]

        # Check if listings exist given some filter(s)
        if not rows:
            return "No listings found matching your filters."

        output = []
        for i, r in enumerate(rows, 1):
            output.append(
                f"{i}. {r['Address']} — {r['Neighborhood']}\n"
                f"- {r['Price']} | {r['Beds/Baths']} | Status: {r['Status']}\n"
                f"- {r['URL']}\n"
                f"- {r['Notes']}"
            )
        return "\n\n".join(output)
    except Exception as e:
        return f"Error fetching listings: {str(e)}"


@mcp.tool()
def update_listing(address: str, field: str, new_value: str) -> str:
    """Update a field on an existing listing. Find it by address.
    Valid fields: Neighborhood, Price, Beds/Baths, URL, Status, Broker Email, Notes
    Valid statuses: New, Contacted, Visited, Pass, Apply
    """
    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()

        # Find the row number (offset by 2: where 1 is for header, and 1 for 1-indexing)
        row_num = None
        for i, r in enumerate(rows, 2):
            if address.lower() in r["Address"].lower():
                row_num = i
                break

        if not row_num:
            return f"No listing found matching '{address}'"

        # Map field name to column number
        headers = sheet.row_values(1)
        if field not in headers:
            return f"Invalid field '{field}'. Valid fields {', '.join(headers)}"

        # Update field with new value
        col_num = headers.index(field) + 1
        sheet.update_cell(row_num, col_num, new_value)

        # Update the last updated timestamp
        ts_col = headers.index("Last Updated") + 1
        sheet.update_cell(row_num, ts_col, datetime.now().strftime("%Y-%m-%d %H:%M"))

        return f"Updated '{field}' to '{new_value}' for {address}"
    except Exception as e:
        return f"Error updating listing {str(e)}"


@mcp.tool()
def delete_listing(address: str) -> str:
    """Delete a listing from the sheet by address"""
    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()

        row_num = None
        # Figure out which row number listing to delete is
        for i, r in enumerate(rows, 2):
            if address.lower() in r["Address"].lower():
                row_num = i
                break
        # If row does not exist then alert user
        if not row_num:
            return f"No listing found matching '{address}'"

        # Delete row
        sheet.delete_rows(row_num)
        return f"Deleted listing for '{address}'"
    except Exception as e:
        return f"Error deleting listing: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
