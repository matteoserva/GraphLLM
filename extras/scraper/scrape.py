#!/usr/bin/python3

# come ho generato firefox:
## creato un profilo dedicato
## installato ublock origin e tutti i filtri
## ???
## profit


from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.firefox.webdriver import Service

from selenium import webdriver

import inspect
import os
import sys
from os.path import expanduser, exists

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.insert(0,currentdir)
os.environ["PATH"] +=":"+currentdir

# try:
#     from . import scraper_utils
# except:
    #import scraper_utils
import scraper_utils


#url="https://en.m.wikipedia.org/wiki/Piston"
#url="https://www.ilpost.it/2024/04/26/prezzi-variabili-opachi/"
#url="https://admiralcloudberg.medium.com/fire-in-the-fog-the-crash-of-swissair-flight-306-c54893961151"
#url="https://arstechnica.com/science/2024/04/metafluid-gives-robotic-gripper-a-soft-touch/"
url="https://www.reddit.com/r/italy/?feedViewType=compactView"

url="https://news.ycombinator.com/"

if len(sys.argv) > 1:
  url = sys.argv[1]

debug_mode = False

if(len(sys.argv) > 1):
    url = sys.argv[1]

print("loading additional scripts", file=sys.stderr)

f = open(currentdir +"/removeHiddenNodes.js","r")
script_removeHiddenNodes = f.read()
f.close()

f = open(currentdir +"/Readability.js","r")
scr = f.read()
f.close()

f = open(currentdir +"/fetchWrapper.js","r")
fetch_wrapper = f.read()
f.close()

# this is  executed just before appying readability.js
f = open(currentdir +"/redditFixer.js","r")
reddit_fixer = f.read()
f.close()

f = open(currentdir +"/Readability-readerable.js","r")
readerable = f.read()
f.close()

driver = None

def load_page(url):
  global driver
  service = Service()

  print("Started processing url: " + url, file=sys.stderr)

  options = webdriver.FirefoxOptions()
  #options.add_argument('--safe-mode')
  if not debug_mode:
    options.add_argument('--headless')

  home_dir = expanduser("~")
  profile_path = home_dir + "/.mozilla/firefox/profile.bot"
  print("Loading the firefox profile", profile_path, file=sys.stderr)
  if not exists(profile_path):
      print("WARNING: profile not found. check the documentation.", profile_path, file=sys.stderr)
  
  try:
      profile=webdriver.FirefoxProfile(profile_path)
  except:
      print("profile.bot not found. Using default with degraded performance", file=sys.stderr)

      profile=webdriver.FirefoxProfile()

  options.profile = profile

  print("launching firefox via geckodriver", file=sys.stderr)

  if not driver:
    try:
        driver = webdriver.Firefox(options=options, service=service)
    except:
        service.path = currentdir + "/geckodriver"
        if not exists(service.path):
          print("WARNING: geckodriver not found. download it and put it here.", service.path, file=sys.stderr)
        
        driver = webdriver.Firefox(options=options, service=service)


  start_url = "about:reader?url=" + url # not used anymore
  print("loading webpage", url,file=sys.stderr)

  driver.get(url)

  print("waiting for readyState complete", file=sys.stderr)

  # aspetto che il documento sia caricato
  while driver.execute_script("return document.readyState") != "complete":
      time.sleep(.1)

  driver.execute_script(fetch_wrapper)
  print("waiting for jquery scripts to terminate", file=sys.stderr)

  #aspetto che jabascript finisca
  while driver.execute_script("return (window.jQuery != null) && (jQuery.active > 0);") :
      time.sleep(.1)
  #sposto in basso per attivare il caricamento di pagine extra
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
  #mezzo secondo di attesa per far partire eventuali ajax

  print("waiting for dynamic components", file=sys.stderr)
  for i in range(20):
    #print(driver.execute_script("return document.readyState") != "complete", file=sys.stderr)
    time.sleep(.1)
  time.sleep(.5)
  #aspetto eventuali ajax
  while driver.execute_script("return (window.jQuery != null) && (jQuery.active > 0);") :
      time.sleep(.1)
  for i in range(20):
    r = driver.execute_script("return window.running_fetches")
    if(r == 0):
      break
    #print(r, file=sys.stderr)
    time.sleep(.1)
    

  # cancello i nodi nascosti da ublock

  print("deleting nodes identified by ublock origin.", file=sys.stderr)
  driver.execute_script(script_removeHiddenNodes)


  # trying to avoid special cases
  driver.execute_script(reddit_fixer)

  print("readability.js", file=sys.stderr)

  ## readability per estrarre il contenuto
  pagina_rjs = driver.execute_script(scr + "\n" + "return new Readability(document.cloneNode(true)).parse();")
  scraper_utils.write_file("/tmp/pagina1.html",str(pagina_rjs["content"]))

  ## check
  should_keep = driver.execute_script(readerable + "\n" + "return isProbablyReaderable(document);")
  print("reader mode available?", should_keep)

  html_content = driver.page_source

  #if not should_keep:
  #    pagina_rjs["content"] = html_content

  scraper_utils.write_file("/tmp/pagina0.html",html_content)
  if not debug_mode:
    print("closing firefox", file=sys.stderr)
    driver.quit()
  return pagina_rjs

def apply_static_readability(content):
  ## ora riparso e rimuovo i link
  from readabilipy import simple_json_from_html_string
  print("static readability", file=sys.stderr)

  article = simple_json_from_html_string(content,use_readability=False)
  article["plain_text"]

  scraper_utils.write_file("/tmp/pagina2.html",article["plain_content"])
  return article


## carico i dati in bs per eventuali riprocessamenti
def clean_soup(content):
  print("clean soup", file=sys.stderr)
  #soup = BeautifulSoup(article["plain_content"], 'lxml')
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(content, 'lxml')
  for s in soup.select('figure'):
      s.extract()
  for el in  soup.select('a[role="button"]'): #wikipedia [edit] links
      el.extract()
      
  for el in soup.select("shreddit-post>p[slot=title]"):
      el.extract()
  return soup
  
##converto in md
def convert_to_md(title, data):
  print("convert to md", file=sys.stderr)
  import html2text
  converter = html2text.HTML2Text()
  converter.ignore_links=False
  converter.ignore_images=True
  markdown_content = "# " + title + "\n\n" + converter.handle(data).strip()
  scraper_utils.write_file("/tmp/pagina.md",markdown_content)
  return markdown_content
  
def scrape(url):
  pagina_rjs = load_page(url)
  article = apply_static_readability(pagina_rjs["content"])
  soup = clean_soup(pagina_rjs["content"])
  markdown_content = convert_to_md(pagina_rjs["title"], str(soup))
  return markdown_content

if __name__ == "__main__":
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'd')
    for (k, v) in opts:
       if k == "-d": debug_mode = True
    markdown_content = scrape(args[0])
    print(markdown_content)
