from functools import cache
from math import pi
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
def filter_letters(x, y, g, words):
    # remove words w/ invalid letters
    new = [ele for ele in words if all(char not in ele for char in x)]
    # remove words w/ yellow in same pos but yellow in word
    new1 = []
    new2 = []
    l = lambda let, pos, w: (w[pos] != let)
    l1 = lambda let, w: let in w
    if y == []:
        new1 = new
    else:
        for group in y:
            for word in new:
                if(l(group[0], group[1], word) and word not in new1):
                    new1.append(word)
        for group in y: 
            for word in new1:
                if(l1(group[0], word) and word not in new2):
                    new2.append(word)
    # remove words without green in same pos
    new3 = []
    l2 = lambda let, pos, w: w[pos] == let
    if g == []:
        new3 = new2
    else:
        for group in g:
            for word in new2:
                if(l2(group[0], group[1], word and word not in new3)):
                    new3.append(word)
    print(len(new), len(new1), len(new2), len(new3))

    return new3

def process_word(list, num, driver):
    word = random.choice(list)
    driver.find_element('tag name', 'body').send_keys(word + Keys.ENTER)

    # get color for each letter in row 0
    # body/game-app/shadow/game-theme-manager/div/div/div/<game-row letters=word0 length="5">
    row = driver.execute_script("return document.querySelector('game-app').shadowRoot.querySelector('game-row:nth-child(%d)')._evaluation" % num)

    x = []
    y = []
    g = []

    for idx, i in enumerate(row):
        if row[idx] == "absent":
            x.append(word[idx])
        if row[idx] == "present":
            y.append([word[idx], idx])
        if row[idx] == "correct":
            g.append([word[idx], idx])

    print(word)
    print(x)
    print(y)
    print(g)

    return x,y,g

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

driver.execute_script("document.querySelector('game-app').shadowRoot.querySelector('game-modal').shadowRoot.querySelector('game-icon').click()")

wordlist = w_5let_clean

for i in range(1,6):
    x,y,g = process_word(wordlist, i, driver) 
    wordlist = filter_letters(x,y,g,wordlist)
    sleep(2)



