from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class': 'lister-list'})
titles = table.find_all('h3', attrs={'class':'lister-item-header'})
rating_bar = table.find_all('div', attrs={'class':'ratings-bar'})
votes = table.find_all('p', attrs={'class':'sort-num_votes-visible'})

row_length = len(votes)

temp = [] #initiating a list 

for i in range(0, row_length):

    title = titles[i].find('a').text
    
    rating = rating_bar[i].find('strong').text.strip()
    
    metascore_sec = rating_bar[i].find('span', attrs={'class':'metascore favorable'})
    if metascore_sec is not None:
        metascore = metascore_sec.text.strip()
    else:
        metascore = metascore_sec
        
    vote = votes[i].find('span', attrs={'name': 'nv'}).text.strip()

    temp.append((title, rating, metascore, vote))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=('title', 'rating', 'metascore', 'votes'))

#insert data wrangling here
df.metascore.fillna(0, inplace=True)
df.votes = df.votes.str.replace(',', '')
df = df.astype({'rating':'float', 'metascore': 'int', 'votes': 'int'})
#end of data wranggling 

@app.route("/")
def index(): 
	top_7_popularity = df.sort_values(by='votes', ascending=False).head(7).copy()
	card_data = f'{round(df["votes"].mean(),2)}' #be careful with the " and ' 

	# generate plot
	ax = top_7_popularity[['title', 'votes']].set_index('title').sort_values('votes').plot(kind='barh', figsize = (16,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# generate plot
	ay = top_7_popularity[['title', 'rating']].set_index('title').sort_values('rating').plot(kind='barh', figsize = (16,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)