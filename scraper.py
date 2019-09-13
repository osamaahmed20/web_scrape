import requests
from bs4 import BeautifulSoup


URL = "https://www.amazon.com/Cancelling-Headphones-Bluetooth-Microphone-Comfortable/dp/B019U00D7K"

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

price = soup.find(id = 'priceblock_ourprice').get_text()
price = price[1:]
price_conv = float(price)
print(price_conv)
