from selenium import webdriver

# 初始化Chrome浏览器驱动
# 注意：现代版本的Selenium无需手动下载浏览器驱动，它会自动下载所需的驱动
driver = webdriver.Chrome()

# 使用浏览器访问ASOS网站的主页
driver.get('http://www.asos.com/?hrd=1')

# 使用XPath定位需要的链接
links = driver.find_elements("xpath", '//*[@id="chrome-app-container"]/section[1]/div/div[2]/div[1]/div[2]/a')

# 遍历找到的所有链接元素
for link in links:
    # 获取每个链接元素的href属性（即链接地址）并打印出来
    print(link.get_attribute('href'))

# 自动关闭浏览器
driver.quit()