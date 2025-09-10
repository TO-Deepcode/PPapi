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
    kind = request.form.get('kind', '')
    metadata = 'true'

    if currencies:
        params['currencies'] = currencies
    if filter_type:
        params['filter'] = filter_type
    if region:
        params['regions'] = region
    if kind in ['news', 'media']:
        params['kind'] = kind
    params['metadata'] = metadata

    news = []
    error = None
    if request.method == 'POST':
        try:
            resp = requests.get(API_BASE, params=params)
            if resp.status_code == 200:
                news = resp.json().get('results', [])
            else:
                error = f"API Hatası: {resp.status_code} - {resp.text}"
        except Exception as e:
            error = f"İstek hatası: {str(e)}"
    return render_template('index.html', news=news, error=error)

@app.route('/post/<post_id>')
def post_detail(post_id):
    params = {
        'auth_token': API_TOKEN,
        'public': 'true',
        'metadata': 'true',
    }
    params['id'] = post_id
    error = None
    post = None
    try:
        resp = requests.get(API_BASE, params=params)
        if resp.status_code == 200:
            results = resp.json().get('results', [])
            if results:
                post = results[0]
            else:
                error = "Haber bulunamadı."
        else:
            error = f"API Hatası: {resp.status_code} - {resp.text}"
    except Exception as e:
        error = f"İstek hatası: {str(e)}"
    return render_template('detail.html', post=post, error=error)

if __name__ == '__main__':
    app.run(debug=True)
