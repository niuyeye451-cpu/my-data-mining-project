import os
import re
import time
import urllib
from selenium import webdriver
import urllib.request

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ISOTIMEFORMAT = '%Y-%m-%d %X'  # 时间戳
ROOTPATH = '' # 此处输入图片保存路径

# 保存图片
def saveImgs(driver, img_path, img_url_list):
    img_num = 0
    if not os.path.exists(img_path):  # 判断文件是否存在，返回布尔值
        os.makedirs(img_path)
    # 遍历 img_url_list 保存
    while img_num < len(img_url_list):
        image_url = img_url_list[img_num]
        save_path = img_path + str(img_num) + '.jpg'
        urllib.request.urlretrieve(image_url, save_path)
        img_num = img_num + 1
    return img_num

# 定义爬取商品内容的主函数
def craw_product_contents(product_url):
    product_info_list = []  # 用于存储商品信息的列表
    driver.get(product_url)  # 访问商品页面

    # URL 里的商品 ID
    url_product_id = re.findall(r'\d+', product_url)[0]
    product_info_list.append(url_product_id)

    # 获取面包屑导航栏的内容，例如 Home > Women > Dresses
    breadcrumb = ''
    # 等待导航栏加载完成 WebDriverWait(driver, 10)中的10意思是最大等待 10 秒
    nav_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ojIeyOc'))
    )
    # 获取导航栏中的文本内容
    breadcrumb_elements = nav_element.find_elements(By.XPATH, ".//a")
    breadcrumb_texts = [element.text for element in breadcrumb_elements]
    breadcrumb = ' > '.join(breadcrumb_texts)
    product_info_list.append(breadcrumb)

    # 商品 URL
    product_info_list.append(product_url)

    # URL 状态 1
    product_url_stat = 1
    product_info_list.append(str(product_url_stat))

    # 商品代码
    # 由于该元素需要展开才可见，因此需要模拟点击
    details_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='productDescription']/ul/li[1]/div/h2/button")))
    details_button.click()
    # 显式等待，直到目标文本元素出现，然后获取
    product_code = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='productDescriptionDetails']/div/p"))
    ).text
    product_info_list.append(product_code)
    
    # 商品描述
    product_description = 'product description: '
    ul_element = driver.find_element("xpath","//*[@id='productDescriptionDetails']/div/div/ul")
    li_elements = ul_element.find_elements("xpath","./li")
    for li in li_elements:
        product_description += li.text + ";\n"  # 加入每个 li 元素的文本内容并换行

    # 商品网站
    product_website = 'http://www.asos.com/'
    product_info_list.append(product_website)

    # 商品的性别 men=1 women=0
    gender = 0
    if 'Men' in breadcrumb:
        gender = 1
    else:
        gender = 0
    product_info_list.append(str(gender))

    # 商品品牌
    # 模拟点击 Brand 按钮
    brand_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,"//*[@id='productDescription']/ul/li[2]/div/h2/button")))
    brand_button.click()
    # 显式等待，直到目标文本元素出现，然后获取
    product_brand = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='productDescriptionBrand']/div/div/a/strong"))
    ).text
    product_info_list.append(product_brand)

    # 记录爬取时间
    product_craw_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))  # 获取当前时区时间格式 2024-07-14 17:23:40
    product_info_list.append(product_craw_time)

    # 商品名
    product_title = ''
    product_title = driver.find_element("xpath","//*[@id='pdp-react-critical-app']/span[1]/h1").text
    product_info_list.append(product_title)

    # 商品价格
    product_price = 0
    product_price = driver.find_element("xpath", "//*[@id='pdp-react-critical-app']/span[2]/div/span[1]").text
    product_info_list.append(product_price)

    # 获取商品的衣料信息
    product_material = ''
    # 模拟点击 About Me 按钮
    about_me_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='productDescription']/ul/li[5]/div/h2/button")))
    about_me_button.click()
    product_material = driver.find_element("xpath","//*[@id='productDescriptionAboutMe']/div/div").text.strip()
    # 移除多余的空行
    product_material = '\n'.join(line.strip() for line in product_material.splitlines() if line.strip())
    # 合并前面的获取商品详细描述和衣料信息，并添加到列表
    product_description = product_description + product_material
    product_info_list.append(product_description.strip(';'))


    # 获取商品尺码
    size = ''
    # 定位尺码选择器的 select 元素
    select_element = driver.find_element("xpath", "//*[@id='looksVariantSelector']")
    # 获取 select 元素下的所有 option 元素
    option_elements = select_element.find_elements("tag name", "option")
    # 遍历每个 option 元素，获取其文本内容（即尺码信息）
    for option in option_elements:
        size_text = option.text.strip()  # 获取文本内容，并去除首尾空白字符
        if size_text and size_text != "Please select":  # 排除掉空文本和 "Please select" 选项
            size += size_text + ";"
    product_info_list.append(size)

    # 商品洗护信息
    product_care = ''
    # 模拟点击 Look After Me 按钮
    care_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,"//*[@id='productDescription']/ul/li[4]/div/h2/button")))
    care_button.click()
    # 显式等待，直到目标文本元素出现，然后获取
    product_care = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='productDescriptionCareInfo']/div/div"))
    ).text
    product_info_list.append(product_care)

    # 商品颜色
    product_colour = ''
    product_colour = driver.find_element("xpath","//div[@data-testid='productColour']/p").text
    product_info_list.append(product_colour)

    # 获取商品图片
    img_url_list = []
    ele_imgs = driver.find_elements("xpath","//img[@class='gallery-image']")
    for ele in ele_imgs:
        img_url_list.append(ele.get_attribute("src"))
    img_url_list = list(set(img_url_list)) # 去重
    img_number = saveImgs(driver, ROOTPATH + '/'  + str(url_product_id) + "/", img_url_list)
    product_info_list.append('img_number: '+str(img_number))

    # 打印商品信息并保存到文件
    print(product_info_list)
    with open('product.txt', 'a',encoding='utf-8')as f:
        for product_message in product_info_list:
            f.write(product_message)
            f.write('\n')
        f.write('\n')
    return product_info_list

# 主程序入口
if __name__ == '__main__':
    driver = webdriver.Chrome()
    product_data = craw_product_contents(
        'https://www.asos.com/asos-design/asos-design-high-neck-mesh-midi-dress-in-swirl-stripe-print/prd/206238647#colourWayId-206238648')