# Apartment Sheets MCP (AS-MCP)

A light-weight Model Context Protocol (MCP) server that lets Claude (or other platforms) to save and manage apartment listings to a shared Google Sheet.

## Background

This project has been inspired by the hectic apartment hunting process we have here in NYC.

**Why a Google Sheet?**
1. Google provides a generous API service
2. There's no easier medium to share your apartment search with your roommate(s)/partner(s)

## Notes

Because this is a MCP, use the AI platform of your choice to handle the web scraping, listing update, and more. All this MCP does is give your AI tool of choice the connectivity to your respective sheet

## Tools Available
- `save_listing` : adds a new listing to your sheet
- `get_listing` : fetches all listings, with optional filters (Neighborhod and Status today)
- `update_listing` : update any field on an existing listing
- `delete_listing` : remove a listing from the sheet

## Setup
*you have to clone this repo, duh!

### 1. Google Cloud Credentials
- Create a service account in Google Cloud Console
- Enable Google Sheets and Google Drive APIs
- Download the credentials JSON and save as `credentials.json` (place in root of project)
- Share your Google Sheet with the service account email as Editor

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Claude desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "nyc-apartment-tracker": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/server.py"],
      "cwd": "/path/to/nyc-apartment-mcp"
    }
  }
}
```

## Environment variables
| Variable | Default | Description |
|---|---|---|
| `SHEET_NAME` | `NYC Apartment Listings` | Name of your Google Sheet |

## Security Note
If you plan on pushing to git please mae sure to never commmit credentials.json!
