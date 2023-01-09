import json, os, asyncio
from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#[+] Load Details And AMQ Songs From File First [+]#
load_dotenv("Private/.env")
fullList = open('Songs/songsList.json', encoding="utf-8"); loadSongs = json.load(fullList)


"""
TODO:
Remove the extra requests for more accurate ids
Add error handlers for pop ups and such
Do Create Room
"""

async def menu():
    if os.getenv('USER') == '' or os.getenv('PASSWORD') == '':
        print("[+] Please go to Private/.env and fill in the Username and Password before continuing.\n[+] THIS WILL CLOSE IN 10 SECONDS")
        await asyncio.sleep(10)
        quit(0)

    print("""\n1) Train The Bot\n2) Join Game\n3) Create Room\n4) Quit\nUse 1, 2, 3 or 4 to pick.\n""")

    userInput = int(input("[+] Enter Number : "))
    if userInput == 1:
        await setUp(0)

    if userInput == 2:
        await setUp(1)

    if userInput == 3:
        pass
    
    if userInput == 4:
        quit(0)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Arguments For Chrome And Options [+]#
async def setUp(selection: int):
    chromeOptions = Options()
    chromeOptions.add_experimental_option("detach", True)
    chromeOptions.add_argument("--mute-audio")
    #chromeOptions.add_argument('headless') #<-- This is to prevent chrome from actually opening up. EXPERIMENTAL THOUGH MAY BREAK THE BOT
    #chromeOptions.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chromeOptions)
    await loggingIn(driver, selection)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Log Into The Account [+]#
async def loggingIn(driver: webdriver.Chrome, selection: int):
    driver.get(f"https://animemusicquiz.com/")
    driver.implicitly_wait(5)

    #[+] Logging in [+]#
    driver.find_element(By.ID, 'loginUsername').send_keys(os.getenv('USER')) #Username
    driver.find_element(By.ID, 'loginPassword').send_keys(os.getenv('PASSWORD')) #Password
    driver.find_element(By.ID, 'loginButton').click() #Login Button

    try:
        if driver.find_element(By.CLASS_NAME, 'modal-title').text == 'Account Already Logged In':
            driver.find_element(By.ID, 'alreadyOnlineContinueButton').click()
    except: pass

    #[+] Select What The User Wants To Do [+]#
    if selection == 0:
        await Training(driver)
    
    if selection == 1:
        await Multiplayer(driver)
    
    if selection == 2:
        pass

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Logging Into AMQ and Joining Room -> TRAINING ONLY [+]#
async def Training(driver: webdriver.Chrome):
    driver.implicitly_wait(10)
    
    try:
        popUpText = driver.find_element(By.ID, 'swal2-title').text
        if popUpText == 'Rejoin Disconnect Game':
            driver.find_element(By.CLASS_NAME, 'swal2-cancel.swal2-styled').click()
    except:
        pass

    #[+] Create Room [+]#
    driver.find_element(By.ID, 'mpPlayButton').click() #Click Play Button 
    driver.find_element(By.ID, 'gmsSinglePlayer').click() #Click Solo

    driver.implicitly_wait(10)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/a').click()
    
    #[+] Config Settings [+]#
    if os.getenv('TRAIN') == 'False':
        driver.find_element(By.ID, 'mhHostButton').click() #Click Host
        driver.find_element(By.ID, 'lbStartButton').click() #Start Game
    else:
        #driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[8]/div/div/div[3]/div[2]/div[2]/div[3]/div[4]/div[1]/div/div/div/div[6]/div[1]').click() #Random
        driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[8]/div/div/div[3]/div[2]/div[2]/div[3]/div[4]/div[2]/div/div/div[3]/div/label/i').click() #Insert Song
        driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[8]/div/div/div[3]/div[2]/div[2]/div[4]/div[4]/div[1]/div[1]/div[3]/div/label/i').click() # Difficulty to Hard
        driver.find_element(By.ID, 'mhNumberOfSongsText').send_keys('100') # Amount of Songs
        driver.find_element(By.ID, 'mhHostButton').click() #Click Host
        driver.find_element(By.ID, 'lbStartButton').click() #Start Game

    #[+] Start Game [+]#
    await PlayGame(driver)

# _________________________________________________________________________________________________________________________________________________________________ #

#[+] Logging Into AMQ and Joining Room -> MULTIPLAYER ONLY [+]#
async def Multiplayer(driver: webdriver.Chrome):
    driver.implicitly_wait(10)

    try:
        popUpText = driver.find_element(By.ID, 'swal2-title').text
        if popUpText == 'Rejoin Disconnect Game':
            driver.find_element(By.CLASS_NAME, 'swal2-cancel.swal2-styled').click()
    except: pass

    #[+] Find Room [+]#
    driver.find_element(By.ID, 'mpPlayButton').click() #Click Play Button 
    driver.find_element(By.ID, 'gmsMultiplayer').click() #Click Multiplayer

    driver.implicitly_wait(5)
    
    #[+] Join Find Room [+]#
    driver.find_element(By.ID, 'rbSearchInput').send_keys(os.getenv('Room_Name')) #Find Room
    getRoom = driver.find_element(By.ID, f"rbRoom-{os.getenv('Room_Code')}")
    getRoom.find_element(By.CLASS_NAME, 'rbrJoinButton').click()
    
    #[+] If Password Is Needed As For Password [+]#
    if driver.find_element(By.CLASS_NAME, 'swal2-input'):
        driver.find_element(By.CLASS_NAME, 'swal2-input').send_keys(os.getenv('Room_Password'))
        driver.find_element(By.CLASS_NAME, 'swal2-confirm').click()

    driver.find_element(By.ID, 'lbStartButton').click()

    #[+] Ready Up [+]#
    await PlayGame(driver)

# _________________________________________________________________________________________________________________________________________________________________ #

async def PlayGame(driver: webdriver.Chrome):
    gameStarted = False
    addToList, requestChecked = True, False

    # [+] Ready Up and wait until game is started.
    while gameStarted == False:
        if driver.find_element(By.XPATH, "//div[@id='lbStartButton']//h1").text == 'Unready':
            pass
        else:
            gameStarted = True

    # [+] Game started
    while gameStarted == True:
        checker = driver.find_element(By.ID, 'qpHiderText').text

        if checker.isdigit() == True and requestChecked == False:
            addToList, requestChecked = False, True

            for request in driver.requests:
                if request.url.startswith('https://nl.catbox.video'):
                    url = request.url
                    animeID = request.url.replace('https://nl.catbox.video/', '')[:6]

            if animeID in loadSongs:
                answer = loadSongs[animeID]['name']
            else:
                answer = 'Unknown Song'
            
            #[+] Send Song Into Input Field [+]#
            inputField = driver.find_element(By.ID, 'qpAnswerInput')
            inputField.send_keys(answer)
            inputField.send_keys(Keys.ENTER)
            driver.requests.clear()

        if checker.isdigit() == False and addToList == False and checker != 'Answers':
            addToList, requestChecked = True, False
            animeName = driver.find_element(By.ID, 'qpAnimeName').text

            if animeID in loadSongs and answer != 'Unknown Song' and answer != animeName:
                loadSongs[animeID]['name'] = animeName
                with open('Songs/songsList.json', 'w+') as f:
                    json.dump(loadSongs, f, indent=4)
                    f.close()
                    print(f"[=] '{animeName}' has been corrected in the JSON -> ID {animeID}")
                            
            if answer == 'Unknown Song' and animeID not in loadSongs:
                with open ('Songs/songsList.json', 'a+', encoding='utf-8') as file:
                    file.write(f'''    "{animeID}": ''' + '{{"name": "{0}", "VideoLink": "{1}"}},\n'.format(animeName, url))
                    print(f"[=] Added '{animeName}' with URL -> {url}")
                    file.close()

        if driver.find_element(By.ID, 'qpAnimeName').text == '': # Check to see if anime video has finished playing
            requestChecked = False
    
        #[+] If Game Is Over, Automatically Ready Up Or Start Game. [+]#
        readyOrStart = driver.find_element(By.XPATH, "//div[@id='lbStartButton']//h1").text
        if readyOrStart == 'Start' or readyOrStart == 'Ready':
            driver.find_element(By.ID, 'lbStartButton').click()
            PlayGame(driver)
        else:
            pass

# _________________________________________________________________________________________________________________________________________________________________ #

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(menu())
