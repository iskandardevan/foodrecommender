from flask import Flask, render_template, request, json
import joblib
import re
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv


import numpy as np
import pandas as pd
import os
import psycopg2

# Memuat nilai dari file .env
load_dotenv()

# Mengakses nilai-nilai dari file .env
db_host = os.environ.get("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")


conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_password
)


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

model = joblib.load(
            "./model-food-recommender.pkl")
vectorizer = joblib.load(
            "./vectorizer-food-recommender.pkl")

def remove_special_chars(text):
    # Menghapus tanda baca, angka, dan spesial karakter lainnya
    text = re.sub('[^a-zA-Z]', ' ', text)

    # Menghapus spasi di awal dan akhir string
    text = text.strip()

    # Mengganti spasi ganda dengan spasi tunggal
    text = re.sub('\s+', ' ', text)

    return text

@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        query = request.get_json()
        clean_data = remove_special_chars(query['bahan'])
        clean_data = clean_data.lower()
        print(clean_data)
        query_vec = vectorizer.transform([clean_data]) 
        results = cosine_similarity(model,query_vec).reshape((-1,))
        # print(results, 'INI HASIL')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE hitrate SET rate = rate + 5")
        conn.commit()

        ids = results.argsort()[-5:][::-1]
        ids = [id + 1 for id in ids.tolist()]

        sql='SELECT * from recipes WHERE id IN %(ids)s'
        cursor.execute(sql, {
            "ids": tuple(ids)
        })
        records = cursor.fetchall()
        # list resep
        resep = []
        for data in records:
            # menambahkan resep ke list resep 
            res = {
                'id': data[0],
                'judul_resep': data[1],
                'bahan': data[2],
                'url': f"https://cookpad.com{data[5]}"
            }
            resep.append(res)
            response = app.response_class(
            status=200,
            mimetype='application/json',
            response=json.dumps(resep)
        )
        return response
        
    else:
        return "Unsupported Request Method"

@app.route("/success", methods=['POST'])
def success():
    if request.method == 'POST':
        query = request.get_json()
        print(query['id'], 'INI ID SUCCESS RECOMMENDATION')
        id = query['id']
        cursor = conn.cursor()
        cursor.execute(f"UPDATE recipes SET successcount = successcount + 1 WHERE id = {id}")
        cursor.execute(f"UPDATE hitrate SET hit = hit + 1")
        conn.commit()
        # record = cursor.fetchall()
        # database.iloc[int(query['id']), 5] += 1
        # database.to_csv('./dataset/merged.csv', index=False)
        response = app.response_class(
            status=200,
            mimetype='application/json',
            response=json.dumps({'message': 'success'})
        )
        return response
    else:
        return "Unsupported Request Method"

# API GET DAFTAR PANGAN
@app.route("/daftarbahantambahan", methods=['GET'])
def pangan():
    if request.method == 'GET':
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM bahan")
        record = cursor.fetchall()
        # list pangan
        pangan = []
        for i in range(len(record)):
            # menambahkan resep ke list resep 
            res = {
                'id': str(i),
                'nama_pangan': record[i][1],
                # 'nama_pangan': database_pangan.iloc[i,0],
            }
            pangan.append(res)
        response = app.response_class(
            status=200,
            mimetype='application/json',
            response=json.dumps(pangan)
        )
        return response
        
    else:
        return "Unsupported Request Method"
    

def getImageFromURL(url):
    # scrape image from url using beautifulsoup
    import requests
    from bs4 import BeautifulSoup

    url = 'https://cookpad.com/id/resep/13068090-ayam-goreng-kremes'
    userAgentWindows = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'

    #  set user agent
    headers = {'User-Agent': userAgentWindows}
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # <img alt="Jus Jeruk foto resep utama" width="680" height="482" data-original="https://img-global.cpcdn.com/recipes/c4829ec1a24b3a27/680x482cq70/jus-jeruk-foto-resep-utama.jpg" data-src="https://img-global.cpcdn.com/recipes/c4829ec1a24b3a27/680x482cq70/jus-jeruk-foto-resep-utama.jpg" class=" lazyloaded" src="https://img-global.cpcdn.com/recipes/c4829ec1a24b3a27/680x482cq70/jus-jeruk-foto-resep-utama.jpg">
    print(soup.prettify())
    image = soup.find_all('img')
    return image
        
if __name__ == '__main__':
    print(getImageFromURL(""))
    # app.run(port=5000, debug=True)