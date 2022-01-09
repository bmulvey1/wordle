from functools import cache
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
import requests
import random
import re
from cachetools import cached, TTLCache
from itertools import groupby


def filter_words(inp):
    for word in inp:
        if regex.match(word) is None:
            yield word


regex = re.compile(r'.*(.).*\1.*')

@cached(cache=TTLCache(maxsize=1, ttl=86400))
def get_words():
    word_site = "http://www.instructables.com/files/orig/FLU/YE8L/H82UHPR8/FLUYE8LH82UHPR8.txt"
    site = requests.get(word_site)
    words = site.text.splitlines()
    w_5let = list(filter(lambda x: len(x) == 5, words))
    return list(filter_words(w_5let))


 # x: [letter, letter], y: [[letter, pos], [letter, pos]], g: [[letter, pos], [letter, pos]]
def filter_words(x, y, g, words):
    # remove words w/ invalid letters
    new = [ele for ele in words if all(char not in ele for char in x)]
    # remove words w/ yellow in same pos

    # remove words without green in same pos



w_5let_clean = get_words()

service = Service(executable_path=GeckoDriverManager().install())


driver = webdriver.Firefox(service=service)

# go to wordle page
driver.get("https://www.powerlanguage.co.uk/wordle/")

# need to close initial dialog, button @ <body class="nightmode">/<game-app>/#shadow-root/<game-theme-manager>/<div id="game">/<game-modal open="">/#shadow-root/<div class="overlay">/<div class="content">/<div class="close-icon">/<game-icon icon="close">
# need to repeatedly switch host context
# game-app -> shadow
#   game-modal -> shadow
#       button
sleep(2)

button = driver.execute_script("document.querySelector('game-app').shadowRoot.querySelector('game-modal').shadowRoot.querySelector('game-icon').click()")

driver.find_element('tag name', 'body').send_keys(random.choice(w_5let_clean) + Keys.ENTER)



