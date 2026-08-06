import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALFILE = "C:\\Users\\tripa\\OneDrive\\Desktop\\project\\secret\\client_secret_941410077075-0qgjm1sjg0ab5hmpeoag8o9n3cgo35k1.apps.googleusercontent.com.json"

def main():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALFILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        # print(labels)

        # Define the label you want to retrieve emails from (e.g., "inbox" or a custom label)
        label_id = "INBOX"

        messages = service.users().messages().list(userId='me', labelIds=[label_id]).execute()
        message_list = messages.get('messages', [])

        if not message_list:
            print('No matching emails found.')
        else:
            for message_info in message_list:
                message = service.users().messages().get(userId='me', id=message_info['id']).execute()


                # Check if 'subject' field exists in the message
                subject = message.get('Subject', 'Subject not found')
                
                
                # Check if 'from' field exists in the message
                sender = message.get('From', 'Sender not found')


                # Print the subject and sender, or default messages if not found
                #print('Subject:', subject)
                #print('From:', sender)
                #print('Message Body:', message.get('snippet', 'Snippet not found'))
                print(message) #---> gives json file


    except HttpError as error:
        print(f'An error occurred: {error}')

    except KeyboardInterrupt:
        print('Terminating Skynet')


if __name__ == '__main__':
    main()

