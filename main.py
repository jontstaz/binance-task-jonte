# Import the necessary modules
import os
from os.path import join, dirname
from dotenv import load_dotenv
import asyncio
import websockets
import json
import os
import requests
import locale
import time
import hmac
import signal
import hashlib
import re
from urllib.parse import urljoin, urlencode

# ctrl-c handler
def handler(signum, frame):
    res = input("Do you want to exit the program? y/n ")
    if res == 'y':
        exit(1)
signal.signal(signal.SIGINT, handler)

# Function to execute orders on Testnet
def makeOrder():
    timestamp = int(time.time() * 1000)
    # Order parameters for the API request
    params = {
        'symbol': 'ETHUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.1,
        'price': 500.0,
        'recvWindow': 5000,
        'timestamp': timestamp
    }
    query_string = urlencode(params)
    # Encode the API secret along with the order parameters to create the signature
    params['signature'] = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    # Set the URL to correct API Endpoint
    url = urljoin(BINANCE_API_ROOT, ORDER_PATH)
    # Make the request to the API
    r = requests.post(url, headers=headers, params=params)
    # Return the execution time in milliseconds
    return round(time.time() * 1000)

# Define the asynchronous function to handle the websocket messages
async def socket():
    # Set the locale for the Websocket connection
    locale.setlocale(locale.LC_ALL, 'en_AU.UTF-8')
    # Set the URL to correct Websocket Endpoint
    uri = DATA_STREAM_ENDPOINT + '/' + listenKey
    # Initialise the trade counter
    totalTrades = 0
    # Connect to the Websocket
    async with websockets.connect(uri) as websocket:
        print("Established connection to websocket. Listening for messages... Press Ctrl+C to exit.\n")
        # Subscribe to the websocket
        while True:
            # Wait for the message to be received
            message = await websocket.recv()
            # Parse the message into a JSON object
            data = json.loads(message)
            # Check if the message is an executionReport and execution type is TRADE
            if data['e'] == 'executionReport' and data['x'] == 'TRADE':
                # A message matching the criteria has been received
                print("Execution Report Event Identified!")
                # Calculate the delay between the time recorded by the program when the order was placed and the execution time reported by the websocket message 
                delayDetected = data['E'] - tradeTimes[totalTrades]
                print("Delay between actual trade time and event time from websocket message:", delayDetected, "ms")
                # If the delay is greater than the desired delay, print a warning message
                if delayDetected > delay:
                    print("The delay is greater than the delay of", delay, "ms!!!\n")
                else:
                    print("The delay is less than the delay of", delay, "ms.\n")
                # Increment the trade counter
                totalTrades += 1

# Asynchronous unction which executes orders on Testnet every 30 seconds
async def makeOrders():
    while True:
        # Wait x seconds before making order
        await asyncio.sleep(orderInterval)
        print("Making testnet order...")
        # Make the order by calling the makeOrder function from the testOrder.py file and add the real time of trade to the tradeTimes list
        tradeTimes.append(makeOrder())

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
API_KEY = str(os.environ.get("API_KEY"))
API_SECRET = str(os.environ.get("API_SECRET"))

# Sanitise and record user input for the X ms delay
print("Enter the desired delay in milliseconds:")
# Initialise the variables
flag = True
delay = None
while flag:
    # Get user input
    delay = input()
    # Define regex to check if the input is a number
    matchValue = re.match("[-+]?\\d+$", delay)
    if matchValue is None:
        # If the input is not a number, ask the user to enter a valid integer
        print("Please enter a valid integer.")
    elif int(delay) < 100:
        # If the input is a number but less than 100ms, ask the user to enter a valid integer > 100ms
        print("Please enter a delay greater than 100ms:")
    else:
        # User input is acceptable, exit out of the while loop
        flag = False
# Set the delay variable to the user input, converting it to an integer
delay = int(delay)

# Sanitise and record user input for the time interval between orders being placed
print("Enter the desired time between orders in seconds:")
flag = True
orderInterval = None
while flag:
    orderInterval = input()
    matchValue = re.match("[-+]?\\d+$", orderInterval)
    if matchValue is None:
        print("Please enter a valid integer:")
    elif int(orderInterval) < 15:
        print("Please enter an interval greater than 15 seconds:")
    else:
        flag = False
orderInterval = int(orderInterval)

# Set the API/WS Endpoints
DATA_STREAM_ENDPOINT = 'wss://testnet.binance.vision/ws'
BINANCE_API_ROOT = 'https://testnet.binance.vision'
PATH = '/api/v3/userDataStream'
ORDER_PATH = '/api/v3/order'

# Set the API Key in request header
headers = {
    'X-MBX-APIKEY': API_KEY
}

# Set the URL to correct API Endpoint
url = urljoin(BINANCE_API_ROOT, PATH)

# Make the request to the API
r = requests.post(url, headers=headers)

# Handle the response from the API to get the listenKey
if r.status_code == 200:
    data = r.json()
    listenKey = data['listenKey']
else:
    raise Exception(r.text)

# Initialise the global tradeTimes list for storing the real local execution times of trades
global tradeTimes
tradeTimes = []
    
# Run the 2 asynchronous functions, socket and makeOrders, in parallel
asyncio.get_event_loop().run_until_complete(asyncio.wait([   
   socket(),
   makeOrders()
]))

