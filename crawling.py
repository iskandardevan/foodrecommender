import requests, re, json, lxml, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg2 import pool
import psycopg2
import validators
import time
from tqdm import tqdm

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1117104786412675183/AWTj_sC_WaZyE_POulxVo5bqFTJlCauAMFD488R3mWO68CENvKA7lD1GTaECJmqYwJRV"

def send_discord_webhook(message):
    userId = "388263469964722176"
    messagePayload = f"<@{userId}> {message}"
    payload = {
        "content": messagePayload
    }
    requests.post(DISCORD_WEBHOOK_URL, data=payload)

load_dotenv()

# Mengakses nilai-nilai dari file .env
db_host = os.environ.get("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def crawl_google_images(keyword):
    google_images = []
    params = {    
        "q": keyword,              # search query
        "tbm": "isch",             # image results
    }
        
    html = requests.get("https://google.com/search", params=params, headers=headers, timeout=30)
    # print(html)
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
        title = ""
        link = ""
        elm = metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")
        if elm is not None:
            title = elm["title"]
            link = elm["href"]
        if link == "":
            continue
        google_images.append({
            "title": title,
            "link": link,
            "source": metadata.select_one(".fxgdke").text,
            "thumbnail": thumbnail,
            "original": original
        })
    
    return google_images[0]["original"] if google_images else None, html.status_code


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

    pbar = tqdm(total=total_results)
    last_request = time.time()
    error_too_many_request_count = 0
    error_invalid_url_count = 0
    for result in results:
        id = result[0]
        title = result[1]
        conn = psql_pool.getconn()
        cur = conn.cursor()
        # print(f"Crawling for {id}-{title}")
        defaultDelay = 0.600
        delay = defaultDelay - (time.time() - last_request)
        image_url, status_code = crawl_google_images(title)
        last_request = time.time()
        truncated_text = ""
        if image_url:
            # print(f"Updating {id}-{title} with {image_url}")
            cur.execute("UPDATE recipes SET img = %s WHERE id = %s", (image_url, id))
            conn.commit()
            total_updated = total_updated + 1
            pbar.update(1)
            text = image_url
            modified_url = text.replace("https://", "")
            truncated_text = modified_url[:10] + "..."
        else:
            error_invalid_url_count = error_invalid_url_count + 1
            if error_invalid_url_count % 4 == 0:
                send_discord_webhook(f"Error 429: {error_too_many_request_count} || Error URL: {error_invalid_url_count}")


        if status_code == 429:
            error_too_many_request_count = error_too_many_request_count + 1
            if error_too_many_request_count % 4 == 0:
                send_discord_webhook(f"Error 429: {error_too_many_request_count} || Error URL: {error_invalid_url_count}")
        
        
        pbar.set_description(f"{id}-{truncated_text} || Error 429: {error_too_many_request_count} || Error URL: {error_invalid_url_count}")
        cur.close()
        psql_pool.putconn(conn)
        
        # print(f"Updated {total_updated} of {total_results} rows")
        if delay > 0:
            time.sleep(delay)
    pbar.close()
    psql_pool.closeall()

if __name__ == "__main__":
    send_discord_webhook(f"Crawling started at {time.time()}")
    try:
        main()
    except Exception as e:
        send_discord_webhook(f"Error: {e}")
    # main()
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