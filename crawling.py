import requests, re, json, lxml, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg2
import validators
import time

load_dotenv()

# Mengakses nilai-nilai dari file .env
db_host = os.environ.get("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

headers = {
    "User-Agent": "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14"
}

def crawl_google_images(keyword):
    google_images = []
    params = {    
        "q": keyword,              # search query
        "tbm": "isch",             # image results
    }
        
    html = requests.get("https://google.com/search", params=params, headers=headers, timeout=30)
    print(html)
    soup = BeautifulSoup(html.text, "lxml")
    all_script_tags = soup.select("script")
    
    # https://regex101.com/r/RPIbXK/1
    matched_images_data = "".join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
        
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)
        
    # https://regex101.com/r/NRKEmV/1
    matched_google_image_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)
        
    # https://regex101.com/r/SxwJsW/1
    matched_google_images_thumbnails = ", ".join(
        re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                        str(matched_google_image_data))).split(", ")
        
    thumbnails = [bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails]
        
    # removing previously matched thumbnails for easier full resolution image matches.
    removed_matched_google_images_thumbnails = re.sub(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))
        
    # https://regex101.com/r/fXjfb1/4
    # https://stackoverflow.com/a/19821774/15164646
    matched_google_full_resolution_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)
        
    full_res_images = [
            bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for img in matched_google_full_resolution_images
    ]
            
    for index, (metadata, thumbnail, original) in enumerate(zip(soup.select('.isv-r.PNCib.MSM1fd.BUooTd'), thumbnails, full_res_images), start=1):
        google_images.append({
            "title": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["title"],
            "link": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["href"],
            "source": metadata.select_one(".fxgdke").text,
            "thumbnail": thumbnail,
            "original": original
        })

    return google_images[0]["original"] if google_images else None

import concurrent.futures

def main():
    max_workers = 30
    psql_pool = pool.SimpleConnectionPool(1, max_workers,
                                                host=db_host,
                                                port=db_port,
                                                database=db_name,
                                                user=db_user,
                                                password=db_password,
                                                sslmode='require')
    
    conn = psql_pool.getconn()

    cur = conn.cursor()
    cur.execute("SELECT * FROM recipes Where img IS NULL")
    results = cur.fetchall()
    total_results = len(results)
    print(f"Total need to be updated: {total_results}")
    total_updated = 0
    cur.close()
    psql_pool.putconn(conn)

    def update(result):
        id = result[0]
        title = result[1]
        conn = psql_pool.getconn()
        cur = conn.cursor()
        print(f"Crawling for {id}-{title}")
        image_url = crawl_google_images(title)
        print(f"Got {image_url}")
        if image_url:
            print(f"Updating {id}-{title} with {image_url}")
            cur.execute("UPDATE recipes SET img = %s WHERE id = %s", (image_url, id))
            conn.commit()
            cur.close()
            psql_pool.putconn(conn)
            return 1
        else:
            cur.close()
            psql_pool.putconn(conn)
            return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        print("Starting crawling")
        futures = []
        last_req = time.time()
        for result in results:
            now = time.time()
            delay = last_req + 0.600 - now
            if delay > 0:
                time.sleep(delay)
            futures.append(executor.submit(update, result))
            
        
        for future in concurrent.futures.as_completed(futures):
            total_updated = total_updated + future.result()
            print(f"Updated {total_updated} of {total_results} rows")
        


    psql_pool.closeall()

if __name__ == "__main__":
    main()
    # print(crawl_google_images("ayam"))
    # psql_pool = pool.SimpleConnectionPool(1, 2,
    #                                             host=db_host,
    #                                             port=db_port,
    #                                             database=db_name,
    #                                             user=db_user,
    #                                             password=db_password,
    #                                             sslmode='require'
    # )
    # print(db_host)
    # conn = psycopg2.connect(
    #                                             host=db_host,
    #                                             port=db_port,
    #                                             database=db_name,
    #                                             user=db_user,
    #                                             password=db_password,
    #                                             sslmode='require'
    # # )
    # conn = psql_pool.getconn()
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM recipes Where img IS NULL")
    # results = cur.fetchall()
    # print(len(results))