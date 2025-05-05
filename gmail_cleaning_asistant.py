from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import base64
import email
import streamlit as st

# To run this application in browser:
# 1. Save this file
# 2. Open a terminal/command prompt
# 3. Navigate to the directory containing this file
# 4. Run the command: streamlit run gmail_cleaning_asistant.py
# 5. A browser window will automatically open with the application

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_email_content(subject, content, size):
    prompt = f"""
    Analyze this email and categorize it based on the following criteria:
    1. Subject: {subject}
    2. Content: {content}
    3. Size: {size} bytes

    Categorize into one of these categories and provide a brief reason:
    - CRITICAL (important business/personal communications)
    - KEEP (useful but not critical)
    - DELETE (promotional, spam, outdated, or redundant)

    Consider the email size when making recommendations for deletion to save storage.
    Respond in format: CATEGORY | Reason
    """
    
    response = model.generate_content(prompt)
    return response.text

def get_gmail_service(credentials_file):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=51744)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    # Limit to first 10 emails for cost control
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    email_details = []
    
    total_emails = len(messages)
    st.warning(f"⚠️ For cost control, analyzing only {total_emails} most recent emails.")
    
    with st.spinner('Fetching emails...'):
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg['payload']
            headers = payload['headers']
            
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            
            if 'parts' in payload:
                parts = payload['parts']
                content = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        content += base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = payload['body'].get('data', '')
                content = base64.urlsafe_b64decode(data).decode('utf-8')
                
            size = msg['sizeEstimate']
            
            # Truncate content to reduce token usage
            content = content[:500] + '...' if len(content) > 500 else content
            
            email_details.append({
                'id': message['id'],
                'subject': subject,
                'content': content,
                'size': size
            })
            
            # Add progress bar
            progress_text = f'Analyzing email {len(email_details)}/{total_emails}'
            progress_bar = st.progress(0)
            progress_bar.progress(len(email_details)/total_emails, text=progress_text)
    
    return email_details

def analyze_email(email_detail):
    result = analyze_email_content(
        email_detail['subject'],
        email_detail['content'],
        email_detail['size']
    )
    
    # Handle different response formats
    if ' | ' in result:
        category, reason = result.split(' | ', 1)
    else:
        # If the model didn't use the expected format, make a best effort to extract category
        if 'CRITICAL' in result:
            category = 'CRITICAL'
        elif 'KEEP' in result:
            category = 'KEEP'
        elif 'DELETE' in result:
            category = 'DELETE'
        else:
            category = 'KEEP'  # Default to KEEP if unclear
        
        reason = result  # Use the full response as the reason
    
    return {
        'id': email_detail['id'],
        'category': category,
        'reason': reason,
        'size': email_detail['size']
    }

def process_emails(service, email_details):
    analysis_results = []
    with st.spinner('Analyzing emails...'):
        for email_detail in email_details:
            result = analyze_email(email_detail)
            analysis_results.append(result)
    
    total_saved = 0
    delete_recommendations = []
    
    for result in analysis_results:
        if result['category'] == 'DELETE':
            total_saved += result['size']
            delete_recommendations.append({
                'id': result['id'],
                'reason': result['reason'],
                'size': result['size']
            })
    
    st.subheader("Storage Cleanup Recommendations")
    st.write(f"Total space that can be saved: {total_saved / 1024 / 1024:.2f} MB")
    
    st.subheader("Emails recommended for deletion:")
    for rec in delete_recommendations:
        st.write(f"- {rec['reason']} (Size: {rec['size'] / 1024:.2f} KB)")
        
    if st.button("Proceed with Deletion"):
        with st.spinner("Deleting emails..."):
            for rec in delete_recommendations:
                service.users().messages().trash(userId='me', id=rec['id']).execute()
            st.success(f"Successfully cleaned up {total_saved / 1024 / 1024:.2f} MB of storage")

def main():
    st.title("Gmail Storage Cleanup Assistant")
    
    st.write("""
    This app helps you analyze and clean up your Gmail storage by identifying emails that can be safely deleted.
    Please upload your Gmail API credentials file to get started.
    
    ⚠️ Usage Limits:
    - Analyzes up to 10 most recent emails
    - Content is truncated to 500 characters
    - Uses Google's Gemini Pro model for analysis
    """)
    
    credentials_file = st.file_uploader("Upload Gmail API credentials (JSON)", type=['json'])
    
    if credentials_file:
        # Save the uploaded credentials temporarily
        with open('credentials.json', 'wb') as f:
            f.write(credentials_file.getvalue())
            
        try:
            service = get_gmail_service('credentials.json')
            
            # Execute the pipeline
            email_details = fetch_emails(service)
            process_emails(service, email_details)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up the temporary credentials file
            if os.path.exists('credentials.json'):
                os.remove('credentials.json')

if __name__ == "__main__":
    main()
