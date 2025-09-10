# CryptoPanic Haber & Analiz Web Uygulaması

Bu proje, CryptoPanic API ile kripto para haberlerini ve analizlerini sunan bir web uygulamasıdır. React frontend ve Node.js/Express backend proxy ile API anahtarı gizlenir. Modern arayüz, filtreleme ve arama özellikleri içerir.

## Başlangıç

### Backend
1. `cd server`
2. `npm install`
3. `npm start`

### Frontend
1. Ana dizinde `npm install`
2. `npm run dev`

## Özellikler
- Kripto haberlerini ve analizleri listeleme
- Para birimi, filtre, bölge seçimi
- Arama ve yenileme
- API anahtarı sunucu tarafında gizli

## API Proxy
Sunucu `/api/news` endpointi ile CryptoPanic API’ye istek atar. Parametreler frontend’den gönderilebilir.

## Özelleştirme
Arayüz ve filtreler kolayca genişletilebilir.

---

Daha fazla bilgi için CryptoPanic API dokümantasyonuna bakınız.
