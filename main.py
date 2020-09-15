import tweepy
import requests
import time
import os
from itertools import cycle
import pickle
from datetime import datetime

# Telegram
# api_id = '1067817'
# api_hash = 'b8f1a4a4d2eed57590b197ef1b5b0e85'

#Twitter
# Bearer token : 'AAAAAAAAAAAAAAAAAAAAAOCmHgEAAAAA%2BT75vMsvT5uBpaPLV5ZfpLEcpsA%3Dh4Qh1FZ3S9QP2DVPl7MUoDNSn2Nn9ODQ54vqvzUcL3MTqzwjTT'


class Twitter_Bot():

    def __init__(self):
        self.telegram_chat_id = ""
        self.telegram_token = ""
        self.twitter_consumer_key = ""
        self.twitter_consumer_key_secret = ""
        self.twitter_access_token = ""
        self.twitter_access_token_secret = ""
        self.previous_friends = []
        self.current_friends = []
        self.users_dict = {}
        self.user_pool = {}
        self.data_file = os.path.join(os.getcwd(),'data.pkl')

    def send_message(self,text):
        url = "https://api.telegram.org/bot"+self.telegram_token+"/sendMessage?chat_id="+self.telegram_chat_id+"&text="+text
        response = requests.get(url)

    def setup(self):

        #TELEGRAM KEYS

        #This is the bot's unique token, if you make another bot, make sure you change this with your bot's
        self.telegram_token = '1073518944:AAEkMGKpyFKR3ROm99Fr22S5XL2wwICkSpM'
        #This is your chat's ID
        self.telegram_chat_id  = '952665789'
        

        #Twitter's APP Keys, shouldnt really touch these
        self.twitter_consumer_key = 'AdUe16M1yvrckJ3ypQntdpJBo'
        self.twitter_consumer_key_secret = 'QBRkoFsuMktQoivdJMuAAJPicPQGCrYhAHxlBHdu447zjqpgnE'
        self.twitter_access_token = '557618485-lf7QU3s3Wjly55Zb8Lo2LP7E7D8ugUfcg7BrjBxh'
        self.twitter_access_token_secret = 'BuOKLAFb4rMJq8ECwMqp8oImLKkvwcRs8ZPmMnQ4cgghh'

        self.read_users()
        self.user_pool = cycle(list(self.users_dict.keys()))

    #Reads the users you want to observe into self.users_dict
    def read_users(self):
        with open(os.path.join(os.getcwd(),"users.txt"),"r") as cfg:
            users = cfg.readlines()
            users = [i.strip().strip("\n") for i in users]
            for us in users:
                self.users_dict[us] = ""
        
        
        #Reads the data saved from previous run(if there was any)
        if os.path.exists(self.data_file):
            self.users_dict = self.load_data(self.data_file)
            print(self.users_dict)
            print("\n")
        else:
            self.write_data(self.data_file,self.users_dict)

    def write_data(self,data_file,data):
        file = open(self.data_file,'wb')
        pickle.dump(data,file)
        # print("Data file REWRITTEN....")
        
    def load_data(self,data_file):
        file = open(self.data_file,'rb')
        return pickle.load(file)
        # print("Data file exists, READING....")

    def run(self):

        auth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_key_secret)
        # Setting your access token and secret
        auth.set_access_token(self.twitter_access_token, self.twitter_access_token_secret)
        redirect_url = auth.get_authorization_url()

        api = tweepy.API(auth, wait_on_rate_limit=True)
        first_time = True
        
        print(self.users_dict)

        while True:
            print(datetime.now())

            #Cycling through the users
            curr_user = next(self.user_pool)
            user = api.get_user(curr_user)
            current_user_screen_name = user.screen_name.lower()

            #List of the current user's friends
            friends = user.friends()
            #Latest friend of the user
            latest_friend = friends[0].screen_name

            #Setting up the dict(first iteration)
            if self.users_dict[current_user_screen_name] == "":
                self.users_dict[current_user_screen_name] = latest_friend
                print(current_user_screen_name + " was empty, so its filled with " + latest_friend)

            #The dict is set-up, comparing results
            else:
                #User has a new friend(s)
                if self.users_dict[current_user_screen_name] != latest_friend:
                    previous_friend = self.users_dict[current_user_screen_name]
                    friend_names = [fr.screen_name for fr in friends]
                    
                    #Handling the more friends inbetween iterations problem
                    if previous_friend in friend_names:     #Handles the case where the user unfollowed its current latest friend

                        prev_friend_index = friend_names.index(previous_friend)
                        new_followers = friend_names[:prev_friend_index]
                        #Sends message for each new friend
                        for n_f in new_followers:
                            message = "twitter.com/"+ current_user_screen_name + " started following " + "twitter.com/"+n_f
                            print(message)
                            self.send_message(message)
                            print("Message sent")
                        print(new_followers)
                    
                    #Updating the dict
                    self.users_dict[current_user_screen_name] = latest_friend
            #Updating the dict on file
            self.write_data(self.data_file,self.users_dict)
            temp = self.load_data(self.data_file)

            #Pause
            print("-----SLEEPING 15 SECONDS------")
            time.sleep(15)
        

if __name__ == '__main__':
    bot = Twitter_Bot()
    bot.setup()
    try:
        bot.run()
    except Exception as e:
        bot.send_message("The bot pretty much FAILED ! :)")
        bot.send_message(e)
