import sys
import getpass
import imaplib
import os
import time
import re
import itertools

from Tkinter import*
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#globals
global BindingOfIsaac
global HeroesComplete
global PrisonArchitect
global DarkSouls
global Civ5Complete
global SaintsRow4
global WalkingDead2
global Skyrim
global SevenDays
BindingOfIsaac = '672427722'
HeroesComplete = '675668842'
PrisonArchitect = '672470779'
DarkSouls = '673034635'
Civ5Complete = '674146614'
SaintsRow4 = '672898268'
WalkingDead2 = '674183229'
Skyrim = '672985606'
SevenDays = '309549539'

# class for gui window to get user and pass
class gui:
    def __init__(self, master):
        self.master = master
        
        # labels for each entry
        Label(self.master, text="Steam Username").grid(row=0)
        Label(self.master, text="Steam Password").grid(row=1)
        Label(self.master, text="Email Password").grid(row=2)
        
        # button widget
        self.steamUserW = Entry(self.master)
        self.steamPassW = Entry(self.master, show="*")
        self.emailPassW = Entry(self.master, show="*")
        self.submit = Button(self.master, text="Submit", command=self.assign)

        # bind the ENTER key to callback function
        self.emailPassW.bind("<Return>", self.assign)
        self.emailPassW.bind("<KP_Enter>", self.assign)

        # space out the widgets
        self.steamUserW.grid(row=0, column=1)
        self.steamPassW.grid(row=1, column=1)
        self.emailPassW.grid(row=2, column=1)
        self.submit.grid(row=3, column=1)
        
    # grabs the values in the entry boxes and assigns them to variable
    def assign(self, *args):
        self.steamUser = self.steamUserW.get()
        self.steamPass = self.steamPassW.get()
        self.emailPass = self.emailPassW.get()
        self.close()
            
    # closes GUI window
    def close(self):
        self.master.destroy()

root = Tk()
userGui = gui(root)
root.mainloop()
steamUser = userGui.steamUser
steamPass = userGui.steamPass
emailPass = userGui.emailPass


# open up log-in screen
chromedriver = "/Users/Justin/Desktop/Steam Gifts/Programs/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)
driver.get("https://steamcommunity.com/login/home/")

# enter username and password
username = driver.find_element_by_id("steamAccountName")
username.send_keys(steamUser)
password = driver.find_element_by_id("steamPassword")
password.send_keys(steamPass, Keys.TAB, Keys.ENTER)


# process mailbox to get special code
# get Steam access code from e-mail
def process_mailbox(steamUser):
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    M.login('youremail@gmail.com', emailPass)
    rv, data = M.select("Steam Access")
    rv, data = M.search(None,'(UNSEEN)')
    
    ids = data[0] # data is a list
    id_list = ids.split() # ids is a space seperated string

    # parses email, creates folder, gets the secret code and returns it
    for i in range(len(id_list)):
        # get e-mail body text
        result, data = M.fetch(id_list[i], "(RFC822)")
        
        # get the secret code from gmail
        startPos = data[0][1].find("Here is the Steam Guard code you need to login to account")
        M.close()
        M.logout()
        print data[0][1]
        return data[0][1][startPos+63+len(steamUser):startPos+68+len(steamUser)]

specialCode = None
while specialCode == None:
    specialCode = process_mailbox(steamUser) # ... do something with emails, see below ...

# input special code
specialCodeForm = driver.find_element_by_id("authcode")
specialCodeForm.send_keys(specialCode)

# input computer name
computerNameForm = driver.find_element_by_id("friendlyname")
computerNameForm.send_keys("Firefox Steam Gifts")
#driver.find_element_by_css_selector('auth_button.leftbtn').click()
driver.find_element_by_xpath("//*[@id='auth_buttonset_entercode']/div[1]").click()

# get JSON data
wait = WebDriverWait(driver,10)
element = wait.until(EC.visibility_of_element_located((By.ID, "success_continue_btn")))
driver.get("http://steamcommunity.com/id/" + steamUser + "/inventory/json/753/1")

# extract the instance brackets into linkData
linkData = re.findall(r'{"id".*?}', driver.page_source)
print linkData

# get links for each gift (instanceids and classids for custom game)
linkList = []
for links in linkData:
    instanceid = re.findall(r'"instanceid":"(\d*)', links)
    classid = re.findall(r'"classid":"(\d*)', links)
    #if instanceid[0] == '0' or classid[0] == DarkSouls or classid[0] == '672446220':
    id = re.findall(r'"id":"(\d*)', links)
    linkList.append("http://store.steampowered.com/checkout/sendgift/" + id[0])

# generator function to get different combinations of  my e-mail
def emailComboGen():
    combList = ['y','o','u','r','e','m','a','i','l']
    combNumbers = []
    i = 1
    j = 2
    k = 0

    while i < len(combList):
        combNumbers.append(i)
        i = i + 1

    while j < len(combList):
        emailCombos = itertools.combinations(combNumbers, j)
        for combo in emailCombos:
            combListCopy = combList[:]
            k = 0
            for index in combo:
                combListCopy.insert(index + k, '.')
                k = k + 1
            yield ''.join(combListCopy) + "@gmail.com"
        j = j + 1

# create generator for e-mails
email = emailComboGen()

time.sleep(5)

# go through and fill in forms for each steam gift
for link in linkList:
    # go to email steam gift link
    driver.get(link)
    # fill in e-mail
    emailGift = wait.until(EC.presence_of_element_located((By.ID, "email_input")))
    #emailGift = driver.find_element_by_id("email_input")
    emailGift.send_keys(next(email), Keys.TAB, Keys.ENTER)
    # fill in personalized message forms
    name = driver.find_element_by_id("gift_recipient_name")
    name.send_keys("Sir/Madam")
    message = driver.find_element_by_id("gift_message_text")
    message.send_keys("Have fun with the game, be sure to leave positive feedback :)")
    signature = driver.find_element_by_id("gift_signature")
    signature.send_keys("Justin", Keys.TAB, Keys.TAB, Keys.ENTER)

