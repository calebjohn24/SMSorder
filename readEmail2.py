import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

hotel_rev = ["with no"]

sid = SentimentIntensityAnalyzer()
for sentence in hotel_rev:
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in ss:
        print((k, ss[k]))

