from PIL import Image
import smtplib, ssl, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from io import BytesIO
import pandas as pd
from bs4 import BeautifulSoup
import re
from getpass import getpass
import collections
import base64

Login = collections.namedtuple('Login',['username','password'])


class steamItem:
    #amount of gems worth
    #starting price
    #isTradingCard
    #badge progress?
    #inventory(which its in)
    #game
    #item name
    def __init__(self,link):
        self.link=link
        

class SteamWebInstance:
    def __init__(self):
        self.__loginUrl='https://store.steampowered.com/login/?redir=&redir_ssl=1'
        self.__nonBreakSpace = u'\xa0'
        self.__loginInfo=None
        opt=Options()
        #opt.headless=True
        self.driver=webdriver.Firefox(options=opt)
    
    def __getLoginInfo(self):
        user=input('Please enter you Steam username: ')
        password=getpass(prompt='Please enter you Steam password: ')
        self.__loginInfo =Login(user,password)
    
    def start(self):
        self.__wait=WebDriverWait(self.driver,25)
        self.__smallWait=WebDriverWait(self.driver,1)
        self.__login()
        self.__navigateToInventory()
        itemLinks=self.__getItemLinks()
        return itemLinks
    
    def __returnToMainTab(self):
        """
        Needs fixing (Cant remember why)
        """
        handles = self.driver.window_handles
        for handle in handles:
            if handle != self.__mainHandle:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(self.__mainHandle)

    def __openNewTabWithLink(self,link):
        """
        Opens link in a new tab and then switches focus to that tab
        """
        self.driver.execute_script("window.open('');")
        handles=self.driver.window_handles
        size = len(handles)
        parent_handle=self.__mainHandle
        for x in range(size):
            if handles[x] != parent_handle:
                newTab=handles[x]
        self.driver.switch_to.window(newTab)
        self.driver.get(link)
    
    def showElement(self,elem):
        data=elem.screenshot_as_base64
        im=Image.open(BytesIO(base64.b64decode(data)))
        im.show()
        
    def __login(self):
        self.driver.get(self.__loginUrl)
        self.__mainHandle=self.driver.current_window_handle
        self.__getLoginInfo()
        elem=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='username']")))
        elem.send_keys(self.__loginInfo.username)
        passElem=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='password']")))
        passElem.send_keys(self.__loginInfo.password)
        try:
            captchaElem=self.__smallWait.until(EC.visibility_of_element_located((By.XPATH,"//img[@id='captchaImg']")))
            data=captchaElem.screenshot_as_base64
            im=Image.open(BytesIO(base64.b64decode(data)))
            im.show()
            captcha=input('Please enter the captcha: ')
            captchaField=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@name='captcha_text']")))
            captchaField.send_keys(captcha)
            captchaField.send_keys(Keys.ENTER)
        except TimeoutException:
            passElem.send_keys(Keys.ENTER)
            print('No captcha needed')
        try:
            elem=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@id='twofactorcode_entry']")))
            auth=input('Please enter the two factor authentication code: ')
            elem.send_keys(auth)
            elem.send_keys(Keys.ENTER)
        except Exception as _:
            print('No two factor authentication needed')

    def __navigateToInventory(self):
        elem=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//a[@class='menuitem supernav username']")))
        profileLink=elem.get_attribute('href')
        inventoryLink='/'.join(profileLink.split('/')[:-2])+'/inventory/'
        self.baseInventoryLink=inventoryLink
        self.driver.get(inventoryLink)

    def __getItemLinks(self):
        tabs=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='games_list_tabs']")))
        firstTab=tabs.find_elements_by_xpath("a")[0]
        #playerID=self.driver.current_url.split('/')[-3]
        #baseInvID=firstTab.get_attribute('href')[1:]
        firstTab.click()
        links=[]
        
        #loop grabs all but last page twice, removed dupes as a temporary fix at the end of the function
        while True:
            elem=self.driver.find_element_by_id('active_inventory_page')
            inventoryDivParent=elem.find_element_by_xpath("div[@class='inventory_page_left']/div[@id='inventories']")
            activeLeftDiv=inventoryDivParent.find_element_by_xpath("div[@style!='display: none;']")
            activeDivItems=activeLeftDiv.find_elements_by_xpath("div[@style!='display: none;' and @class='inventory_page']/div[@class='itemHolder']/div")
            time.sleep(.5)
            for div in activeDivItems:
                temp='#'+div.get_attribute('id')
                links.append(temp)
            pageControls=elem.find_element_by_xpath("div[@class='inventory_page_left']/div[@id='inventory_pagecontrols']")
            nextPageButton=pageControls.find_element_by_id('pagebtn_next')
            nextPageButtonEnabled='disabled' not in nextPageButton.get_attribute('class')
            if not nextPageButtonEnabled:
                break
            self.driver.execute_script("InventoryNextPage();")

        for i in range(len(links)):
            links[i]=self.baseInventoryLink+links[i]
        return set(links)

    def createSteamItem(self,link):
        self.driver.get(link)
        elem=self.__wait.until(EC.visibility_of_element_located((By.ID,'active_inventory_page')))
        activeRightDivParent=elem.find_element_by_xpath("div[@class='inventory_page_right']")
        activeRightDiv=activeRightDivParent.find_element_by_xpath("div[not(contains(@style,'display: none;'))]")

instance=SteamWebInstance()
instance.start()
print('hi')
        