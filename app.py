from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_BASE = "https://cryptopanic.com/api/developer/v2/posts/"
API_TOKEN = "ef356460da478d6803afa3f02c2d13080c62a968"

# Ana sayfa ve filtre formu
@app.route('/', methods=['GET', 'POST'])
def index():
    params = {
        'auth_token': API_TOKEN,
        'public': 'true',
        'metadata': 'true',
        'kind': 'news',   # Sadece haberler
        'regions': 'en',  # İngilizce haberler
    }
    currencies = request.form.get('currencies', '')
    filter_type = request.form.get('filter', '')
    region = request.form.get('region', 'en')
    kind = request.form.get('kind', '')

    if currencies:
        params['currencies'] = currencies
    if filter_type:
        params['filter'] = filter_type
    if region:
        params['regions'] = region
    if kind in ['news', 'media']:
        params['kind'] = kind

    news = []
    error = None
    if request.method == 'POST' or request.method == 'GET':
        try:
            resp = requests.get(API_BASE, params=params)
            if resp.status_code == 200:
                all_news = resp.json().get('results', [])
                # En güncel haberleri en üstte göstermek için published_at'a göre sırala
                def get_pub(post):
                    pub = post.get('published_at') or post.get('created_at')
                    try:
                        return datetime.strptime(pub, '%Y-%m-%dT%H:%M:%SZ') if pub else datetime.min
                    except Exception:
                        return datetime.min
                all_news_sorted = sorted(all_news, key=get_pub, reverse=True)
                # Sadece son 48 saat içindeki haberleri göster
                now = datetime.utcnow()
                filtered_news = []
                for post in all_news_sorted:
                    pub = post.get('published_at') or post.get('created_at')
                    if pub:
                        try:
                            pub_dt = datetime.strptime(pub, '%Y-%m-%dT%H:%M:%SZ')
                            if (now - pub_dt) <= timedelta(hours=48):
                                filtered_news.append(post)
                        except Exception:
                            filtered_news.append(post)
                news = filtered_news
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

@app.route('/api/posts', methods=['POST'])
def api_posts():
    params = {
        'auth_token': API_TOKEN,
        'public': 'true',
        'metadata': 'true',
    }
    data = request.get_json(force=True)
    currencies = data.get('currencies', '')
    filter_type = data.get('filter', '')
    region = data.get('region', 'en')
    kind = data.get('kind', '')
    if currencies:
        params['currencies'] = currencies
    if filter_type:
        params['filter'] = filter_type
    if region:
        params['regions'] = region
    if kind in ['news', 'media']:
        params['kind'] = kind
    try:
        resp = requests.get(API_BASE, params=params)
        if resp.status_code == 200:
            news = resp.json().get('results', [])
            return jsonify({'status': 'ok', 'news': news})
        else:
            return jsonify({'status': 'error', 'error': resp.text}), resp.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/post/<post_id>', methods=['GET'])
def api_post_detail(post_id):
    params = {
        'auth_token': API_TOKEN,
        'public': 'true',
        'metadata': 'true',
        'id': post_id
    }
    try:
        resp = requests.get(API_BASE, params=params)
        if resp.status_code == 200:
            results = resp.json().get('results', [])
            if results:
                return jsonify({'status': 'ok', 'post': results[0]})
            else:
                return jsonify({'status': 'error', 'error': 'Haber bulunamadı.'}), 404
        else:
            return jsonify({'status': 'error', 'error': resp.text}), resp.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
