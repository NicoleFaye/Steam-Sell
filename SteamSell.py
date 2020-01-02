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
        self.__wait=WebDriverWait(self.driver,15)
        self.__smallWait=WebDriverWait(self.driver,1)
        self.__login()
    
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
    def navigateToInventory(self):
        elem=self.__wait.until(EC.visibility_of_element_located((By.XPATH,"//a[@class='menuitem supernav username']")))
        profileLink=elem.get_attribute('href')
        inventoryLink='/'.join(profileLink.split('/')[:-2])+'/inventory/'
        self.driver.get(inventoryLink)
    def getItemLinks(self):
        elem=self.driver.find_element_by_id('active_inventory_page')


instance=SteamWebInstance()
instance.start()
instance.navigateToInventory()
print('hi')
        