# cx_rag — Yapay Zekâ Destekli Bilgi Asistanı

**Hazırlayan:** Abdullah Hazuri
**Sunulan:** Customer Experience Ltd.

Kurgusal çamaşır makinesi şirketi **cx_wash**'ın müşteri destek ekibi için hazırlanmış, şirket belgelerinden Türkçe cevap veren bir bilgi asistanıdır.

## Ne yaptım

- **Belgeler:** cx_wash için 10 Türkçe `.txt` belgesi (`documents/`). İade politikasının eski ve güncel sürümü vardır.
- **Soru-cevap API'si:** Belgeler bölümlere ayrılır, vektöre çevrilir ve aranır; model yalnızca bulunan bölümlerden cevap verir.
- **Kaynak gösterimi:** Her cevap belge adını, bölümü, sürümü ve tarihi döndürür.
- **Cevap verememe:** Belgelerde bilgi yoksa sistem uydurmaz; `answerable: false` ve kibar bir özür mesajı döner.
- **Sürüm seçimi:** Aynı adla yeniden yüklenen belge yeni sürüm olur. Cevapta yalnızca en yüksek sürüm kullanılır, eski sürüm ayrıca gösterilir.
- **Sohbet hafızası:** Konuşmalar saklanır; her soruda son 5 mesaj modele gönderilir.
- **Arayüz ve Docker:** Tüm uç noktaları gösteren bir React arayüzü ve tek dosyalık Docker Compose kurulumu.

## Teknoloji yığını

| Katman | Teknoloji | Neden |
|---|---|---|
| API | Python 3.12, FastAPI | Görevde önerildi; Swagger belgelerini kendiliğinden üretir |
| Veritabanı | Microsoft SQL Server 2022 | .NET ekipleriyle uyumlu; belgeler, bölümler ve mesajlar burada |
| Vektör veritabanı | Qdrant | Tek konteyner; vektörün yanında belge adı ve sürüm saklar |
| Dil modeli | OpenAI veya OpenRouter | Fabrika deseni ile ayardan seçilir |
| Gömme modeli | OpenAI `text-embedding-3-small` | Türkçeyi destekler |
| Arayüz | React, Vite | API'nin davranışını görünür kılar |

## Klasör yapısı

```
├── docker-compose.yml               Tüm servisler
├── .env.example                     Örnek ortam değişkenleri
├── cx_rag.postman_collection.json   Postman koleksiyonu
├── documents/                       Bilgi belgeleri (eski_surum/ içinde eski iade politikası)
├── src/                             Backend
│   ├── routes/                      API uç noktaları
│   ├── controller/                  İş mantığı (bölümleme, sürüm seçimi, cevap)
│   ├── models/                      Tablolar, sorgular ve Alembic göçleri
│   └── stores/                      Dil modeli ve vektör veritabanı sağlayıcıları, istem şablonları
└── frontend/                        Arayüz
```

## Docker ile çalıştırma

1. `.env.example` dosyasını `.env` adıyla kopyalayın; `OPENAI_API_KEY` ve `MSSQL_PASSWORD` değerlerini doldurun.
2. Sistemi başlatın:

```bash
docker compose up -d --build
```

Veritabanı ve tablolar kendiliğinden oluşturulur. Tüm verileri silip sıfırlamak için `docker compose down -v` kullanılır.

## Docker olmadan çalıştırma

Gereksinimler:

- Python 3.12 ve Node.js 20+
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Çalışan bir SQL Server (ücretsiz Express veya Developer sürümü yeterlidir)
- Çalışan bir Qdrant ([bağımsız sürüm](https://github.com/qdrant/qdrant/releases) veya Qdrant Cloud)

`.env` dosyasında `MSSQL_HOST`, `MSSQL_PORT`, `MSSQL_USERNAME`, `MSSQL_PASSWORD` ve `VECTOR_DB_URL` değerlerini kendi kurulumunuza göre ayarlayın. Docker varsa bu iki servis `docker compose up -d mssql qdrant` ile de başlatılabilir.

Backend (Windows için; Linux ve macOS'ta etkinleştirme komutu `source .venv/bin/activate` olur):

```bash
cd src
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
cd models/db_schemes/cx_rag
alembic upgrade head
cd ../../..
fastapi run main.py --port 8000
```

`init_db.py` veritabanını, `alembic upgrade head` tabloları oluşturur; bu iki adım yalnızca ilk kurulumda gereklidir. uv kullananlar `pip install` yerine `uv sync` çalıştırıp komutların başına `uv run` ekleyebilir.

Arayüz için ayrı bir terminalde:

```bash
cd frontend
npm install
npm run dev
```

## Erişim

| Adres | Ne için |
|---|---|
| http://localhost:8000/docs | Swagger; API buradan denenebilir |
| http://localhost:3000 | Arayüz |
| localhost:1433 | SQL Server |
| http://localhost:6333/dashboard | Qdrant paneli |

Sistemi başlattıktan sonra Swagger için http://localhost:8000/docs, arayüz için http://localhost:3000 adresini açın. İstekler ayrıca kök dizindeki `cx_rag.postman_collection.json` dosyası Postman'e aktarılarak denenebilir.

## Belgelerin yüklenmesi

Sürüm yükleme sırasına göre belirlendiği için sıra önemlidir:

1. Arayüzde önce `documents/eski_surum/` içindeki dosyayı yükleyin.
2. Sonra `documents/` içindeki 9 dosyayı yükleyin.
3. **Split documents**, ardından **Index chunks** düğmesine basın.
4. **Ask** sekmesinden soru sorun.

## Yaklaşım

- **Bölümleme:** Belgeler `## ` başlıklarından bölünür; başlık yoksa yaklaşık 500 karakterlik parçalar kullanılır. Böylece cevapta bölüm adı gösterilebilir.
- **Otomatik belge bilgisi:** Ad dosya adından, tarih yükleme gününden, sürüm aynı adla yapılan yükleme sırasından alınır.
- **Sürüm seçimi kodda yapılır:** Bulunan bölümler belge adına göre gruplanır ve yalnızca en yüksek sürüm modele gider. Karar modele bırakılmadığı için sonuç tutarlıdır.
- **İki aşamalı reddetme:** Eşleşme puanı `RAG_MIN_SCORE` altındaki bölümler elenir; kalan bölümler yetersizse model `NO_ANSWER` yazar ve kod bunu reddetmeye çevirir.
- **Fabrika deseni:** Dil modeli ve vektör veritabanı birer arayüzün arkasındadır; yeni sağlayıcı eklemek bir sınıf ve bir satırdır.

## Bilinen sınırlamalar

- Sürüm seçimi yalnızca aramadan dönen bölümleri karşılaştırır ve yükleme sırasına bağlıdır.
- Belge silme veya güncelleme uç noktası yoktur; aynı dosya iki kez yüklenirse iki kopya oluşur.
- Dizinleme istek içinde çalışır; arka plan işçisi yoktur.
- Konu dışı bir sorudan sonraki devam sorusu daha zayıf sonuç getirebilir.
- `RAG_MIN_SCORE` deneme ile seçilmiştir; farklı bir gömme modelinde yeniden ayarlanmalıdır.
