'''
Functions for extracting data from Billboard Hot 100 list

Created by Alec Plante
'''




import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

## FUNCTIONS

def firstrowstats(row):
    '''
    returns stats of the first row on a given page (because HTML tags differ from all other rows)
    
    Arguments:
    row -- the soup data for the first row on a given page
    '''
    
    # get the rank value [1-100] (#1 spot may be blank, so need to check what the number is)
    rank = row.find("span", {'class': "c-label a-font-primary-bold-l u-font-size-32@tablet u-letter-spacing-0080@tablet"}).contents[0].strip()
    # get the title of the song for the first row
    title = row.find("h3", {'id': "title-of-a-story"}).contents[0].strip()
    # get the artist name for the first row
    artist = row.find("span", {'class': "c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet"}).contents[0].strip()
    # get the last week rank, peak postition, and the # of weeks the song has been on the charts
    lastweek, peak, weekcount = [i.contents[0].strip() for i in row.find_all('span', {'class':'c-label a-font-primary-bold-l a-font-primary-m@mobile-max u-font-weight-normal@mobile-max lrv-u-padding-tb-050@mobile-max u-font-size-32@tablet'})[:3]]
    return [rank, title, artist, lastweek, peak, weekcount]
    
def rowstats(row):
    '''
    returns stats of the given row (will never be row 0)
    
    Arguments:
    row -- the soup data for the given row
    '''
    # get the rank value of the entry [1-100]
    rank = row.find("span", {'class': "c-label a-font-primary-bold-l u-font-size-32@tablet u-letter-spacing-0080@tablet"}).contents[0].strip()
    # get the title of the song for the given row
    title = row.find("h3", {'id': "title-of-a-story"}).contents[0].strip()
    # get the artist name for the given row
    artist = row.find("span", {'class': "c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"}).contents[0].strip()
    # get the last week rank, peak postition, and the # of weeks the song has been on the charts
    lastweek, peak, weekcount = [i.contents[0].strip() for i in row.find_all('span', {'class':'c-label a-font-primary-m lrv-u-padding-tb-050@mobile-max'})[:3]]
    return [rank, title, artist, lastweek, peak, weekcount]
    
def pagestats(df, data, date):
    '''
    adds the stats of a given page to the dataframe
    
    Arguments:
    df -- dataframe that we use to store the extracted results
    data -- soup/requests data from a given page
    date -- date of the page (YYYY-MM-DD)
    '''
    
    # Gets list of soup for all rows of data, with each row as a list entry
    rows = data.find_all("div", {"class":"o-chart-results-list-row-container"} )
    # adds new row to the datafram for the first song on this page
    df.loc[len(df.index)] = [date]+firstrowstats(rows[0])
    
    # for every other entry in the Billboard top 100 for this date, add a row 
    for i in range(1,len(rows)):
        df.loc[len(df.index)] = [date]+rowstats(rows[i])
        
def getdata(df, weeklist):
    '''
    Loops through every date in the list and grabs billboard data soup 
    from that week and puts it in the dataframe
    
    Arguments
    df -- dataframe to store the data in
    weeklist -- list of weeks from the desired start and end time    
    '''
    
    for week in weeklist:
        date=week.strftime('%Y-%m-%d')
        print(f"INIT: request page {date}")
        with requests.get(f'https://www.billboard.com/charts/hot-100/{date}', stream=True) as r:
            data = BeautifulSoup(r.content, parser="lxml")
        pagestats(df, data, week)

def updatedata(df):
    '''
    Updates the data in the dataframe with all new info.
    If empty, it gets all of the data
    
    Arguments:
    df -- DataFrame used to store the data
    '''
    
    # if empty get all billboard data
    if len(df['Date']) == 0:
        gatheralldata(df)
    # else, add only new data to the dataframe
    else:
        maxdate= max(df['Date'].value_counts().keys())
        datelist = pd.date_range(end = datetime.today(), start = maxdate + timedelta(days=7), freq='W-SAT')
        print(f"INIT: getdata from {maxdate}")
        getdata(df, datelist)
        print(f"END: getdata from {maxdate}")
    
def gatheralldata(df):
    '''
    Gets all data from the begining of the Billboard dataset
        from 1958-08-02 to last saturday
        
    Arguments:
    df -- DataFrame used to store the data
    '''
    
    earliestDate="1958-08-02"
    dates = pd.date_range(end = datetime.today(), start = datetime.strptime(earliestDate, '%Y-%m-%d'), freq='W-SAT')
    getdata(df, dates)
    
def createtable():
    '''
    Creates a new df with the columns in the dataset
    '''
    
    col = ["Date", "Rank", "Title", "Artist", "LastWeek", "Peak", "WeeksOnChart"]
    return pd.DataFrame(columns= col)
