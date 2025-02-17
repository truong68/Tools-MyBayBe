from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Thông tin proxy
proxy_host = "160.22.173.91"  # Địa chỉ IP của proxy
proxy_port = 39546  # Cổng proxy
proxy_user = "best6395"  # Tên đăng nhập proxy
proxy_pass = "xedaba89n03"  # Mật khẩu proxy

# Cấu hình proxy cho Chrome
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
chrome_options.add_argument('--ignore-certificate-errors')

# Đăng nhập proxy (nếu proxy yêu cầu xác thực)
proxy_auth_extension = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: []
        }
    };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
""" % (proxy_host, proxy_port, proxy_user, proxy_pass)

# Lưu extension để sử dụng proxy authentication
import zipfile
proxy_auth_plugin_path = 'proxy_auth_plugin.zip'
with zipfile.ZipFile(proxy_auth_plugin_path, 'w') as zp:
    zp.writestr("manifest.json", """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """)
    zp.writestr("background.js", proxy_auth_extension)

chrome_options.add_extension(proxy_auth_plugin_path)

# Khởi tạo WebDriver với proxy
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Hàm tìm kiếm và cuộn trang nếu tìm thấy URL yêu cầu
def tim_kiem_va_cuon_trang(tu_khoa):
    try:
        # Mở Google và nhập từ khóa tìm kiếm
        driver.get("https://www.google.com")
        time.sleep(2)  # Chờ trang tải
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(tu_khoa)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Chờ kết quả hiển thị

        max_pages = 5
        current_page = 1
        found = False

        while current_page <= max_pages:
            print(f"Đang kiểm tra trang {current_page}...")

            # Kiểm tra các phần tử <cite> để tìm URL chứa "duhocvietphuong.edu.vn"
            cites = driver.find_elements(By.XPATH, "//cite")
            for cite in cites:
                url = cite.text
                if "duhocvietphuong.edu.vn" in url:
                    print(f"Đã tìm thấy URL trong cite: {url}")
                    # Tìm phần tử cha của <cite> để click vào liên kết
                    parent_link = cite.find_element(By.XPATH, "..")
                    parent_link.click()
                    time.sleep(5)  # Đợi trang tải đầy đủ
                    found = True
                    break

            if found:
                break

            # Nếu không tìm thấy, chuyển sang trang tiếp theo
            try:
                next_page_button = driver.find_element(By.XPATH, "//a[@id='pnnext']")
                next_page_button.click()
                current_page += 1
                time.sleep(3)
            except Exception:
                print("Không tìm thấy nút 'Tiếp', kết thúc tìm kiếm.")
                break

        if found:
            # Cuộn lên và xuống liên tục trong 120 giây
            print("Trang đã tải xong. Bắt đầu cuộn lên và xuống trong 120 giây...")
            start_time = time.time()
            scroll_direction = "down"  # Ban đầu cuộn xuống
            while time.time() - start_time < 120:
                if scroll_direction == "down":
                    driver.execute_script("window.scrollBy(0, 200);")  # Cuộn xuống 200px
                    if driver.execute_script("return window.innerHeight + window.scrollY") >= driver.execute_script("return document.body.scrollHeight"):
                        scroll_direction = "up"  # Đổi chiều nếu đạt cuối trang
                else:
                    driver.execute_script("window.scrollBy(0, -200);")  # Cuộn lên 200px
                    if driver.execute_script("return window.scrollY") == 0:
                        scroll_direction = "down"  # Đổi chiều nếu đạt đầu trang
                time.sleep(0.5)  # Chờ 0.5 giây rồi tiếp tục cuộn

        else:
            print(f"Không tìm thấy URL 'duhocvietphuong.edu.vn' cho từ khóa '{tu_khoa}'.")

    except Exception as e:
        print(f"Lỗi xảy ra khi tìm kiếm từ khóa '{tu_khoa}': {e}")

# Danh sách các từ khóa để tìm kiếm
keywords = [
    "du học Mỹ", "hồ sơ du học mỹ gồm những gì",

]

# Thực hiện tìm kiếm cho các từ khóa trong danh sách
for keyword in keywords:
    tim_kiem_va_cuon_trang(keyword)
    print(f"Đã hoàn thành tìm kiếm từ khóa: {keyword}")
    time.sleep(120)  # Thêm thời gian chờ 120 giây giữa mỗi lần tìm kiếm

# Đóng trình duyệt sau khi hoàn thành
driver.quit()
