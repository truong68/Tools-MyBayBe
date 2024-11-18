from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# Cấu hình proxy
proxy_host = "160.22.173.91"
proxy_port = 39546
proxy_user = "best6395"
proxy_pass = "xedaba89n03"

# Hàm tạo driver với proxy
def create_driver_with_proxy():
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# API cho tìm kiếm tự động
@app.route('/search', methods=['GET'])
def search_keyword():
    keyword = request.args.get('keyword', '')
    
    if not keyword:
        return jsonify({"error": "Missing 'keyword' parameter"}), 400

    driver = create_driver_with_proxy()
    try:
        # Mở Google và tìm kiếm
        driver.get("https://www.google.com")
        time.sleep(2)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        found_url = ""
        cites = driver.find_elements(By.XPATH, "//cite")
        for cite in cites:
            url = cite.text
            if "duhocvietphuong.edu.vn" in url:
                found_url = url
                break

        if found_url:
            return jsonify({"found_url": found_url})
        else:
            return jsonify({"message": "No relevant URL found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
