from flask import Flask, render_template, request
import requests
import json
import re
import time

API_KEY="tKaD34wiXMod"
PROJECT_TOKEN="tT_Q5EvFTmTo"
RUN_TOKEN="t6O3ujJFY-AV"

class Data:
	def __init__(self, api_key, project_token):
		self.api_key= api_key
		self.project_token=project_token
		self.params={
					"api_key": self.api_key
					}
		self.data=self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
		data= json.loads(response.text)
		return data

	def get_total_cases(self):
		data= self.data['total']

		for content in data:
			if content['name']== "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self):
		data= self.data['total']

		for content in data:
			if content['name']== "Deaths:":
				return content['value']
		return "0"

	def get_country_data(self, country):
		data = self.data["country"]

		for content in data:
			if content['name'].lower()==country.lower():
				return content
		return "0" 

	def get_list_of_countries(self):
		countries=[]
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries


def main(query):
	data=Data(API_KEY, PROJECT_TOKEN)
	country_list= data.get_list_of_countries()

	TOTAL_PATTERNS = {
					re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
					re.compile("[\w\s]+ total cases"): data.get_total_cases,
					re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
					re.compile("[\w\s]+ total deaths"): data.get_total_deaths
					}

	COUNTRY_PATTERNS = {
						re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
						re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
						}
	text=query
	result= None

	for pattern, func in COUNTRY_PATTERNS.items():
		if pattern.match(text):
			words= set(text.split(" "))
			for country in country_list:
				if country in words:
					result= func(country)
					break

	if result==None:	
		for pattern, func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result= func()
				break
	return result

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
	update=False
	query= "Make your first query now!"
	result= "Nothing to show, make a query."
	if request.method=="POST":
		for name in request.form:
			if name=='nm':
				query= request.form["nm"].lower()
			elif name=="Update":
				update=True
		if update:
			response = requests.post(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/run', params=API_KEY)

		try:
			result=main(query)
		except:
			result="Make a new query"

	return render_template("index.html",result=result, query=query)

if __name__=="__main__":
	app.run(debug=True)

