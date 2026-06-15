import lxml.html  # 用于解析HTML
from selenium import webdriver  # 用于自动化浏览器操作
import time  # 用于添加延时
from multiprocessing.dummy import Pool  # 用于创建线程池，实现多线程

# 初始化Chrome浏览器驱动
driver = webdriver.Chrome()

# 定义一个函数来获取产品URL
def get_product_url(i):
    # 定义基础URL和页码URL
    basic_url = "https://www.asos.com/women/sale/dresses/cat/?cid=5235"
    append_url = '&page=' + str(i)
    
    # 使用浏览器访问完整URL
    driver.get(basic_url + append_url)
    
    # 等待5秒，确保页面加载完成
    time.sleep(5)

    # 使用lxml解析页面源代码
    selector = lxml.html.fromstring(driver.page_source)

    # 使用XPath提取所有产品的URL
    product_list = selector.xpath(
        r"//article[contains(@id,'product-')]//a/@href")
    
    # 打印提取到的产品URL列表
    print(product_list)

    # 将提取到的URL写入文件
    with open('product_url_women.txt', 'a') as f:
        for product_url in product_list:
            f.write(product_url)
            f.write('\n')  # 每个URL占一行

# 主程序入口
if __name__ == '__main__':
    # 创建（如果不存在）或清空（如果已存在）输出文件
    f = open('product_url_women.txt','w')
    f.close()
    
    # 创建一个包含10个线程的线程池
    pool = Pool(10)
    print("线程池创建完毕")
    
    # 使用线程池并发执行get_product_url函数，爬取10个页面
    pool.map(get_product_url, [1,2,3,4,5,6,7,8,9,10])
    print("多线程爬取结束")