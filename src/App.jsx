import React, { useEffect, useState } from 'react';
import { fetchNews } from './api';

const filters = [
  'rising', 'hot', 'bullish', 'bearish', 'important', 'saved', 'lol'
];
const regions = [
  'en', 'de', 'nl', 'es', 'fr', 'it', 'pt', 'ru', 'tr', 'ar', 'cn', 'jp', 'ko'
];

function App() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');
  const [currency, setCurrency] = useState('');
  const [region, setRegion] = useState('en');
  const [search, setSearch] = useState('');

  useEffect(() => {
    getNews();
    // eslint-disable-next-line
  }, [filter, currency, region]);

  const getNews = async () => {
    setLoading(true);
    const params = {
      public: true,
      filter: filter || undefined,
      currencies: currency || undefined,
      regions: region || undefined,
      metadata: true
    };
    const data = await fetchNews(params);
    setNews(data.results || []);
    setLoading(false);
  };

  const filteredNews = news.filter(post =>
    search ? post.title.toLowerCase().includes(search.toLowerCase()) : true
  );

  return (
    <div style={{ maxWidth: 900, margin: 'auto', padding: 24 }}>
      <h1>Kripto Haber & Analiz</h1>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value=''>Filtre Yok</option>
          {filters.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
        <input
          placeholder='Para birimi (BTC, ETH...)'
          value={currency}
          onChange={e => setCurrency(e.target.value.toUpperCase())}
        />
        <select value={region} onChange={e => setRegion(e.target.value)}>
          {regions.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
        <input
          placeholder='Haberlerde ara'
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button onClick={getNews}>Yenile</button>
      </div>
      {loading ? <div>Yükleniyor...</div> : (
        <div>
          {filteredNews.length === 0 ? <div>Haber bulunamadı.</div> : (
            filteredNews.map(post => (
              <div key={post.id} style={{ border: '1px solid #eee', borderRadius: 8, marginBottom: 16, padding: 16 }}>
                <h2>{post.title}</h2>
                {post.image && <img src={post.image} alt='' style={{ maxWidth: 200, borderRadius: 8 }} />}
                <p>{post.description}</p>
                <a href={post.url} target='_blank' rel='noopener noreferrer'>Kaynağa Git</a>
                <div style={{ fontSize: 12, color: '#888' }}>{post.published_at}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default App;
