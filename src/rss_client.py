
import feedparser
import os 
import re
import logging
import csv
from datetime import datetime, date
#from langchain_core.documents import Documents  


logging.basicConfig(level=logging.INFO)

#helper function to print and write to a file 
def print_and_write(f, msg):
    print(msg)
    f.write(msg + "\n")

import ssl
# Bypass SSL verification for all HTTPS calls in this script
#MUST SWAP TO PERMANENT FIX 
ssl._create_default_https_context = ssl._create_unverified_context

RSS_FEED_URL = "https://www.aeroroutes.com/eng?format=rss"

def fetch_rss_feed(url):
    try:
        feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        logging.info(f"Fetched entries from RSS feed.")
        return feed.entries     #return entries instead of an object, entries= multiple dict inside a list
    except Exception as e:
        logging.error(f"Error fetching RSS feed: {e}")
        return []
    
def clean_html(raw_html):
    """Remove HTML tags and extra whitespace from the description."""   
    if not raw_html:
        return "N/A"
    # Remove all HTML tags
    clean = re.sub(r'<[^>]+>', '', raw_html)
    # Replace newlines and multiple spaces
    clean = ' '.join(clean.split())  
    return clean


def save_rss_feed(entries):

    print("="*20)
    print("ALL RSS FEEDS")
    print("="*20)

    with open("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_feed.txt", "w") as f:
        for idx, entry in enumerate(entries, 1):
            
            print_and_write(f, f"\n[{idx}] TITLE: {entry.get('title', 'N/A')}")
            print_and_write(f, f"\n    LINK: {entry.get('link', 'N/A')}")
            print_and_write(f, f"\n    DATE FETCHED: {datetime.now()}")
            print_and_write(f, f"\n    DESCRIPTION: {clean_html(entry.get('description', ''))}") 
            '''
            f.write(f"\n[{idx}] TITLE: {entry.get('title', 'N/A')}")
            f.write(f"\n    LINK: {entry.get('link', 'N/A')}")
            f.write(f"\n    PUBLISHED: {entry.get('pubDate', 'N/A')}")
            f.write(f"\n    DESCRIPTION: {clean_html(entry.get('description', ''))}") 
            f.write("\n" + ("-" * 80) + "\n")
            '''

def save_rss_links(entries):
    with open("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_links.txt", "w") as f:
        for entry in entries:
            check = entry.get('link', 'N/A')
            f.write(f"{check}\n")
            break  #Only save the first link as the newest

def load_prev_link ():
    link = None
    if os.path.exists("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_links.txt"):
        with open("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_links.txt", "r") as f:
            link = f.readline().strip()
            #this also works print(link)
    return link


def save_newest_feeds(entries):
    prev_link =load_prev_link()
    #this works print(prev_link)

    if not prev_link:   
        logging.info("No previous link found. First fetch.")
        return 

    #start here

    print("="*20)
    print("NEWEST RSS FEEDS")
    print("="*20)

    with open("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_new.txt", "w") as f:
        for idx, entry in enumerate(entries, 1):
            if entry.get('link', 'N/A') != prev_link:

                
                print_and_write(f, f"\n[{idx}] TITLE: {entry.get('title', 'N/A')}")
                print_and_write(f, f"\n    LINK: {entry.get('link', 'N/A')}")
                print_and_write(f, f"\n    DATE FETCHED: {datetime.now()}")
                print_and_write(f, f"\n    DESCRIPTION: {clean_html(entry.get('description', 'N/A'))}")
                '''
                f.write(f"\n[{idx}] TITLE: {entry.get('title', 'N/A')}")
                f.write(f"\n    LINK: {entry.get('link', 'N/A')}")
                f.write(f"\n    DATE FETCHED: {entry.get('pubDate', 'N/A')}")
                f.write(f"\n    DESCRIPTION: {clean_html(entry.get('description', 'N/A'))}")
                f.write("\n" + ("-" * 80) + "\n")
                '''
            else:
                break  #stop write once it is the same link: indicates previous newest
    save_rss_links(entries)     #will update the latest link

def append_rss_feed(entries):
    prev_link=load_prev_link()

    if not prev_link:   
        logging.info("No previous link found. First fetch.")
        return 

    #start here
    with open("/Users/fionaleong/aeroroutes_flight_monitor/data/rss_new.txt", "a") as f:
        for idx, entry in enumerate(entries, 1):
            if entry.get('link', 'N/A') != prev_link:
                
                f.write(f"\n[{idx}] TITLE: {entry.get('title', 'N/A')}")
                f.write(f"\n    LINK: {entry.get('link', 'N/A')}")
                f.write(f"\n    DATE FETCHED: {datetime.now()}")
                f.write(f"\n    DESCRIPTION: {clean_html(entry.get('description', 'N/A'))}")
                f.write("\n" + ("-" * 80) + "\n")
                
            else:
                break  #stop write once it is the same link: indicates previous newest


if __name__== "__main__":           #this is the main file 
    entries= fetch_rss_feed(RSS_FEED_URL)
    #sequence of execution: save newest feeds (bcs would load new link)-> save all feeds
    append_rss_feed(entries)    #append the new to existing database
    save_newest_feeds(entries)  #only newest entries + will load new link
    save_rss_feed(entries)      #all entries on the current run
    


