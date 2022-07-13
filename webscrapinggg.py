from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime
from datetime import date
import asyncio
import parametry
#kodowanie, unicode(latin-1 supplement)

def konwersja_czasu(czas):
    miesiac = {'stycznia':'1',
		     'lutego':'2',
    	     'marca':'3',
    	     'kwietnia':'4',
    	     'maja':'5',
             'czerwca':'6',
    	     'lipca':'7',
    	     'sierpnia':'8',
    	     'wrze\u015bnia':'9',
    	     'pa\u017adziernika':'10',
    	     'listopada':'11',
    	     'grudnia':'12'
             }

    czas = czas.split()

    if ':' in czas[-1]:
        teraz = str(date.today().strftime("%d-%m-%Y"))
        teraz += ' ' + czas[-1]
        teraz = datetime.strptime(teraz, "%d-%m-%Y %H:%M")
        return teraz
    else:
        teraz = str(date.today().strftime('%d-%m-%Y %H:%M'))
        teraz = datetime.strptime(teraz, "%d-%m-%Y %H:%M")
        teraz = teraz.replace(month=int(miesiac[czas[-2]]),day=int(czas[-3]))
        return teraz



async def radar(msg, login, haslo):
    to_update = parametry.bot.send_message(msg.chat.id, 'Uruchamianie bota...')

    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-gpu')
    options.add_argument('load-extension=' + parametry.sciezka_adblock_malina)
    options.binary_location = parametry.sciezka_chrome_malina #wersja chrome(przegladarka)
    #ChromeDriverManager().install()
    #'C:/Users/kacpe/Downloads/chromedriver_win32/chromedriver.exe' wersja chromedriver
    browser = webdriver.Chrome(service=Service(parametry.sciezka_chromedriver_malina), options=options)

    #wejscie na strone
    browser.get('https://www.olx.pl/konto/?ref%5B0%5D%5Baction%5D=myaccount&ref%5B0%5D%5Bmethod%5D=index')
    #akceptacja cookies
    try:
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        browser.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except:
        pass
    #znalezienie i podanie pasow
    browser.find_element(By.ID, 'userEmail').send_keys(login)
    browser.find_element(By.ID, 'userPass').send_keys(haslo)
    #logowanie
    browser.find_element(By.ID, 'se_userLogin').click()
    try:
        WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Ups! Co\u015b posz\u0142o nie tak')]")))
        browser.find_element(By.XPATH, "//*[contains(text(),'Ups! Co\u015b posz\u0142o nie tak')]")
        browser.quit()
        parametry.users_id[msg.from_user.id][0] = False
        parametry.bot.send_message(msg.from_user.id, 'Strona OLX nie odpowiada. Spr\u00f3buj ponownie p\u00f3\u017aniej.')
        return
    except:
        pass

    to_update = parametry.bot.edit_message_text(chat_id=to_update.chat.id, message_id=to_update.message_id, text='Logowanie do konta OLX powiod\u0142o si\u0119.')

    #akceptacja pop-upow
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Jasne']")))
        browser.find_element(By.XPATH, "//button[text()='Jasne']").click()
    except:
        pass
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='css-spwpto']")))
        browser.find_element(By.XPATH, "//button[@class='css-spwpto']").click()
    except:
        pass
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Zamknij']")))
        browser.find_element(By.XPATH, "//span[text()='Zamknij']").click()
    except:
        pass

    to_update = parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Zapisywanie obserwowanych wyszukiwa\u0144...')

    #obserwowane wyszukiwania
    browser.get('https://www.olx.pl/obserwowane/wyszukiwania/')
    obserwowane_wyszukiwania = browser.find_elements(By.XPATH, "//a[contains(text(),'nowe:')]")
    url_obserwowane = []

    for wyszukiwanie in obserwowane_wyszukiwania:
        url = wyszukiwanie.get_attribute('href')
        url = url.split('?')
        lewy = url[0]
        prawy = url[1].split('&')
        smieci = ['min_id=','reason=observed_search']

        for i in smieci:
            for j in prawy:
                if i in j:
                    prawy.remove(j)

        if len(prawy) == 1:
            url = str(lewy) + '?' + ''.join(prawy) + '&search%5Border%5D=created_at:desc'
        elif len(prawy) > 1:
            url = '?' + prawy[0]
            for i in range(1,len(prawy)):
                url = url + '&' + prawy[i]
            url = str(lewy) + url + '&search%5Border%5D=created_at:desc'
        else:
            url = str(lewy) + '?search%5Border%5D=created_at:desc'
 
        url_obserwowane.append(url)

    #pierwsze ogleszenie do porownania
    ostatnie_zapisane_ogloszenie = pd.DataFrame(columns=['tytul','czas'])

    for url in url_obserwowane:
        browser.get(url)
        ogloszenie = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
        #szukanie przez xpath lub class? patrz stackoverflow bookmarks
        tytul = ogloszenie.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
        czas = ogloszenie.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text
        ostatnie_zapisane_ogloszenie.loc[len(ostatnie_zapisane_ogloszenie)] = [tytul, konwersja_czasu(czas)]

    parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Rozpocz\u0119to skanowanie...')

    while True:
        for indeks, url in enumerate(url_obserwowane):
            #przeszukiwanie 25 stron(tyle jest dostepne)
            for i in range(1,26):
                if(parametry.users_id[msg.from_user.id] == False):
                    browser.quit()
                    parametry.bot.send_message(msg.from_user.id, 'Bot zostal zamkniety')
                    return

                url_strona = url
                if i != 1:
                    url_strona = url + '&page=' + str(i)
                browser.get(url_strona)
                browser.refresh()

                #porownuje czas ostatnio zapisanego ogloszenia z aktualnymi, aby nie przechodzic przez wszystkie 25 stron
                WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")))
                czas_porownanie = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
                czas_porownanie = konwersja_czasu(czas_porownanie.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text)

                if czas_porownanie < ostatnie_zapisane_ogloszenie.iloc[indeks,1]:
                    browser.get(url)
                    browser.refresh()
                    nowy = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
                    tytul = nowy.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
                    czas = nowy.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text
                    ostatnie_zapisane_ogloszenie.loc[indeks] = [tytul, konwersja_czasu(czas)]
                    break

                if len(browser.find_elements(By.XPATH, f"//h6[text()='{ostatnie_zapisane_ogloszenie.iloc[indeks,0]}']")) == 1:
                    WebDriverWait(browser, 60).until(EC.presence_of_all_elements_located((By.XPATH, f"//h6[text()='{ostatnie_zapisane_ogloszenie.iloc[indeks,0]}']//ancestor::div[@data-cy='l-card']//preceding-sibling::div[@data-cy='l-card']")))
                    znalezione = browser.find_elements(By.XPATH, f"//h6[text()='{ostatnie_zapisane_ogloszenie.iloc[indeks,0]}']//ancestor::div[@data-cy='l-card']//preceding-sibling::div[@data-cy='l-card']")

                    znalezione2 = []
                    if len(znalezione) > 0:
                        for k in znalezione:
                            try:
                                k.find_element(By.XPATH, ".//div[@data-testid='adCard-featured']")                                
                            except:
                                znalezione2.insert(0,k)
                    

                    #nie ma nowych ogloszen
                    if i == 1 and len(znalezione2) == 0:
                        break

                    #sa nowe ogloszenia na 1 stronie
                    if i == 1 and len(znalezione2) > 0:
                        for j in znalezione2:
                            tytul = j.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
                            cena = j.find_element(By.XPATH, ".//p[contains(text(),'z\u0142')]").text
                            lokalizacja = j.find_element(By.CLASS_NAME, "css-p6wsjo-Text.eu5v0x0").text.split('-')[0]
                            link = j.find_element(By.XPATH, "./a").get_attribute('href')

                            parametry.bot.send_message(msg.from_user.id, f'Co: {tytul}\nCena: {cena}\nGdzie: {lokalizacja}\n{link}')
                        
                        najnowsze_ogloszenie = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
                        ostatnie_zapisane_ogloszenie.iloc[indeks,0] = najnowsze_ogloszenie.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text #tytul
                        ostatnie_zapisane_ogloszenie.iloc[indeks,1] = konwersja_czasu(najnowsze_ogloszenie.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text) #czas 

                        break

                    #siblingsy na ostatniej stronie
                    if len(znalezione2) > 0:
                        for j in znalezione2:
                            tytul = j.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
                            cena = j.find_element(By.XPATH, ".//p[contains(text(),'z\u0142')]").text
                            lokalizacja = j.find_element(By.CLASS_NAME, "css-p6wsjo-Text.eu5v0x0").text.split('-')[0]
                            link = j.find_element(By.XPATH, "./a").get_attribute('href')

                            parametry.bot.send_message(msg.from_user.id, f'Co: {tytul}\nCena: {cena}\nGdzie: {lokalizacja}\n{link}')
                    else:
                        #brak siblingsow na ostatniej stronie, ale sa nowe ogloszenia na wczesniejszych stronach
                        pass

                    for j in range(i-1,0,-1):
                        url_strona = url
                        if j != 1:
                            url_strona = url + '&page=' + str(j)
                        browser.get(url_strona)
                        browser.refresh()

                        WebDriverWait(browser, 60).until(EC.presence_of_elements_located((By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")))
                        x = browser.find_elements(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")

                        for k in range(len(x)-1,-1,-1):
                            tytul = x[k].find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
                            cena = x[k].find_element(By.XPATH, ".//p[contains(text(),'z\u0142')]").text
                            lokalizacja = x[k].find_element(By.CLASS_NAME, "css-p6wsjo-Text.eu5v0x0").text.split('-')[0]
                            link = x[k].find_element(By.XPATH, "./a").get_attribute('href')

                            parametry.bot.send_message(msg.from_user.id, f'Co: {tytul}\nCena: {cena}\nGdzie: {lokalizacja}\n{link}')

                    #zapisanie najnowszego ogloszenia na ten moment
                    najnowsze_ogloszenie = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
                    ostatnie_zapisane_ogloszenie.iloc[indeks,0] = najnowsze_ogloszenie.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text #tytul
                    ostatnie_zapisane_ogloszenie.iloc[indeks,1] = konwersja_czasu(najnowsze_ogloszenie.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text) #czas

                    break
            #ostatnio zapisane ogloszenie poza zasiegiem
            if i == 25:
                browser.get(url)
                browser.refresh()
                x = browser.find_element(By.XPATH, "//div[@class='css-3xiokn' and not(./*[contains(@data-testid,'adCard-featured')])]//ancestor::div[@data-cy='l-card']")
                tytul = x.find_element(By.CLASS_NAME, 'css-v3vynn-Text.eu5v0x0').text
                czas = x.find_element(By.CLASS_NAME, 'css-p6wsjo-Text.eu5v0x0').text
                ostatnie_zapisane_ogloszenie.loc[indeks] = [tytul, konwersja_czasu(czas)]

        await asyncio.sleep(30)
