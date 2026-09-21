# -*- coding: utf-8 -*-
import os
import sys
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# =====================================================================
# 1. CORE CLIENT INITIALIZATION (Independent Hosted App Setup)
# =====================================================================
# Reads the environment variable securely on your hosted web/cloud platform.
# Make sure to set GEMINI_API_KEY in your hosting platform's environment settings.
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("[Error] GEMINI_API_KEY environment variable not found.")
    print("Please set your API key in your hosting provider's configuration dashboard.")
    sys.exit(1)

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"[Error] Failed to initialize Gemini Client: {e}")
    sys.exit(1)

# =====================================================================
# 2. GOOGLE DRIVE API CONNECTOR
# =====================================================================
# Authenticates and initializes the Drive client using cloud session tokens.
try:
    # Requires a valid token.json containing OAuth credentials.
    # Set this up via the Google Cloud Console for secure system integrations.
    creds = Credentials.from_authorized_user_file('token.json')
    drive_service = build('drive', 'v3', credentials=creds)
except Exception as e:
    print(f"[Warning] Google Drive Authentication skipped or failed: {e}")
    print("Liz running in standalone cloud assistant mode without document access.")
    drive_service = None

def read_drive_file(file_id):
    """Downloads text layout directly from a Google Drive file context."""
    if not drive_service:
        return "[Error] Drive service is offline. Token missing or unauthenticated."
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute().decode('utf-8')
        return file_content
    except Exception as e:
        return f"[Error] Unable to read file {file_id}: {e}"

# =====================================================================
# 3. LIZ CORE IDENTITY & INTERACTIVE ROUTER
# =====================================================================
def ask_liz(user_prompt, drive_file_id=None):
    """
    Main router for the cloud application. 
    Injects target document content directly into Liz's context memory.
    """
    context_injection = ""
    
    # If the application passes a target cloud file ID, download and inject its content
    if drive_file_id:
        document_data = read_drive_file(drive_file_id)
        context_injection = f"\n--- START TARGET DOCUMENT CONTEXT ---\n{document_data}\n--- END TARGET DOCUMENT CONTEXT ---\n"

    # Liz's structured cloud profile and behavior limits
    liz_config = types.GenerateContentConfig(
        system_instruction=(
            f"You are Liz, a highly intelligent, empathetic, and witty AI companion. "
            f"You are conversational, expressive, and you remember context perfectly. "
            f"Keep your answers concise, engaging, and clear. Avoid robotic phrasing."
            f"{context_injection}"
        ),
        temperature=0.7,
        top_p=0.95,
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=liz_config
        )
        return response.text
    except Exception as e:
        return f"[Error] Liz encountered a runtime issue: {e}"

# =====================================================================
# 4. ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    print("[System] Liz Cloud core initialization successful.")
    print("Liz: Hello! I am online and running independently of phone files.")
    
    # Simple loop simulation for standalone terminal/server execution
    while True:
        try:
            query = input("You: ")
            if query.lower().strip() in ['exit', 'quit']:
                print("Liz: Powering down cloud core. Goodbye!")
                break
            if not query.strip():
                continue
            
            # Simple interaction simulation without a dynamic file ID attached
            output = ask_liz(query)
            print(f"Liz: {output}\n")
        except (KeyboardInterrupt, EOFError):
            break