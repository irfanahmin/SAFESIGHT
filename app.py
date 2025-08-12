from flask import Flask, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(_name_)
CORS(app)  # Enable CORS

# Load Twilio credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")
TO_WHATSAPP = os.getenv("RECIPIENT_WHATSAPP_NUMBER")

@app.route('/')
def home():
    return '''
    <h1>Emergency Alert System</h1>
    <script>
        function fetchLocationAndSend() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    const locationLink = https://www.google.com/maps?q=${latitude},${longitude};
                    
                    fetch("/send_alert", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ latitude, longitude, locationLink })
                    }).then(response => response.json())
                      .then(data => document.getElementById("status").innerHTML = data.message)
                      .catch(error => console.error("Error:", error));
                }, function(error) {
                    console.error("Location error:", error);
                    document.getElementById("status").innerHTML = "Failed to get location.";
                });
            } else {
                document.getElementById("status").innerHTML = "Geolocation not supported.";
            }
        }
        fetchLocationAndSend();
    </script>
    <div id="status">Fetching location...</div>
    '''

@app.route('/send_alert', methods=['POST'])
def send_alert():
    try:
        # Retrieve location from request
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_link = data.get('locationLink')

        print(f"Received Location: {latitude}, {longitude}")  # Debugging

        # Check if Twilio credentials exist
        if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_WHATSAPP, TO_WHATSAPP]):
            raise ValueError("Missing Twilio credentials!")

        # Send WhatsApp alert via Twilio
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=f"Emergency Alert!\nLocation: {location_link}",
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )

        print(f"Message Sent! SID: {message.sid}")  # Debugging
        return jsonify({"message": "Alert sent successfully!", "sid": message.sid}), 200
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True, host="0.0.0.0", port=5000)