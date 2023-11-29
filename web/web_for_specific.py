import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs
import string

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
}

file = pd.read_csv('C:/Users/linto/Downloads/notfound.csv',header=None)

file = file.values[1:]

productlinks = file
medlist = []
med_unfetched = []


i = 0
for link in productlinks:
        try:
            r = requests.get(link[0], headers=headers, timeout=90)
            r.raise_for_status()  # Check for HTTP errors
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            med_unfetched.append(link)
            continue
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            time.sleep(5)  # Wait for a few seconds before retrying
            med_unfetched.append(link)
            continue
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            med_unfetched.append(link)
            continue
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            med_unfetched.append(link)
            continue

        soup = BeautifulSoup(r.content, 'html.parser')
        name = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
        if name:
            name = name.text.strip()
        else:
            name = link

        composition = soup.find('div', class_='saltInfo DrugHeader__meta-value___vqYM0')
        if composition:
            composition = composition.text.strip()
        else:
            composition = None

        useslist = soup.find_all('ul', class_='DrugOverview__list___1HjxR DrugOverview__uses___1jmC3')
        use = [a_tag.text.strip() for uses in useslist for a_tag in uses.find_all('li')]

        selist = []
        sideeffect = soup.find_all('div', class_='DrugOverview__list-container___2eAr6 DrugOverview__content___22ZBX')
        selist = [li_tag.text.strip() for se in sideeffect for li_tag in se.find_all('li')]

        medicine = {'name': name, 'composition': composition, 'uses': use, 'side effects': selist}
        medlist.append(medicine)
        i += 1
        print('Saving...', medicine['name'], ">>", i)
        

df = pd.DataFrame(medlist)
unfetched = pd.DataFrame(med_unfetched)
df.to_csv(f'C:/Users/linto/Downloads/medicine_found.csv', index=False)
unfetched.to_csv(f'C:/Users/linto/Downloads/medicine_notfound.csv', index=False)
print('Your file is ready!!')
