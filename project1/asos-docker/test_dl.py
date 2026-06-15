import time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=opts)

# Try navigating directly to an image URL
test_img = "https://images.asos-media.com/products/asos-design-plisse-dropped-shoulder-ruched-midi-dress-in-black/209733038-1-black?$n_640w$&wid=513&fit=constrain"
print(f"Loading image directly: {test_img}")
driver.get(test_img)
time.sleep(3)

# Take screenshot of the whole page (image)
os.makedirs("/app/data/images_test", exist_ok=True)
driver.save_screenshot("/app/data/images_test/test_direct.png")
print(f"Page title: '{driver.title}'")
print(f"Screenshot saved. Body HTML length: {len(driver.page_source)}")

# Check if it's an image or error page
body_text = driver.find_element("tag name", "body").text[:200]
print(f"Body text: {body_text}")

driver.quit()
