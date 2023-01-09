import json
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#[+] Load Details And AMQ Songs From File First [+]#
detailsFile = open('details.json',  encoding="utf-8"); loadFile = json.load(detailsFile)
amqScraper = open('songsList.json', encoding="utf-8"); loadAMQ = json.load(amqScraper)

"""
TODO:
Remove the extra requests for more accurate ids
Add error handlers for pop ups and such
Do Create Room
Fix Amount of song Settings
May have to rewrite entire thing
"""

def menu():
    print("""\n1) Train The Bot\n2) Join Game\n3) Create Room\n4) Quit\nUse 1, 2, 3 or 4 to pick.\n""")

    userInput = int(input("[+] Enter Number : "))
    if userInput == 1:
        setUp('Train')

    if userInput == 2:
        setUp('Multi')

    if userInput == 3:
        pass
    
    if userInput == 4:
        quit(0)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Arguments For Chrome And Options [+]#
def setUp(selection: str):
    chromeOptions = Options()
    chromeOptions.add_experimental_option("detach", True)
    chromeOptions.add_argument("--mute-audio")
    #chromeOptions.add_argument('headless') #<-- This is to prevent chrome from actually opening up. EXPERIMENTAL THOUGH MAY BREAK THE BOT
    chromeOptions.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chromeOptions, service_log_path='NUL') #Mute those annoying chrome logs
    loggingIn(driver, selection)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Log Into The Account [+]#
def loggingIn(driver: webdriver.Chrome, selection: str):
    driver.get(f"https://animemusicquiz.com/")
    driver.implicitly_wait(5)

    #[+] Logging in [+]#
    driver.find_element(By.ID, 'loginUsername').send_keys(loadFile['account']['username']) #Username
    driver.find_element(By.ID, 'loginPassword').send_keys(loadFile['account']['password']) #Password
    driver.find_element(By.ID, 'loginButton').click() #Login Button

    if driver.find_element(By.CLASS_NAME, 'modal-title').text == 'Account Already Logged In':
        driver.find_element(By.ID, 'alreadyOnlineContinueButton').click()

    #[+] Select What The User Wants To Do [+]#
    if selection == 'Train':
        Training(driver, 'Train')
    
    if selection == 'Multi':
        Multiplayer(driver, 'Multi')
    
    if selection == 'Create':
        pass

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Logging Into AMQ and Joining Room -> TRAINING ONLY [+]#
def Training(driver: webdriver.Chrome, selection: str):
    driver.implicitly_wait(10)
    
    try:
        popUpText = driver.find_element(By.ID, 'swal2-title').text
        if popUpText == 'Rejoin Disconnect Game':
            driver.find_element(By.CLASS_NAME, 'swal2-cancel.swal2-styled').click()
    except:
        pass

    #[+] Create Room [+]#
    driver.find_element(By.ID, 'mpPlayButton').click() #Click Play Button 
    driver.find_element(By.ID, 'gmsSinglePlayer').click() #Click Multiplayer

    driver.implicitly_wait(5)
    
    #[+] Config Settings [+]#
    songSelect = loadFile['trainingDetails']['SongSelection']
    songTypes = loadFile['trainingDetails']['SongTypes']
    songDiff = loadFile['trainingDetails']['SongDiff']
    AmountOfSongs = loadFile['trainingDetails']['SongAmount']
    
    for songSel in songSelect:
        if songSelect[songSel] == 'True':
           try: driver.find_element(By.XPATH, songSelect[songSel[6:]]).click()
           except: pass

    for songSel in songTypes:
        if songTypes[songSel] == 'True':
            try: driver.find_element(By.XPATH, songTypes[songSel[6:]]).click()
            except: pass
        
    for songSel in songDiff:
        if songDiff[songSel] == 'True':
            try: driver.find_element(By.XPATH, songDiff[songSel[6:]]).click()
            except: pass

    driver.find_element(By.ID, 'mhNumberOfSongsText').send_keys(AmountOfSongs)
    driver.find_element(By.ID, 'mhHostButton').click() #Click Host
    driver.find_element(By.ID, 'lbStartButton').click()

    #[+] Start Game [+]#
    PlayGame(driver, selection)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Logging Into AMQ and Joining Room -> MULTIPLAYER ONLY [+]#
def Multiplayer(driver: webdriver.Chrome, selection: str):
    driver.implicitly_wait(10)

    try:
        #swal2-confirm.swal2-style <---- Confirm text
        popUpText = driver.find_element(By.ID, 'swal2-title').text
        if popUpText == 'Rejoin Disconnect Game':
            driver.find_element(By.CLASS_NAME, 'swal2-cancel.swal2-styled').click()
    except:
        pass

    #[+] Find Room [+]#
    driver.find_element(By.ID, 'mpPlayButton').click() #Click Play Button 
    driver.find_element(By.ID, 'gmsMultiplayer').click() #Click Multiplayer

    driver.implicitly_wait(5)
    
    #[+] Join Find Room [+]#
    driver.find_element(By.ID, 'rbSearchInput').send_keys(loadFile['roomDetails']['name']) #Find Room
    getRoom = driver.find_element(By.ID, f"rbRoom-{loadFile['roomDetails']['code']}")
    getRoom.find_element(By.CLASS_NAME, 'rbrJoinButton').click()
    
    #[+] If Password Is Needed As For Password [+]#
    if driver.find_element(By.CLASS_NAME, 'swal2-input'):
        driver.find_element(By.CLASS_NAME, 'swal2-input').send_keys(loadFile['roomDetails']['password'])
        driver.find_element(By.CLASS_NAME, 'swal2-confirm').click()

    driver.find_element(By.ID, 'lbStartButton').click()

    #[+] Ready Up [+]#
    PlayGame(driver, selection)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Let The Bot Play The Game [+]#
def PlayGame(driver: webdriver.Chrome, selection: str):
    gameStarted, answer = False, ''
    addedToList, checkRequest = False, False

    #[+] If Bot Isn't Ready Up, It Will Automatically Do So. [+]#
    while gameStarted == False:
        if driver.find_element(By.XPATH, "//div[@id='lbStartButton']//h1").text == 'Unready':
            pass
        else:
            gameStarted = True

    #[+] Get Code From Requests, And Look Into JSON File And Grab Song Name [+]#
    while gameStarted == True:
        checker = driver.find_element(By.ID, 'qpHiderText').text

        #[+] Check To See If Video Is Not Playing Or Buffering, If Not Then Continue [+]#
        if checker.isdigit() == True and checkRequest == False:
            addedToList = False
            checkRequest = True
            
            #[+] Grab All Requests From List
            for request in driver.requests:
                #[+] Check To See If List Contains A Url That Starts With nl.catbox
                if request.url.startswith('https://nl.catbox.video'):
                    #[+] Set URL and Anime To Variable And Delete The Url From List, So It Prevents Clutter + Other IDs Taking It. [+]#
                    url = request.url
                    animeID = url.replace('https://nl.catbox.video/', '')[:6]
                del driver.requests

            #[+] Check To See If ID Exists, Else Set As Unknown Song. [+]#
            if animeID in loadAMQ:
                answer = loadAMQ[animeID]['name']
            else:
                answer = 'Unknown Song'

            #[+] Send Song Into Input Field [+]#
            inputField = driver.find_element(By.ID, 'qpAnswerInput')
            inputField.send_keys(answer)
            inputField.send_keys(Keys.ENTER)
        
        if checker == '':
            checkRequest = False
            animeName = driver.find_element(By.ID, 'qpAnimeName').text

            #[+] In case of a slip up, this will replace
            if answer != 'Unknown Song' and answer != animeName and addedToList == False:
                if animeID in loadAMQ:
                    loadAMQ[animeID]['name'] = animeName
                    print(f"[=] '{animeName}' has been corrected in the DB -> ID {animeID}")
                    addedToList = True

            #[+] If Bot Cant Find Song, Add To List [+]#
            if answer == 'Unknown Song' and addedToList == False:                
                if animeID not in loadAMQ:
                    with open('songsList.json', 'a', encoding='utf-8') as song:
                        song.write(f'''    "{animeID}": ''' + '{{"name": "{0}", "VideoLink": "{1}"}},\n'.format(animeName, url))
                        print(f"[=] Added '{animeName}' with URL -> {url}")
                        addedToList = True

        #[+] If Game Is Over, Automatically Ready Up Or Start Game. [+]#
        readyOrStart = driver.find_element(By.XPATH, "//div[@id='lbStartButton']//h1").text
        if readyOrStart == 'Start' or readyOrStart == 'Ready':
            driver.find_element(By.ID, 'lbStartButton').click()
            PlayGame(driver)
        else:
            pass

# _________________________________________________________________________________________________________________________________________________________________ #

menu()