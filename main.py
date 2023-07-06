from flask import Flask, jsonify, request, json, session
import joblib
import re
from flask_cors import CORS, cross_origin
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

import uuid

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
                                                password=db_password,
                                                sslmode='require')


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost", "http://localhost:5500", "http://http://127.0.0.1:5500", "http://localhost:5000", "https://foodrecommender.surge.sh", "https://surge.sh"]}}, supports_credentials=True)

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
        rate = 6
        response = app.response_class(
            status=200,
            mimetype='application/json',
        )
        sid = ""
        if request.cookies.get('sid'):
            print("COOKIE ACTIVE", request.cookies.get('sid'))
            sid = request.cookies.get('sid')
        else:
            response, sid = generate_response_sid(response)
            print("COOKIE NOT ACTIVE", request.cookies.get('sid'))

        query = request.get_json()
        clean_data = remove_special_chars(query['bahan'])
        clean_data = clean_data.lower()
        print(clean_data)
        query_vec = vectorizer.transform([clean_data]) 
        results = cosine_similarity(model,query_vec).reshape((-1,))
        # print(results, 'INI HASIL')
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        upsertQueryHitrate = """
            WITH upsert AS (
                UPDATE hitrate SET rate = rate + %s 
                WHERE sid = %s
                RETURNING *
            )
            INSERT INTO hitrate (sid, hit, rate)
            SELECT %s, 0, %s
            WHERE NOT EXISTS (SELECT * FROM upsert);
        """
        cursor.execute(upsertQueryHitrate, (rate, sid, sid, rate))
        conn.commit()

        ids = results.argsort()[-rate:][::-1]
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

        
        response.data = json.dumps(resep)
        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method"

@app.route("/success", methods=['POST'])
def success():
    if request.method == 'POST':
        rate = 6
        response = app.response_class(
            status=200,
            mimetype='application/json',
        )
        sid = ""
        if request.cookies.get('sid'):
            print("COOKIE ACTIVE", request.cookies.get('sid'))
            sid = request.cookies.get('sid')
        else:
            response, sid = generate_response_sid(response)
            print("COOKIE NOT ACTIVE", request.cookies.get('sid'))

        query = request.get_json()
        id = query['id']
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        updateSuccessCountQuery = "UPDATE recipes SET successcount = successcount + 1 WHERE id = %s"
        cursor.execute(updateSuccessCountQuery, (str(id),))
        conn.commit()

        upsertQueryHitrate = """
            WITH upsert AS (
                UPDATE hitrate SET hit = hit + 1 
                WHERE sid = %s
                RETURNING *
            )
            INSERT INTO hitrate (sid, hit, rate)
            SELECT %s, 1, %s
            WHERE NOT EXISTS (SELECT * FROM upsert);
        """

        cursor.execute(upsertQueryHitrate, (sid, sid, rate))
        conn.commit()
        response.data = json.dumps({'message': 'success'})

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
    

@app.route("/session", methods=['GET'])
def session():
    response = app.response_class(
        status=200,
        mimetype='application/json',
    )
    # check cookie first
    if request.cookies.get('sid'):
        return response
    
    response, _ = generate_response_sid(response)
    return response

# API GET ID RESEP
@app.route("/detail", methods=['GET'])
def detail():
    if request.method == 'GET':
        id = request.args.get('id')
        print(id, "INI ID")
        
        conn = psql_pool.getconn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM recipes WHERE id = %s", (id,))
        record = cursor.fetchall()
        response = app.response_class(
            status=200,
            mimetype='application/json',
        )


        if len(record) == 0:
            response.status_code = 404
            return response
        else:
            res = {
                'id': record[0][0],
                'title': record[0][1],
                'ingredients': record[0][2],
                'steps': record[0][3],
                'likes': record[0][4],
                'dilihat': record[0][6],
                'img': record[0][7],
            }
            response.data = json.dumps(res)

        

        cursor.close()
        psql_pool.putconn(conn)
        return response
        
    else:
        return "Unsupported Request Method" 

def generate_response_sid(response):
    sid = uuid.uuid4()
    response.set_cookie('sid', str(sid), httponly=True, secure=True, samesite='None', max_age=3600)
    return response, str(sid)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=80))