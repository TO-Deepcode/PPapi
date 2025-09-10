from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_BASE = "https://cryptopanic.com/api/developer/v2/posts/"
API_TOKEN = "ef356460da478d6803afa3f02c2d13080c62a968"

# Ana sayfa ve filtre formu
@app.route('/', methods=['GET', 'POST'])
def index():
    params = {
        'auth_token': API_TOKEN,
        'public': 'true',
    }
    currencies = request.form.get('currencies', '')
    filter_type = request.form.get('filter', '')
    region = request.form.get('region', 'en')
    kind = request.form.get('kind', 'all')
    metadata = 'true'

    if currencies:
        params['currencies'] = currencies
    if filter_type:
        params['filter'] = filter_type
    if region:
        params['regions'] = region
    if kind:
        params['kind'] = kind
    params['metadata'] = metadata

    news = []
    if request.method == 'POST':
        resp = requests.get(API_BASE, params=params)
        if resp.status_code == 200:
            news = resp.json().get('results', [])
        else:
            news = []
    return render_template('index.html', news=news)

if __name__ == '__main__':
    app.run(debug=True)
