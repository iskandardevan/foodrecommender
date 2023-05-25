from flask import Flask, request, json
import joblib
import re
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

import os
from psycopg2 import pool
# Memuat nilai dari file .env
load_dotenv()

# Mengakses nilai-nilai dari file .env
db_host = os.environ.get("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

psql_pool = pool.SimpleConnectionPool(1, 30,
                                                host=db_host,
                                                port=db_port,
                                                database=db_name,
                                                user=db_user,
                                                password=db_password)


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
        conn = psql_pool.getconn()
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
        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method"

@app.route("/success", methods=['POST'])
def success():
    if request.method == 'POST':
        query = request.get_json()
        print(query['id'], 'INI ID SUCCESS RECOMMENDATION')
        id = query['id']
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        updateSuccessCountQuery = "UPDATE recipes SET successcount = successcount + 1 WHERE id = %s"
        cursor.execute(updateSuccessCountQuery, (str(id),))
        conn.commit()

        cursor.execute(f"UPDATE hitrate SET hit = hit + 1")
        conn.commit()
        response = app.response_class(
            status=200,
            mimetype='application/json',
            response=json.dumps({'message': 'success'})
        )

        cursor.close()
        psql_pool.putconn(conn)
        return response
    else:
        return "Unsupported Request Method"

# API GET DAFTAR PANGAN BUMBU
@app.route("/daftarbahanbumbu", methods=['GET'])
def panganbumbu():
    if request.method == 'GET':
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM bahan WHERE kelompok = 'bumbu'")
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
        
        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method"
    

# API GET DAFTAR PANGAN SAYUR
@app.route("/daftarbahansayur", methods=['GET'])
def pangansayur():
    if request.method == 'GET':
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM bahan WHERE kelompok = 'sayur'")
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

        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method"
    

# API GET DAFTAR PANGAN TAMBAHAN
@app.route("/daftarbahantambahan", methods=['GET'])
def pangantambahan():
    if request.method == 'GET':
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM bahan WHERE kelompok = 'tambahan'")
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

        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method"
    

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))