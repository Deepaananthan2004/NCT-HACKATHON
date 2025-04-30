import requests

PINATA_API_KEY = '5211a52676fc504d5a6e'
PINATA_SECRET_API_KEY = '2387732948162f4adf6a25dc2b1fcfb32c287f211d9a9bbeb1224da0765a9c4f'

def upload_to_ipfs(filepath):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    with open(filepath, 'rb') as file:
        response = requests.post(url, files={"file": file}, headers=headers)

    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    else:
        raise Exception("Failed to upload to IPFS: " + response.text)