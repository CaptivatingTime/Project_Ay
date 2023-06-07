import requests
import json
import random
import time
def getGif(searchTerm):

    
    GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
    search_term = searchTerm

    # Define the Giphy API endpoint
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={search_term}&limit=50"

    # Send a request to the Giphy API
    response = requests.get(url)

    # Parse the response as JSON
    json_data = json.loads(response.text)

    random.seed(time.time())
    # Choose a random GIF from the list of results
    gif_url = json_data['data'][random.randint(0, len(json_data['data'])-1)]['images']['original']['url']

    # Send the GIF to the Discord channel or user
    return gif_url
