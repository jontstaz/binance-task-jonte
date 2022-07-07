# Binance API Solutions Engineer - Coding Task

## Description
This program utilises the Binance Testnet REST API and Websocket userDataStream feed to place orders and specifically monitors the `executionReport` websocket message type. First it records the exact timestamp in milliseconds for when the order is sent to the Binance REST API order endpoint. Whilst this is happening, the program is subscribed to the userDataStream websocket and waiting for a `executionReport` event for a `TRADE`. Once the matching executionReport message is received, the initial timestamp of when the order is placed is compared with the timestamp listed in the `executionReport` websocket message. If the delay is greater than the user-defined `X ms`, it will alert the user to this fact.

## How To Use
- Open your terminal of choice
- Clone this repository by running `git clone <INSERT_REPO_URL>`
- Install the dependencies by running `pip install -r requirements.txt`
- Edit the `.env` file by replacing the values as outlined below
    - Enter your testnet API Key 
    - Enter your testnet API Secret Key
```
API_KEY = <INSERT_TESTNET_API_KEY>
API_SECRET = <INSERT_TESTNET_API_SECRET_KEY>
```
- Execute the program by running `python main.py`
- You will be prompted to enter the `X ms` delay (*minimum 100ms*)
- You will also be prompted to determine the interval (in seconds) on which orders are created. (*minimum 15secs*) Eg. orders will be made every `20 seconds`. 

## Software Requirements
The software requirements were given to me exactly as outlined below:
```
Write a small app that can monitor the executionReport websocket message delay for X ms.  If your order is matched, there will be a message with event type executionReport gives many details. We want to have a small application that can alert us if the Event time is delivered delayed over X ms. 

testnet(https://testnet.binance.vision/) has the free funds to trade. 

* X is configable, so I can set to 5000ms or 10000ms, etc. 
* Should not use any pre-build library related to Binance or other crypto exchanges 
* Language is not limited, but please give details of how to run. 
* UI is not required, running from terminal is enough.
```