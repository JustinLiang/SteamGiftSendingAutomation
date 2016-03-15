import sys
import getpass
import imaplib
import os
import time

from Tkinter import*

# gui window to get pass
class gui:
    def __init__(self, master):
        self.master = master
        
        # labels for each entry
        Label(self.master, text="Email Password").grid(row=0)
        
        # button widget
        self.emailPassW = Entry(self.master, show="*")
        self.submit = Button(self.master, text="Submit", command=self.assign)

        # bind the ENTER key to callback function
        self.emailPassW.bind("<Return>", self.assign)
        self.emailPassW.bind("<KP_Enter>", self.assign)

        # space out the widgets
        self.emailPassW.grid(row=0, column=1)
        self.submit.grid(row=1, column=1)
        
    # grabs the values in the entry boxes and assigns them to variable
    def assign(self, *args):
        self.emailPass = self.emailPassW.get()
        self.close()
            
    # closes GUI window
    def close(self):
        self.master.destroy()

root = Tk()
userGui = gui(root)
root.mainloop()
emailPass = userGui.emailPass


def process_mailbox(M):
    rv, data = M.search(None,'(UNSEEN)')
    
    ids = data[0] # data is a list
    id_list = ids.split() # ids is a space seperated string

    # parses email, creates folder, creates text file and appends steam gift link to text file
    for i in range(len(id_list)):
        # get e-mail body text
        result, data = M.fetch(id_list[i], "(RFC822)")

        # get the name of the game
        startPosSubject = data[0][1].find("Subject: You've received a gift copy of the game ")
        endPosSubject = data[0][1].find("on Steam", startPosSubject)
        gameName = data[0][1][startPosSubject + 49:endPosSubject - 1]
        # remove colons
        if ":" in gameName:
            indexOfColon = gameName.find(":")
            gameName = gameName[0:indexOfColon] + gameName[indexOfColon + 1:]

        # create folder for the day if it does not exist
        folderName = time.strftime('%B %d %y')
        folder = 'C:\\Users\\Justin\\Desktop\\Steam Gifts\\' + folderName + '\\'
        if not os.path.exists(folder):
            os.mkdir(folder)
            
        # create a text file named after the game
        f = open(folder + gameName + '.txt.', 'a')
        
        # get the link for the Steam gift
        startPosGift = data[0][1].find("https://store.steampowered.com/account")
        endPosGift = data[0][1].find(".com", startPosGift + 30)
        steamGift = data[0][1][startPosGift:endPosGift + 4]
        
        # write link to the text file
        f.write(steamGift + '\n')

        f.close()
        
M = imaplib.IMAP4_SSL('imap.gmail.com')
M.login('youremail@gmail.com', emailPass)
    

rv, data = M.select("Steam") # select mailbox label
if rv == 'OK':
    print "Processing mailbox...\n"
    process_mailbox(M) # ... do something with emails, see below ...
    M.close() # close mailbox Steam
M.logout()