from datetime import datetime
import requests, time, threading, joblib
from sqlalchemy.sql.sqltypes import DateTime, VARCHAR
import helper, database_management

## Get Real-Time Tweets from Twitter

def connect_to_twitter(next_token=None):
	tweet_fields = helper.config["fields"]
	if next_token is not None:
	    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}".format(helper.config["query"] + "", tweet_fields, next_token)
	else:
	    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(helper.config["query"] + "", tweet_fields)
	headers = {"Authorization": "Bearer {}".format(helper.config["bearer"])}
	response = requests.request("GET", url, headers=headers)
	if response.status_code != 200:
	    # raise Exception(response.status_code, response.text)
	    return response.json(), False
	return response.json(), True


def search_twitter():
	# Load Suicide Detection Model
	try:
		prediction_model = joblib.load(helper.config["prediction_model"])
		helper.log("info","background","Prediction model loaded")
	except:
		helper.log("critical","background","Prediction model can't be loaded")
	response, query_successful = connect_to_twitter()
	tweets = []
	next_token = ""
	max_limit = 1
	predict(tweets, prediction_model)
	while query_successful and 'next_token' in response["meta"]:
		tweets = []
		helper.log("debug","background","Pulling next token")
		for field in response["data"]:
			tweets.append(field)
		predict(tweets, prediction_model)
		max_limit +=1
		if max_limit > helper.config["max_page_token_limit"]:
			break
		next_token = "next_token=" + response["meta"]["next_token"]
		response, query_successful = connect_to_twitter(next_token=next_token)
		time.sleep(helper.config["tweet_wait"])
	return True

def predict(tweets, prediction_model):
	for tweet in tweets:
		# Predict Suicidal Tweet
		prediction = prediction_model.predict([tweet["text"]])
		helper.log("info","background","Ideation predicted")
		if prediction[0] == "1":
			helper.log("critical","background","Suicidal tweet found")
			predicted_tweet = {
				"user_id" : str(tweet["author_id"]),
				"tweet_id" : str(tweet["id"]),
				"tweet_text" : str(tweet["text"]),
				"ideation" : "Potentially Suicidal",
				"status" : "Active"
			}
			db_write_success = database_management.write_tweet_to_db(predicted_tweet)
	return True

class prediction(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
	
	def run(self):
		while True:
			search_twitter()
			time.sleep(helper.config["prediction_control"])
