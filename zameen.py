from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
import re
import os

def change_Area(page):
    change_area_xpath='//div[@class="dropdown _6edd0d50"][2]'
    change_area_xpath2='//button[text()="Change Area Unit"]'
    change_area_xpath3='//div[@class="dropdown _3f5a8f46"]'
    change_area_xpath4='//div[@class="dropdown dropdown--active _3f5a8f46"]//li[text()="Square Yards"]'
    #//div[@class="dropdown dropdown--active _3f5a8f46"]//li[text()="Marla"]
    # //div[@class="dropdown dropdown--active _3f5a8f46"]//li[text()="Square Yards"]
    change_area_xpath5='//button[@class="d8b1d2e4"]'
    # Changing the Area Unit
    chng_area=page.locator(change_area_xpath)
    chng_area.click()
    chng_area=page.locator(change_area_xpath2)
    chng_area.click()
    chng_area=page.locator(change_area_xpath3)
    chng_area.click()
    chng_area=page.locator(change_area_xpath4)
    chng_area.click()
    chng_area=page.locator(change_area_xpath5)
    chng_area.click()
        

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        l1=[]
        df=pd.read_csv("city_list.csv")
        l1=df["City"]
        df=pd.read_csv("link2.csv")
        l2=df["Numbers"]
        count=0
      
        
        for location in l2:
            page_count=1
            page.goto(f'https://www.zameen.com/Farm_Houses/{l1[count]}-{location}-{page_count}.html', timeout=60000)
        
            page.wait_for_timeout(5000)
            change_Area(page)
            print(l1[count])
            while True:
                page_content = page.content()
                parsed_html = BeautifulSoup(page_content, "html.parser")
                check1 = parsed_html.find("li", {"class" : "_449a18e3"})
                check2 = parsed_html.find("div", {"class" : "c27f6e51"})
                if(check1) or (check2):
                    break
                else:

                    containers = parsed_html.find_all("div", {"class" : "_732aff15 c7b81b5c"})
                    price=[]
                    Area=[]
                    City=[]
                    Bedrooms=[]
                    Baths=[]
                    Address=[]
                    for item in containers:
                        pri=item.find("span",{"class":"f343d9ce"}).text
                        value = float(re.findall(r'\d+\.\d+|\d+', pri)[0])
                        if "Crore" in pri:
                            value *= 10000000  # 1 Crore = 10 million
                        elif "Lakh" in pri:
                            value *= 100000  # 1 Lakh = 100 thousand
                        elif "Thousand" in pri:
                            value *= 1000
                        value=int(value)
                        price.append(value)
                        City.append(l1[count])

                        add=item.find("div", {"class" : "_162e6469"}).text
                        Address.append(add)

                        item2=item.find("div", {"class" : "_27f6c93d"})
                        try:
                            bed=item2.find("span", {"class" : "_984949e5"}).text
                            bath=item2.find_next("span", {"class" : "_984949e5"})
                            bath=bath.find_next("span", {"class" : "_984949e5"}).text
                            area_sq=item2.find_next("span", {"class" : "_984949e5"})
                            area_sq=area_sq.find_next("span", {"class" : "_984949e5"})
                        
                            area_sq=area_sq.find_next("span", {"class" : "_984949e5"}).text
                        except:
                            area_sq=None
                        
                        Bedrooms.append(bed)
                        Baths.append(bath)
                        if (area_sq == None) or (len(area_sq)<2):
                            Area.append(None)
                        else:
                            Area.append(area_sq)
                    if page_count==1:
                        df = pd.DataFrame(list(zip(price,Address,City,Bedrooms,Baths,Area)), columns =['Price','Address','City','Bedrooms','Baths','Area'])
                    else:
                        df2 = pd.DataFrame(list(zip(price,Address,City,Bedrooms,Baths,Area)), columns =['Price','Address','City','Bedrooms','Baths','Area'])
                        df = pd.concat([df, df2], ignore_index = True, axis = 0)

                    
                    page_count+=1
                    print("Current Page: ",page_count)
                    page.goto(f'https://www.zameen.com/Farm_Houses/{l1[count]}-{location}-{page_count}.html', timeout=60000)
            
            print("City data extracted for: ",l1[count])
            count+=1
            df["Type"]="Farm Houses"
            if os.path.exists("result2.csv"):
                data2=pd.read_csv("result2.csv")
                # df = df[~df['Bedrooms'].str.contains('Sq.') & ~df['Baths'].str.contains('Sq.')]
                df = pd.concat([df, data2], ignore_index = True, axis = 0)
                df = df[df["Area"].notna()]
                df.drop_duplicates(inplace=True)
                df.to_csv(r'result2.csv', index = False)
                print(df.head())
            else:
                try:
                    df = df[df["Area"].notna()]
                except:
                    pass

                df = df[~df['Bedrooms'].str.contains('Sq.') & ~df['Baths'].str.contains('Sq.')]
                df.drop_duplicates(inplace=True)
                df.to_csv(r'result2.csv', index = False)
                print(df.head())
        
        
        if os.path.exists("result.csv"):
            data2=pd.read_csv("result.csv")
            df = pd.concat([df, data2], ignore_index = True, axis = 0)
            df = df[df["Area"].notna()]
            # df = df[~df['Bedrooms'].str.contains('Sq.') & ~df['Baths'].str.contains('Sq.')]
            df.drop_duplicates(inplace=True)
            df.to_csv(r'result.csv', index = False)
            print(df.head())
        else:
            try:
                df = df[df["Area"].notna()]
            except:
                pass
            # df = df[~df['Bedrooms'].str.contains('Sq.') & ~df['Baths'].str.contains('Sq.')]
            df.drop_duplicates(inplace=True)
            df.to_csv(r'result.csv', index = False)
            print(df.head())
        
        
        
        browser.close()
        


        



if __name__ == "__main__":
    main()
