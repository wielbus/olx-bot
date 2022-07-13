from telebot import types
import webscrapinggg
import asyncio
import parametry
#import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

#logger = parametry.telebot.logger
#logger.setLevel(logging.DEBUG)


@parametry.bot.message_handler(commands=['signup'])
def start(msg):

    try:
        print(parametry.users_id[msg.from_user.id][0])
        parametry.bot.send_message(msg.chat.id, 'Jestes juz zarejestrowany.')
        return
    except:
        pass

    parametry.users_id[msg.from_user.id] = [False]    
    parametry.bot.send_message(msg.chat.id, 'Zarejestrowano pomyslnie.')

#obsluguje komende: login [twoj login] [twoje haslo]
def pasy(msg):

    message = msg.text.split()

    if not message[0].startswith('/',0):
        try:
            print(parametry.users_id[msg.from_user.id][0])
            if len(message) == 3 and message[0] == 'login':
                try:
                    print(parametry.users_id[msg.from_user.id][1],parametry.users_id[msg.from_user.id][2])
                    parametry.bot.send_message(msg.chat.id, 'Dane logowania sa juz zapisane. Mozesz uruchomic bota /on')
                    return False
                except:
                    return True
            else:
                parametry.bot.send_message(msg.chat.id, 'Zle wprowadzone dane logowania lub nieobslugiwana komenda.\nPoprawny schemat logowania:\n\nlogin [twoj login] [twoje haslo]')
                return False
        except:
            parametry.bot.send_message(msg.chat.id, 'Wymagana rejestracja. Kliknij /signup')
            return False
    else:
        return False
      


@parametry.bot.message_handler(func=pasy)
def login(msg):

    to_update = parametry.bot.send_message(msg.from_user.id, 'Sprawdzanie poprawno\u015bci danych...\nNiczego nie klikaj')

    message = msg.text.split()
    user_login = message[1]
    user_pass = message[2]

    #sprawdzenie istnienia konta OLX
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-gpu')
    options.add_argument('load-extension=' + parametry.sciezka_adblock_malina)
    options.binary_location = parametry.sciezka_chrome_malina
    browser = webdriver.Chrome(service=Service(parametry.sciezka_chromedriver_malina), options=options)
    browser.get('https://www.olx.pl/konto/?ref%5B0%5D%5Baction%5D=myaccount&ref%5B0%5D%5Bmethod%5D=index')
    #akceptacja cookies
    try:
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        browser.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except:
        pass
    #sprawdzenie poprawnosci formatu e-mail
    browser.find_element(By.ID, 'userEmail').send_keys(user_login)
    browser.find_element(By.XPATH, "//a[text()='Zaloguj si\u0119']").click()
    try:
        browser.find_element(By.XPATH, "//*[contains(text(),'Niepoprawny format e-mail')]")
        browser.quit()
        parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Niepoprawny format e-mail. Wprowadz dane logowania jeszcze raz.')
        return
    except:
        pass

    browser.find_element(By.ID, 'userPass').send_keys(user_pass)
    #logowanie
    browser.find_element(By.ID, 'se_userLogin').click()
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Nieprawid\u0142owy login lub has\u0142o')]")))
        browser.find_element(By.XPATH, "//*[contains(text(),'Nieprawid\u0142owy login lub has\u0142o')]")
        browser.quit()
        parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Nieprawid\u0142owy login lub has\u0142o. Wprowadz dane logowania jeszcze raz.')
        return
    except:
        pass
    browser.quit()
    #try:
    #    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Ups! Co\u015b posz\u0142o nie tak')]")))
    #    browser.find_element(By.XPATH, "//*[contains(text(),'Ups! Co\u015b posz\u0142o nie tak')]")
    #    browser.quit()
    #    parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Strona OLX nie odpowiada. Spr\u00f3buj ponownie p\u00f3\u017aniej.')
    #    return
    #except:
    #    browser.quit()

    parametry.users_id[msg.from_user.id].extend([user_login, user_pass])
    parametry.bot.edit_message_text(chat_id = to_update.chat.id, message_id = to_update.message_id, text = 'Podane konto istnieje. Login i has\u0142o zosta\u0142y zapisane.')


@parametry.bot.message_handler(commands=['on','off'])
def launch(msg):

    try:
        print(parametry.users_id[msg.from_user.id][0])
        try:
            print(parametry.users_id[msg.from_user.id][1], parametry.users_id[msg.from_user.id][2])
        except:
            parametry.bot.send_message(msg.chat.id, 'Brak danych logowania do konta OLX. Uzyj komendy:\nlogin [twoj login] [twoje haslo]')
            return
    except:
        parametry.bot.send_message(msg.chat.id, 'Wymagana rejestracja. Kliknij /signup')
        return

    if msg.text == '/on':
        if(parametry.users_id[msg.from_user.id][0] == False):
            parametry.users_id[msg.from_user.id][0] = True
            print(parametry.users_id)
            asyncio.run(webscrapinggg.radar(msg, parametry.users_id[msg.from_user.id][1], parametry.users_id[msg.from_user.id][2]))
        else:
            parametry.bot.send_message(msg.chat.id, 'Bot jest juz wlaczony')
            print(parametry.users_id)
    if msg.text == '/off':
        if(parametry.users_id[msg.from_user.id][0] == True):
            parametry.users_id[msg.from_user.id][0] = False
            print(parametry.users_id)
            parametry.bot.send_message(msg.chat.id, 'Zamykanie bota...')
        else:
            parametry.bot.send_message(msg.chat.id, 'Bot nie jest wlaczony. Kliknij /on, zeby wlaczyc')
            print(parametry.users_id)


@parametry.bot.message_handler(commands=['status'])
def status(msg):

    try:
        print(parametry.users_id[msg.from_user.id][0])
    except:
        parametry.bot.send_message(msg.chat.id, 'Wymagana rejestracja. Kliknij /signup')
        return

    parametry.bot.send_message(msg.chat.id, f'Aktualny stan bota: *{parametry.users_id[msg.from_user.id][0]}*', parse_mode= 'Markdown')


@parametry.bot.message_handler(commands=['help'])
def help(msg):

    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('/on')
    btn2 = types.KeyboardButton('/off')
    btn3 = types.KeyboardButton('/status')
    btn4 = types.KeyboardButton('/signup')
    btn5 = types.KeyboardButton('/help')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    parametry.bot.send_message(msg.chat.id, '/on - uruchamia bota\n/off - zamyka bota\n/status - aktualny stan bota(skanuje/nie skanuje)\n/signup - rejestracja', reply_markup = markup)

    parametry.bot.send_message(msg.chat.id, 'Aby podac dane logowania do konta OLX, uzyj ponizszej komendy:\n\nlogin [twoj login] [twoje haslo]')



parametry.bot.infinity_polling()