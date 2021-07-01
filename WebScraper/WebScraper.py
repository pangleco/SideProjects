# BY : CONNOR PANGLE
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib
from urllib.parse import urlencode, urlparse, parse_qs
from lxml.html import fromstring
from requests import get
from operator import itemgetter

from collections import OrderedDict

OPEN_MSG = "--WELCOME TO THE TEACHER RANKER--\n input a valid MSU course along with the max number of teachers you'd like to rank \n (if theres less teachers than your number it will only show that many)\n The score is calculated by turning the median and RMP into like fractions \n and then adding them to create a score out of 40 \n ENJOY! \n"

# Used for testing soup stuff
def testSoup(soup):
    for teacher in soup.find_all('tr'):

       if teacher.find('a') is not None:
          print(teacher.find('a').text)



# Creates the list of teacher name and their grades : returns dictionary
def getGradeDic(soup):
    ls = []
    count = 0
    while True:
        max = input("HOW MANY TEACHERS SHOWN? (MOST RECENTLY TAUGHT): ")
        try:
            max = int(max)
            break
        except:
            print("INPUT A VALID NUMBER")

    for teacher in soup.find_all('tr'):

        if count == max:
            break

        if teacher.find('a') is not None:

            name = teacher.find('a').text
            grades = []

            # [ median , avg ]

            for grade in teacher.find_all('em'):
                grades.append(float(grade.text))

            grades.append(teacher.find_all('td')[4].text)
            grades.reverse()
            tup = (name,grades)
            ls.append(tup)        

            count+=1


    return ls



# Gets the course to look for : returns the soup
def getSoup():
    print(OPEN_MSG)

    while True:
        course = input("INPUT COURSE (ex.CSE 102): ")
        if course.find(' ') == -1:
            print("WRONG FORMAT - MUST BE A SPACE BETWEEN COURSE AND NUMBER")
            continue
        else:
            break

    course = course.replace(' ','_')
    URL = 'https://msugrades.com/courses/'+course+'/instructors#overview'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup



# Get Rate my Prof link using a driver for fun, just give it a name returns link
# VERY SLOW USE AT RISK : just wanted to play with a webdriver
def getRMPLinkDRIVER(name):

    driver = webdriver.Chrome(executable_path='./chromedriver')
    driver.get("https://www.google.com")

    search = name+" michigan state university rate my professor"

    search_bar = driver.find_element_by_name("q")
    search_bar.clear()
    search_bar.send_keys(search)
    search_bar.send_keys(Keys.RETURN)
    URL = driver.current_url
    print(URL)

    driver.close()

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    for i in soup.find_all('a',href=True):
        link = i['href']
        if link[0:4] == '/url':
            break

    link = link[7:]
    link = link.replace('%3F','?')
    link = link.replace('%3D','=')
    index = link.find('=')
    end = link.find('&',index)
    link = link[0:end]

    return link

def getRMPLink(name):

    name = name.replace(' ','+')
    URL = 'https://google.com/search?q=' + name + "+michigan+state+university+rate+my+professor"

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    for i in soup.find_all('a',href=True):
        link = i['href']
        if link[0:4] == '/url':
            break

    link = link[7:]
    link = link.replace('%3F','?')
    link = link.replace('%3D','=')
    index = link.find('=')
    end = link.find('&',index)
    link = link[0:end]

    return link


# Used to loop through all teachers and attach their RMP scores to them : returns new dic
def getRMPRating(ls):

    for teacher in ls:
        link = getRMPLink(teacher[0])
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        #print(link)

        score = soup.find('div',class_="RatingValue__Numerator-qw8sqy-2 liyUjw")
        
      
        ls = soup.find_all('div',class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs")
        if score != None:
            takeAgain = ls[0].text
            if takeAgain != ('N/A'):
                takeAgain = float(takeAgain.replace('%',''))/100
            difficulty = float(ls[1].text)
            score = float(score.text)
        else:
            takeAgain = None
            difficulty = None

        # [term taught , median(4/4) , avg(4/4) , score(5/5) , would they take again (100%) , difficulty(5/5) ]
        teacher[1].append(score)
        teacher[1].append(takeAgain)
        teacher[1].append(difficulty)
    
    return dic
        
def rankTeachers(dic):

    ranking = []
    for teacher in dic:
        nums = teacher[1]
        if nums[3] != None:
            score = (nums[1]*5 + nums[3]*4)

        else:
            score = 0
        
        ls = [score,teacher[0],teacher[1]]
        ranking.append(ls)

    ranking = sorted(ranking, key=itemgetter(0), reverse=True)

    rank = 1
    # [term taught , median(4/4) , avg(4/4) , score(5/5) , would they take again (100%) , difficulty(5/5) ]
    for teacher in ranking:
        print()
        if teacher[2][3] == None:
            teacher[2][2] = 'N/A'
            print("{}. {} - SCORE: {} MEDIAN: {}/4 RMP RATING: {} TERM: {}  **NO RMP RATING**".format(rank,teacher[1],teacher[0],teacher[2][1],teacher[2][3],teacher[2][0]))
        else:
            print("{}. {} - SCORE: {} MEDIAN: {}/4 RMP RATING: {}/5 TERM: {}".format(rank,teacher[1],teacher[0],teacher[2][1],teacher[2][3],teacher[2][0]))
        print()
        rank+=1



dic = getGradeDic(getSoup())
dic = getRMPRating(dic)
rankTeachers(dic)



