#!/usr/bin/env python3
"""
Simple SMTP server for testing email functionality.
Receives emails and prints them to console.
Run this server on a separate terminal before testing password reset.
"""

import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

class EmailHandler(Message):
    """Handler that prints received emails to console."""
    
    def handle_message(self, message):
        """Print the received email message."""
        print("\n" + "="*60)
        print("EMAIL RECEIVED!")
        print("="*60)
        print(f"From: {message.get('From', 'Unknown')}")
        print(f"To: {message.get('To', 'Unknown')}")
        print(f"Subject: {message.get('Subject', 'No Subject')}")
        print("-"*60)
        print("Body:")
        body = message.get_body()
        if body:
            print(body.get_content())
        print("="*60 + "\n")

def main():
    """Start the SMTP server."""
    print("Starting SMTP server on localhost:1025...")
    print("This server will receive and display emails.")
    print("Press Ctrl+C to stop.")
    
    handler = EmailHandler()
    controller = Controller(handler, hostname='localhost', port=1025)
    controller.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\nStopping SMTP server...")
        controller.stop()

if __name__ == '__main__':
    main()
