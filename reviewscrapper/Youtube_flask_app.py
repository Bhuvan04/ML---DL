import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from selenium import webdriver
import time

app = Flask(__name__)
Driver_Path = './chromedriver.exe'
driver = webdriver.Chrome(Driver_Path)

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "+")
            youtube_url = "https://www.youtube.com/results?search_query=" + searchString
            uClient = driver.get(youtube_url)
            time.sleep(15)
            youtubePage = driver.page_source
            youtube_html = bs(youtubePage, "html.parser")
            bigboxes = youtube_html.findAll("div", {"class": "style-scope ytd-video-renderer"})
            del bigboxes[0:2]
            box = bigboxes[0]
            productLink = "https://www.youtube.com/" + box.a['href']

            uClient2 = driver.get(productLink)

            time.sleep(15)
            driver.execute_script('window.scrollTo(1, 500);')
            time.sleep(15)
            driver.execute_script('window.scrollTo(400, 1000);')

            prodRes = driver.page_source
            prod_html = bs(prodRes, "html.parser")

            commentboxes = prod_html.find_all('ytd-comment-renderer', {'class': "style-scope ytd-comment-thread-renderer"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Viewer Name, Number of Likes,Comment \n"
            fw.write(headers)
            reviews = []

            for commentbox in commentboxes:
                try:
                    Viewer = commentbox.find("a", {"id": "author-text"}).span.text
                except:
                    Viewer = 'No Name'

                try:
                    comment = commentbox.find("yt-formatted-string", {"id": "content-text"}).text
                    # comments = prod_html.find("yt-formatted-string", {"id": "content-text"})
                    # for comment in comments:
                    #    print(comment.text)
                except:
                    comment = 'No Comment'

                try:
                    like = commentbox.find("span", {"id": "vote-count-left"}).text
                    # likes = prod_html.findAll("span", {"id": "vote-count-left"})
                    # for like in likes:
                    #   like.text
                except:
                    like = 'Not applicable'

                mydict = {"Product": searchString, "Viewer Name": Viewer, "Number of Likes": like,
                          "Comment": comment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])


        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    #app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8001, debug=True)
