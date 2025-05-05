# Gmail Cleaning Assistant

A smart email management tool that helps you reclaim storage space in your Gmail account by identifying emails that can be safely deleted.

## Features

- **AI-Powered Analysis**: Uses Google's Gemini AI to categorize emails as:
  - CRITICAL (important business/personal communications)
  - KEEP (useful but not critical)
  - DELETE (promotional, spam, outdated, or redundant)
- **Smart Recommendations**: Analyzes email content, subject lines, and sizes to make deletion suggestions
- **Storage Metrics**: Shows potential space savings from recommended deletions
- **Selective Deletion**: Choose which emails to delete from recommendations (rather than deleting all at once)
- **Secure Authentication**: Uses OAuth for secure access to your Gmail account

## Getting Started

### Prerequisites

1. Python 3.7 or higher
2. A Google Cloud Platform account
3. Gmail API credentials

### Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up Google Cloud credentials:
   - Create a project in Google Cloud Console
   - Enable the Gmail API
   - Create OAuth credentials and download the JSON file

### Running the Application

```bash
streamlit run gmail_cleaning_assistant.py
```

The app will open in your default web browser. Upload your credentials file when prompted and follow the on-screen instructions.

## Usage Limits

For performance and cost optimization:
- Analyzes up to 10 most recent emails by default
- Content is truncated to 500 characters per email for analysis
- Uses Google's Gemini model for email categorization

## Screenshots

[Screenshot of the UI showing the email selection interface]

## Privacy & Security

- Your email data is processed locally
- Credentials are temporarily stored during execution only
- The app uses secure OAuth authentication with Gmail
- No email content is permanently stored

## License

MIT