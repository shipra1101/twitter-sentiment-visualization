# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 20:46:22 2018

@author: deeks
"""

from flask import Flask, render_template, request, redirect, url_for, session, Markup #necessary imports
import tweepy
from textblob import TextBlob
import sys
import os
import csv
import operator
from textblob import Word
from textblob.sentiments import NaiveBayesAnalyzer
import io
import base64
import tweepy
import json
import numpy as np 
import pandas as pd
from scipy.misc import imread
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib as mpl
import matplotlib.pyplot as plt_wordcloud
import matplotlib.pyplot as plt_trend
from sqlalchemy import create_engine

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_restful import reqparse
import requests
import datetime
import time
import os
import matplotlib.pyplot as plt

from PIL import Image


IMAGE_FOLDER = os.path.join('static', 'images')


#Here we define the Twitter App Details.
consumerKey = 'a1zyInaIw7y6vzCnxtyyJ8Bkk'
consumerSecret = 'p0M5h6sZewFcCAjIdJUlPldV9S13QKwtRkh04MpoSrugGslxlA'
accessToken = '142729769-53yVD8eLUEjiUJpBcTvRVUYMmHDiqEZ7cbNN7BFs'
accessTokenSecret = 'UhcMzCrYtfzdU70vibsUQ70Vpd4UZ65cT0SBGYYgsSBXh'
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth, wait_on_rate_limit=True)

app = Flask(__name__)
app.config['IMAGES'] = IMAGE_FOLDER
api_db = Api(app)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dk488492:sameera123@cloudupload.czlq7phghrul.us-east-2.rds.amazonaws.com/awsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class SEARCH_INFO(db.Model):   
    ID = db.Column(db.Integer, nullable=False,primary_key=True)
    SEARCH = db.Column(db.String(255), nullable=False)     
    POSITIVE_VALUE = db.Column(db.Integer, nullable=False)
    NEGATIVE_VALUE = db.Column(db.Integer, nullable=False)
    NEUTRAL_VALUE = db.Column(db.Integer, nullable=False)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/sentiment_analysis", methods=['POST','GET'])
def sentiment_analysis():
        
    searchTerm = request.form['topicname']
    NumberSearchTerms = request.form['gridRadios']
    NumberSearchTerms = int(NumberSearchTerms)
    
    session['keyword'] = searchTerm
    session['number'] = NumberSearchTerms

    def percentage(part, whole):
        return 100 * float(part)/float(whole)
    
    tweets = tweepy.Cursor(api.search, q=searchTerm).items(NumberSearchTerms)
    
    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    results = []

    for tweet in tweets:
        analysis = TextBlob(tweet.text)
        polarity += analysis.sentiment.polarity
        results.append(tweet)

        if (analysis.sentiment.polarity == 0):
            neutral += 1
        if (analysis.sentiment.polarity < 0):
            negative += 1
        if (analysis.sentiment.polarity > 0):
            positive += 1

    positive = percentage(positive,NumberSearchTerms)
    neutral = percentage(neutral,NumberSearchTerms)
    negative = percentage(negative,NumberSearchTerms)

    positive = format(positive, '.2f')
    neutral = format(neutral, '.2f')
    negative = format(negative, '.2f')

    print (positive)
    print (neutral)
    print (negative)
    
    labels = ["Postive","Neutral","Negative"]
    values = [positive,neutral,negative]
    colors = ["#66ff33","#FDB45C","#F7464A"]

    session['Postive_SentimentAnalysis'] = positive
    session['Neutral_SentimentAnalysis'] = neutral
    session['Negative_SentimentAnalysis']= negative
    
    searchdetails = SEARCH_INFO(SEARCH=searchTerm, POSITIVE_VALUE=positive, NEGATIVE_VALUE=negative, NEUTRAL_VALUE=neutral)     
    db.session.add(searchdetails)     
    db.session.commit()

    
    def tweets_df(results):
        id_list = [tweet.id for tweet  in results]
        data_set = pd.DataFrame(id_list, columns = ["id"])
        data_set["Hashtags"] = [tweet.entities.get('hashtags') for tweet in results]
        return data_set
    
    data_set = tweets_df(results)
 
    Htag_df = pd.DataFrame()
    j = 0

    for tweet in range(0,len(results)):
        hashtag = results[tweet].entities.get('hashtags')
        for i in range(0,len(hashtag)):
            Htag = hashtag[i]['text']
            Htag_df.set_value(j, 'Hashtag',Htag)
            j = j+1
    
    Htag_df_dict = Htag_df.astype(object).to_dict(orient='records')
    
    session['Htag_df_dict'] = Htag_df_dict
    
    return render_template('sentiment_analysis.html', set=zip(values, labels, colors), searchTerm = searchTerm)

@app.route("/wordcloud_analysis", methods=['POST','GET'])
def wordcloud_analysis():
    
    keyword = session.get('keyword', None)
    number = session.get('number', None)
    Htag_df_dict = session.get('Htag_df_dict', None)
    
    Htag_df = pd.DataFrame.from_dict(Htag_df_dict)
    
    Hashtag_Combined = " ".join(Htag_df['Hashtag'].values.astype(str))
    Tweet_mask = imread("twitter_mask.png", flatten=True)
    
    
    wc = WordCloud(background_color="#F8F8F8", stopwords=STOPWORDS,mask = Tweet_mask, width=1600, height=800)
    #wc = session.get('wc', None)
    wc.generate(Hashtag_Combined)
    img_wordcloud = io.BytesIO()

    plt_wordcloud.imshow(wc)
    plt_wordcloud.axis("off")
    plt_wordcloud.tight_layout(pad=0)

    plt_wordcloud.savefig(img_wordcloud, format='png', dpi=300)
    img_wordcloud.seek(0)
    plot_url_worldcloud = base64.b64encode(img_wordcloud.getvalue()).decode()
    
    plt_wordcloud.clf()
    
    return render_template('wordcloud_analysis.html', plot_url_worldcloud = plot_url_worldcloud, keyword = keyword)

@app.route("/trend_analysis",methods=['POST','GET'])
def trend_Analysis():
    
    searchTerm = session.get('keyword', None)
    engine = create_engine('mysql+pymysql://dk488492:sameera123@cloudupload.czlq7phghrul.us-east-2.rds.amazonaws.com/awsdb')
    query='SELECT * FROM SEARCH_INFO WHERE SEARCH=\''+searchTerm+"\'"+" ORDER BY ID ASC"
    result  = engine.execute(query).fetchall()
    if(len(result)>1):
        postive=[]
        negative=[]
        neutral=[]
        for row in result:
            postive.append(row[2])
            negative.append(row[3])
            neutral.append(row[4])
        pos=np.array(postive)
        neg=np.array(negative)
        neut=np.array(neutral)  
        plt_trend.gca().set_color_cycle(['red', 'green', 'yellow'])

        d = np.arange(len(pos))
        e = np.arange(len(neg))
        f = np.arange(len(neut))

        plt_trend.plot(d,pos)
        plt_trend.plot(e, neg)
        plt_trend.plot(f,neut)

        plt_trend.legend(['Positive', 'Negative', 'Neutral'], loc='upper left')
        img_trend = io.BytesIO()

        plt_trend.savefig(img_trend, format='png', dpi=300)
        img_trend.seek(0)
        plot_url_trend = base64.b64encode(img_trend.getvalue()).decode()
        print ("Graph Generated!")
        plt_trend.clf()
        redirect_value = "NoBack"
        
    else:
        plot_url_trend = "False"
        redirect_value = "Back"
    
    return render_template('trend_analysis.html', plot_url_trend = plot_url_trend, searchTerm = searchTerm, redirect_value = redirect_value)

@app.route("/sentiment_analysis_2", methods=['POST','GET'])
def sentiment_analysis_2():
    
    searchTerm = session.get('keyword', None)
    NumberSearchTerms = session.get('number', None)
    NumberSearchTerms = int(NumberSearchTerms)
    
    positive_SA_2 = session.get('Postive_SentimentAnalysis', None)
    neutral_SA_2 = session.get('Neutral_SentimentAnalysis', None)
    negative_SA_2 = session.get('Negative_SentimentAnalysis', None)


    labels = ["Postive","Neutral","Negative"]
    values = [positive_SA_2,neutral_SA_2,negative_SA_2]
    colors = ["#66ff33","#FDB45C","#F7464A"]
    
    return render_template('sentiment_analysis.html', set=zip(values, labels, colors), searchTerm = searchTerm)

if __name__ == '__main__':
    app.run(debug=True)
    
    