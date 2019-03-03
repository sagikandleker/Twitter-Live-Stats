from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tkinter import Button,Entry,Label, Tk
from time import sleep
from collections import Counter

import Twitter_Permissions
import threading
import re
import time

"""
    Twitter Live Stats Application by Sagi Saada.
    
    Description
    -----------
    This application receive some keywords as a parameter (for example 'Donald Trump').
    Show a live visual bar chart of 10 most popular hashtags which are linked to the keywords.
    
    Libraries
    --------
    Using tweepy library for accessing the Twitter API and tkinter library for Graphical User Interface.
    
    Threads
    -------
    Two threads, one of them to analyze the data from Twitter and the second to update the dynamic "top hashtags" in GUI.
"""

allHashtags = []
topHashtags = []

def restart_data():
    allHashtags.clear()
    topHashtags.clear()

def find_between(myData, start, end):
    """
    This function finds the "hashtags" description from the line in myData.

    Parameters
    ----------
    myData : str
        for Example:
            {"created_at":"Mon Feb 25 14:01:44 +0000 2019","id":1100033106084532224,..........}
    start : str
        hashtags
    end : str
        urls

    Returns
    -------
    str
        for Example:
            ":[{"text":"MAGA","indices":[103,108]},{"text":"KAG","indices":[109,113]}],"

    """
    return (myData.split(start))[1].split(end)[0]

def extraction_hashtags(cut_hashtags_string):
    """
    This function clean the "dirty" string.

    Parameters
    ----------
    cut_hashtags_string : str
        for Example:
            ":[{"text":"MAGA","indices":[103,108]},{"text":"KAG","indices":[109,113]}],"
   
    Calculation
    -------
    Get all the hashtags in the line.
        for Example:
            ['MAGA','KAG']
    
    Finally, put the valid hashtags in "allHashtags".
    """
    ans = re.findall(r'text":"(.*?)"', cut_hashtags_string)
    for hashtag in ans:
        if not("\\" in hashtag):
            allHashtags.append(hashtag)

# TWITTER AUTHENTICATER #
class Twitter_Authenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(Twitter_Permissions.CONSUMER_KEY, Twitter_Permissions.CONSUMER_SECRET)
        auth.set_access_token(Twitter_Permissions.ACCESS_TOKEN, Twitter_Permissions.ACCESS_TOKEN_SECRET)
        return auth

# TWITTER STREAMER #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = Twitter_Authenticator()

    def stream_tweets(self, key_words_list):
        # This handles Twitter authentication and the connection to Twitter Streaming API.
        listener = StdOutListener()
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=key_words_list, is_async = True)


def isRunning():
    return runningFlag

#  TWITTER STREAM LISTENER #
class StdOutListener(StreamListener):
    """
    This is a listener that prints received tweets to "StdOut"
    """
    def on_data(self, data):
        
        substring = 'hashtags":[{"'
        start = "hashtags"
        end = "urls"

        try:
            if(isRunning()):
                if(substring in data):
                    dirtyHashtagsString = find_between(data,start,end)
                    extraction_hashtags(dirtyHashtagsString)
                    top_hashtags_numbered = Counter(allHashtags).most_common(10)

                    temp = []
                    for hashtag in top_hashtags_numbered:
                        temp.append(hashtag[0])
 
                    if(not(topHashtags.__eq__(temp))):
                        topHashtags.clear()
                        topHashtags.extend(temp)
                        
                return True
            else:
                print("The stream stopped!")
                return False
        except BaseException as e:
            print("Error on_data %s" % str(e))
            
        return True
          
    def on_error(self, status):
        if status == 420:
            global runningFlag
            runningFlag = False
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)

keywords = []
runningFlag = False

#  PROGRAM INTERFACE #
def Interface():
    '''
    This is the interface for a client.
    This interface contains various buttons and text boxes.
    One of the text boxes is dynamic and contains the 10 most common hashtags.
    '''
    
    frame = Tk()
    frame.geometry("285x550")
    frame.title("Twitter Live Stats")

    Label(frame, text='Welcome to "Twitter Live Stats" Application', font= "Arial 11 underline").grid(row=1, column=1)
    Label(frame, text='Top 10 Hashtags', font= "Arial 10 underline").grid(row=2, column=1)
    Label(frame, text='Keywords', font= "Arial 10 underline").grid(row=15, column=1)
    Label(frame, text='Status', font= "Arial 10 underline").grid(row=23, column=1)
   

    # This function adds the keyword into the "keywords" Set.
    def add_Button():
        enteredText = textentry.get()
        if(check_Status()):
            print("Cannot add keyword on running.")
        elif check_Input(enteredText):
            if(not(enteredText in keywords)):
                keywords.append(enteredText)
                print("Added new keyword to keywords list.")
                show_KeyWords()
            else:
                print("This keyword exist!")
        else:
            print("Invalid keyword!")
    
    # This function clear "keywords" Set and stop the "Stream" thread.
    def clear_Button():
        keywords.clear()
        show_KeyWords()
        stop_Button()
        print("Keywords list cleaned.")
    
    # This function exit from program and close all threads.
    def exit_Button():
        stop_Button()
        print("Exit")
        frame.destroy()
        exit()
    
    # This function show for the client "keywords" Set.
    def show_KeyWords():
        
        if(not keywords):
            displayKeywords["text"] = ""
        else:
            displayKeywords['text'] = ""
            for key in keywords:
                displayKeywords["text"] += key + "\n"


        print("Keywords display label updated.")
    
    # This function check if the keyword from the client is valid.
    def check_Input(enteredText):
        invalidsymbols=("`","~","!", "@","#","$",'"')
        if enteredText.isdigit() or enteredText.isspace():
            return False
        elif(enteredText is ""):
            return False
        for symbol in invalidsymbols:
            if symbol in enteredText:
                return False
        return True
    
    # This function runs the "hashtagThread" and TwitterStreamer to getting and analyze data.
    def start_Button():
        
        if keywords:
            
            if(not(check_Status())):

                restart_data()
                
                global runningFlag
                runningFlag = True
                
                twitter_streamer = TwitterStreamer()

                twitter_streamer.stream_tweets(keywords)
                

                hashtagsThread = threading.Thread(target=top_Hashtags, daemon=True)
                hashtagsThread.start()
                
                display_Status("start")

            else:
                ("The program is running!")
            
        else:
            print("Keywords is clear! Please add a keyword")
    
    # This function changes the "runningFlag" to stop the Stream thread.
    def stop_Button():
        global runningFlag
        runningFlag = False
        display_Status("stop")

    #This function restarts the program for reuse.
    def restart_Button():
        stop_Button()
        time.sleep(2)
        restart_data()
        displayHashtags['text'] = ""
        global runningFlag
        runningFlag = True
        start_Button()
    
    def top_Hashtags():
        '''
        This function for "hashtagThread".
        The thread compares between the "Old 10 most popular hashtags" to "New 10 most popular hashtags,
        And when they different he change the display.
        '''
        temp = []
        sleep(3)
        while(True):
            try:
                if(runningFlag):
                    if(topHashtags != temp):
                        temp.clear()
                        
                        for hashtag in topHashtags:
                            temp.append(hashtag)
                        
                        displayHashtags['text'] = ""
                        for i in topHashtags:
                            displayHashtags['text'] += i + "\n"                       
                    time.sleep(5)
                else:
                    display_Status("stop")
                    print("hashtagsThread stopped!")
                    break
                    
            except Exception as e:
                print(e)
    
    # This function displays the program status.
    def display_Status(who):
        if(who == "start"):
            displayStatus['text'] = "Running"
            print("Start")
        elif(who == "stop"):
            displayStatus['text'] = "Stopped"
            print("Stop")
    
    def check_Status():
        if(displayStatus['text'] == "Running"):
            return True
        else:
            return False
    
    # The display text boxes.
    displayKeywords = Label(frame, text="", font= "Arial 9")
    displayKeywords.grid(row=17, column=1)
    
    displayHashtags = Label(frame, width=30, font= "Arial 9")
    displayHashtags.grid(row=3, column=1)
    
    displayStatus = Label(frame, text='Waiting', font= "Arial 9")
    displayStatus.grid(row=24, column=1)
        
    textentry = Entry(frame, width=30, bg="white", font= "Arial 9")
    textentry.grid(row=18, column=1)
    
    # The Buttons.
    Button(frame, text="Start", width=15, command=start_Button, font= "Arial 9").grid(row=13, column=1)
    Button(frame, text="Stop", width=15, command=stop_Button, font= "Arial 9").grid(row=14, column=1)
    Button(frame, text="Add", width=15, command=add_Button, font= "Arial 9").grid(row=19, column=1)
    Button(frame, text="Clear", width=15, command=clear_Button, font= "Arial 9").grid(row=20, column=1)
    Button(frame, text="Restart", width=15, command=restart_Button, font= "Arial 9").grid(row=21, column=1)
    Button(frame, text="Exit", width=15, command=exit_Button, font= "Arial 9").grid(row=22, column=1)
    
    frame.mainloop()
    
if __name__ == '__main__':

    Interface()