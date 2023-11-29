import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

baseurl = "https://www.1mg.com"
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
}



from urllib.parse import urlparse, parse_qs
import string

start_letter = 'v'
end_letter = 'z'

letters = [letter for letter in string.ascii_lowercase if start_letter <= letter <= end_letter]

for letter in letters:
    medlist = []
    
    productlinks = []  
    page_number = 1
    print('Letter is ',letter)  
    while True:
        
        r = requests.get(f'https://www.1mg.com/drugs-all-medicines?page={page_number}&label={letter}')
       
        soup = BeautifulSoup(r.content, 'html.parser')

        productlist = soup.find_all('div',class_='Card__container__liTc5 Card__productCard__SrdLF Card__direction__H8OmP container-fluid-padded-xl')

        for item in productlist:
            for link in item.find_all('a',href=True):
                productlinks.append(baseurl + link['href'])

        pagination_buttons = soup.find_all('div', class_='AllMedicines__paginationButton__QmWCn marginBoth-16 col-3')
        for button in pagination_buttons:
            a_tag = button.find('a',href=True)
            text = a_tag.text
            if a_tag and text == 'Next':
                href = a_tag.get('href', '')
                parsed_url = urlparse(href)
                query_parameters = parse_qs(parsed_url.query)
                page_number = query_parameters.get('page', [])[0]
            else:
                href = None
                                
        #testlink = 'https://www.1mg.com/drugs/avastin-100mg-injection-135666' 
        if href == None:
            break 
    i = 1    
    for link in productlinks:
            
            r = requests.get(link, headers=headers,timeout=60) 
                 
            soup = BeautifulSoup(r.content,'html.parser')
            name = soup.find('h1',class_ = 'DrugHeader__title-content___2ZaPo')
            if name:
                try:
                    name = name.text.strip()
                except Exception as e:
                    print("Error extracting text:", str(e))
            else:
              name = link
            composition = soup.find('div',class_ = 'saltInfo DrugHeader__meta-value___vqYM0')
            if composition:
                try:
                    composition = composition.text.strip()
                except Exception as e:
                    print("Error extracting text:", str(e))
            else:
              composition = None
            useslist = soup.find_all('ul',class_ = 'DrugOverview__list___1HjxR DrugOverview__uses___1jmC3')
            use = []
            for uses in useslist:
                a_tags = uses.find_all('li') 
                for a_tag in a_tags:
                    use.append(a_tag.text.strip())

            selist = []
            sideeffect = soup.find_all('div',class_ = 'DrugOverview__list-container___2eAr6 DrugOverview__content___22ZBX')
            for se in sideeffect:
                li_tags = se.find_all('li')
                for li_tag in li_tags:
                    selist.append(li_tag.text.strip())

            medicine = {'name' : name, 
                        'composition' : composition ,
                        'uses': use , 
                        'side effects': selist}

            medlist.append(medicine)
            i+=1
            print('Saving...',medicine['name'],">>",i)

       

    df = pd.DataFrame(medlist)

    df.to_csv(f'C:/Users/linto/Downloads/medicine_{letter}.csv', index=False)
    print('Your file is ready!!')
