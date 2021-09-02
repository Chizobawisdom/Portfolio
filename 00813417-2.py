#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 15:41:43 2021

@author: Chizoba Wisdom Favour

@description: This is a program to fetch data from a webpage and display it.

"""
# Declaration
from selenium import webdriver  # imports the  for selected browser
from selenium.webdriver.common.keys import Keys  # for entering keys from the code

driver = webdriver.Chrome(
    executable_path = "/Users/Mark/Desktop/browser drivers/chromedriver")

# Input
driver.get('https://www.google.com')  # Website to web scrape

# Processing


elemSearch = driver.find_element_by_name('q')
elemSearch.clear()
elemSearch.send_keys("cheese")  # web scrapinng topic
elemSearch.send_keys(Keys.RETURN)  # returns the value of the keys into the search bar

results = []  # empty list where selected website url is saved
elems = driver.find_elements_by_xpath(
    '//*[@id="rso"]/div[12]/div/div/div/div[1]/a')  # selected website according to my matriculation number
for result in elems:
    results.append(result.get_attribute("href"))  # appends website url to empty list results
    result.click()  # clicks website url

elems2 = driver.find_element_by_xpath(
    '//*[@id="tve_editor"]/div/p[1]')

el = driver.find_element_by_tag_name('body')
path = '/Users/Mark/Desktop/web scraping/scrape.png'  # file path to save screenshot
el.screenshot(path)  # screenshots current webpage

# Output
print(results)
print()
print(elems2.text)
