
import sh
from fastapi import FastAPI, HTTPException
import requests
from stem import Signal
from stem.control import Controller
import time

app = FastAPI()


def install_and_start_tor():
    try:
        # Run apt-get update
        sh.bash("-c","apt-get update -y")

        # Install Tor
        sh.bash("-c","apt-get install tor -y")
        torrc_path='/etc/tor/torrc'
        with open(torrc_path, 'a') as torrc:
                torrc.write("#ControlPort 9051\n#CookieAuthentication 1\n")
        with open(torrc_path, 'r') as torrc_file:
                torrc_content = torrc_file.read()
                print(torrc_content)
        # Start Tor service
        sh.bash("-c","service tor start")

        # Wait for Tor to start (you may adjust the sleep duration)
        time.sleep(5)
        sh.bash("-c","service tor stop")
        sh.bash("-c","service tor status")
    except sh.ErrorReturnCode_1 as e:
        raise HTTPException(status_code=500, detail=f"Error installing/starting Tor: {e}")

# Install and start Tor
install_and_start_tor()

def renew_tor_identity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def make_request_with_tor(url):
    proxy = "socks5://127.0.0.1:9050"  # Tor proxy address
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=5)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error using Tor proxy: {e}")

@app.get("/tor-request")
async def tor_request():
    url_to_request = 'https://api.ipify.org?format=json'
    a=make_request_with_tor(url_to_request)
    return {"message": "Request made through Tor","ki":a}

@app.get("/renew-identity")
async def renew_identity():
    renew_tor_identity()
    return {"message": "Tor identity renewed"}
