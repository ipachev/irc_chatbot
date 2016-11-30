from bs4 import BeautifulSoup
import wikipedia
import nltk.data
import re
import urllib


lst = ""
name = ""

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

txt = None
with urllib.request.urlopen(lst) as response:
    txt = f.response()
soup = BeautifulSoup(txt, "lxml")
data = soup.findAll("a")

i = 0
with open("data/" + name + ".csv", 'w') as f:
    for article in data:
        url = article["href"]
        title = article.text
        try:
            summary = wikipedia.summary(title)
            summary = re.sub(r'\s\([^)]*\)', "", summary)
            sent = sent_detector.tokenize(summary)[0]
            f.write(title + "~~" + sent + "\n")
        except:
            print("FAIL :(")
        i += 1
        print(str(i) + ": " + title)
