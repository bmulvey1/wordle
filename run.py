from functools import cache
from math import pi
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
import requests
import random
from cachetools import cached, TTLCache
from itertools import groupby


@cached(TTLCache(maxsize = 1,ttl=86400))
def get_words():
    word_site = "https://gist.githubusercontent.com/bmulvey1/224dd1610f54e7d792589ee08c2f6399/raw/e8cebe9330a5b13157fdc015156673ced900c477/wordlist"
    site = requests.get(word_site)
    words = site.text.splitlines()
    return words


 # x: [letter, letter], y: [[letter, pos], [letter, pos]], g: [[letter, pos], [letter, pos]]
def filter_letters(x, y, g, words):
    # remove words w/ invalid letters
    new = [ele for ele in words if all(char not in ele for char in x)]
    # remove words w/ yellow in same pos but yellow in word
    # has same issue as green
    new1 = []
    if y == []:
        new1 = new
    else:

        for word in new:
            all_in = True
            for group in y:
                if (group[0] not in word) or (word[group[1]] == group[0]):
                    all_in = False
            if all_in and word not in new1:
                new1.append(word)
    # remove words without green in same pos
    new3 = []
    if g == []:
        new3 = new1
    else:
        for word in new1:
            all_in = True
            for group in g:
                if word[group[1]] != group[0]:
                    all_in = False
            if all_in and (word not in new3):
                new3.append(word)

    print(len(new), len(new1), len(new3))

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
    global eliminated

    for idx, i in enumerate(row):
        if i == "absent":
            x.append(word[idx])
            eliminated.append(word[idx])
        if i == "present":
            y.append([word[idx], idx])
        if i == "correct":
            g.append([word[idx], idx])
    

    print(word)
    print(x)
    print(y)
    print(g)

    return x,y,g


eliminated = []

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
#sleep(2)

driver.execute_script("document.querySelector('game-app').shadowRoot.querySelector('game-modal').shadowRoot.querySelector('game-icon').click()")

wordlist = w_5let_clean

for i in range(1,7):
    x,y,g = process_word(wordlist, i, driver) 
    wordlist = filter_letters(x,y,g,wordlist)
    print(eliminated)
    if(len(g)==5): # every letter is correct, terminate
        exit()
    sleep(2)
