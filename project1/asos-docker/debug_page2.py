import time, re, os
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
    
    page = driver.page_source
    
    # Search for text patterns in page source
    searches = [
        "material", "fabric", "composition", "polyester", "cotton",
        "care", "washing", "machine wash",
        "brand", "Aria Cove",
        "colour", "Colour", "COLOR",
        "description", "About me", "aboutMe",
        "productDescription", "product-description",
        "data-testid", "data-auto-id",
        "size", "Size", "SIZE",
    ]
    
    for term in searches:
        # Find context around the term
        idx = page.lower().find(term.lower())
        if idx >= 0:
            snippet = page[max(0,idx-80):idx+120].replace('\n',' ')[:200]
            print(f"🔍 '{term}' @ pos {idx}: ...{snippet}...")
        else:
            print(f"❌ '{term}': NOT FOUND in page source")
    
    # Try to find product description section
    print("\n--- Product Description blocks ---")
    for el in driver.find_elements("xpath", "//*[contains(@id, 'product') or contains(@class, 'product')]"):
        tag = el.tag_name
        el_id = el.get_attribute('id') or ''
        el_class = el.get_attribute('class') or ''
        text = (el.text or '')[:100]
        if text.strip():
            print(f"  <{tag}> id={el_id[:50]} class={el_class[:50]} text={text[:80]}")
    
    # Find the colour value specifically
    print("\n--- Colour elements ---")
    for el in driver.find_elements("xpath", "//*[contains(text(), 'COLOUR:')]"):
        parent_text = el.find_element("xpath", "..").text[:200]
        print(f"  Parent text: {parent_text}")
    
finally:
    driver.quit()
