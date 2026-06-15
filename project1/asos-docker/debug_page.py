import time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=opts)
try:
    driver.get("https://www.asos.com/aria-cove/aria-cove-textured-boucle-bardot-foldover-maxi-jumper-dress-in-chocolate/prd/208487766")
    time.sleep(5)
    
    # Save full page source
    with open("/app/data/debug_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Page source saved")
    
    # Check common elements
    tests = [
        ("h1", "//h1"),
        ("colour by testid", "//div[@data-testid='productColour']/p"),
        ("colour by contains", "//*[contains(text(), 'olour') or contains(text(), 'OLOUR')]"),
        ("any colour element", "//p[contains(., 'olour')]"),
        ("variant select", "//select"),
        ("variant select id", "//select[contains(@id, 'ariant') or contains(@id, 'ariantSelector')]"),
        ("About Me button", "//button[contains(text(), 'About')]"),
        ("Look After Me button", "//button[contains(text(), 'Look')]"),
        ("Details button", "//button[contains(text(), 'Details')]"),
        ("Brand link", "//a[contains(@data-testid, 'brand')]"),
        ("Gallery images", "//img[@class='gallery-image']"),
        ("Any img asos-media", "//img[contains(@src, 'images.asos-media.com')]"),
        ("Nav breadcrumb", "//nav//a"),
        ("Any breadcrumb links", "//ol//li//a[contains(@href, '/women')]"),
        ("Size radio buttons", "//input[@type='radio' and contains(@name, 'size')]"),
        ("Size labels", "//label[contains(@for, 'size') or contains(@for, 'variant')]"),
    ]
    
    for name, xpath in tests:
        try:
            els = driver.find_elements("xpath", xpath)
            if els:
                texts = [e.text.strip()[:80] if hasattr(e, 'text') else str(e.get_attribute('outerHTML'))[:80] for e in els[:3]]
                print(f"  ✅ {name}: found {len(els)} → {texts}")
            else:
                print(f"  ❌ {name}: NOT FOUND")
        except Exception as e:
            print(f"  ⚠️ {name}: ERROR {e}")
finally:
    driver.quit()
