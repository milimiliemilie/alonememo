from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/memo', methods=['POST'])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기

    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    # 혼선을 주기 위한 headers (chrome인 척)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    }

    # request 말고 requests
    response = requests.get(url_receive, headers=headers)

    # 크롤링이 용이하게 parsing하기
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. meta tag를 스크래핑하기

    og_title = soup.select_one('meta[property="og:title"]')  # html은 " "를, python은 ' '를 활용한당.
    title = og_title['content']  # 태그의 속성값을 가져오기 (참고 : <meta property="og:title" content="집중호우 특별재난지역, 6개월간 전파사용료 면제">)
    og_image = soup.select_one('meta[property="og:image"]')
    image = og_image['content']
    og_desc = soup.select_one('meta[property="og:desc"]')
    desc = og_desc['content']

    # 3. mongoDB에 데이터 넣기

    # Dictionary를 이용한당

    article = {
        'url': url_receive,
        'comment': comment_receive,
        'title': title,
        'image_url': image,
        'desc': desc
    }

    db.alonememo.insert_one(article)

    return jsonify({'result': 'success', 'msg': 'POST 연결되었습니다!'})


@app.route('/memo', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기(Read)
    # 2. articles라는 키 값으로 articles 정보 보내주기
    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
