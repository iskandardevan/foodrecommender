import requests, re, json, lxml, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()

# Mengakses nilai-nilai dari file .env
db_host = os.environ.get("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

def crawl_google_images(keyword):
    google_images = []
    params = {    
        "q": keyword,              # search query
        "tbm": "isch",             # image results
    }
        
    html = requests.get("https://google.com/search", params=params, headers=headers, timeout=30)
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
    psql_pool = pool.SimpleConnectionPool(1, 30,
                                                host=db_host,
                                                port=db_port,
                                                database=db_name,
                                                user=db_user,
                                                password=db_password,
                                                sslmode='require')
    
    conn = psql_pool.getconn()

    cur = conn.cursor()
    cur.execute("SELECT * FROM recipes")
    results = cur.fetchall()
    total_results = len(results)
    total_updated = 0

    def update(result):
        id = result[0]
        title = result[1]

        image_url = crawl_google_images(title)
        if image_url:
            print(f"Updating {id}-{title} with {image_url}")
            cur.execute("UPDATE recipes SET img = %s WHERE id = %s", (image_url, id))
            conn.commit()
            return 1
        else:
            return 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for result in results:
            futures.append(executor.submit(update, result))
        
        total_updated = total_updated + sum(future.result() for future in concurrent.futures.as_completed(futures))
        print(f"Updated {total_updated} of {total_results} rows")

    
    cur.close()
    psql_pool.putconn(conn)

    psql_pool.closeall()

if __name__ == "__main__":
    main()
