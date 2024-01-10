import csv
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent


if(__name__== '__main__'):
    options = FirefoxOptions()
    options.add_argument("--headless")
    # ua = UserAgent()
    c= CurrencyRates()
    conversion_rates= c.get_rates('INR')
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    options.add_argument(f'user-agent={userAgent}')
    f= open("./device_affluence.csv", "r")
    data= list(csv.reader(f))
    modelstosearch= [row for row in data]
    print (len(modelstosearch), modelstosearch[:5])
    device_links= {}
    for mmodel in modelstosearch:
        model= str(mmodel[0])
        # if(mmodel[2]=='unknown'):
        print ("--------------------Running for model " + model + "-------------------------")
        try:
            # driver= webdriver.Chrome(ChromeDriverManager().install(), options=options,service_log_path=None)
            driver= webdriver.Firefox(options=options)
            driver.get("https://www.gsmarena.com/res.php3?sSearch="+model.replace(' ', '+'))
            soup= BeautifulSoup(driver.page_source, 'html.parser')
            device_menu = soup.find('div', class_='makers')
            device_list = device_menu.find('ul').find_all('li')
            for li in device_list:
                url= li.a['href']
                device_links[model]= url
                print(url)
                driver= webdriver.Firefox(options=options)
                driver.get("https://www.gsmarena.com/"+url)
                soup= BeautifulSoup(driver.page_source, 'html.parser')
                specs_menu = soup.find('div', id='specs-list').find_all('table')
                for i,sp in enumerate(specs_menu):
                    if sp.find('tbody').find("tr").find("th").text == 'Misc':
                        misc_index= i
                        break
                misc_table= specs_menu[misc_index]
                for sp in misc_table.find("tbody").find_all("tr"):
                    if(sp.find('td',class_= 'ttl').text== "Price"):
                        price= str(sp.find('td',class_= 'nfo').text.split('/')[0]).replace('$\u2009', '').strip()
                driver.quit()
                break
            price= price.replace(",", "")
            if(price.__contains__("EUR")):
                cleanedprice= int(int(re.sub("[^0-9]", "", price))*(1 / conversion_rates['EUR']))
            elif(price.__contains__("Rp")):
                cleanedprice= int(int(str(row[1])[8:])*(1 / conversion_rates['IDR']))
            elif(price.__contains__("INR")):
                cleanedprice= int(re.sub("[^0-9]", "", price))
            elif(price.__contains__("€")):
                cleanedprice= int(int(float((str(price)[2:7])))*(1 / conversion_rates['EUR']))
            elif(price.__contains__("₹")):
                cleanedprice= int(float((str(price)[2:7])))
            else:
                cleanedprice= int(int(float(price.strip()))*(1 / conversion_rates['USD']))
            print (model, cleanedprice)
            mmodel.append(cleanedprice)

            if(mmodel[-1]> 50000):
                affluence =("super high")
            elif(mmodel[-1]> 25000):
                affluence= ("high")
            elif(mmodel[-1]> 15000):
                affluence= ("medium")
            elif(mmodel[-1]> 7000):
                affluence= ("low")
            else:
                affluence= ("super low")
            mmodel.append(affluence)

            with open('./device_affluence_output.csv', 'a') as fop:
                w = csv.writer(fop, delimiter='~')
                w.writerow([mmodel[0], mmodel[2], mmodel[1]])

        except Exception as e:
            print("Failed for model " + model, e)