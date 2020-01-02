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
import pandas as pd
from bs4 import BeautifulSoup
import re
from getpass import getpass
import collections

Login = collections.namedtuple('Login',['username','password'])


class SteamWebInstance:
    def __init__(self):
        self.__loginUrl='https://store.steampowered.com/login/?redir=&redir_ssl=1'
        self.__nonBreakSpace = u'\xa0'
        opt=Options()
        opt.headless=True
        self.driver=webdriver.Firefox(options=opt)
    def getLoginInfo(self):
        user=input(prompt='Please enter you Steam username: ')
        password=getpass(prompt='Please enter you Steam password: ')
        x =Login(user,password)
        return x