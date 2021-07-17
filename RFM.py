# Görev 1:
# Veriyi Anlama ve Hazırlama
# 1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

# 2. Veri setinin betimsel istatistiklerini inceleyiniz.
df.head()
df.shape
df.describe()
# 3. Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().any()
df.isnull().sum()
# 4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)
df.shape
# 5. Eşsiz ürün sayısı kaçtır?
df["StockCode"].nunique()
# 6. Hangi üründen kaçar tane vardır?
df["StockCode"].value_counts()
# 7. En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by="Quantity",ascending=False).head(5)

# 8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]

# 9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Görev 2:
# RFM metriklerinin hesaplanması
# § Recency, Frequency ve Monetary tanımlarını yapınız.
# § Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile
# hesaplayınız.
# § Hesapladığınız metrikleri rfmisimli bir değişkene atayınız.
# § Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
# İpucu:
# Not 1: recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
# Not 2: rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.

# rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,num: num.nunique(),"TotalPrice": lambda price: price.sum()})

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,'Invoice': lambda num: num.nunique(),'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.columns = ['recency', 'frequency', 'monetary']
rfm = rfm[rfm["monetary"] > 0]

rfm.head()
rfm.describe().T


# Görev 3:
# RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi
# § Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# § Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
# § Oluşan 3 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
# Örneğin;
# Ayrı ayrı değişkenlerde sırasıyla 5, 2, 1 olan recency_score, frequency_score ve monetary_score skorlarını
# RFM_SCORE değişkeni isimlendirmesi ile 521 olarak oluşturunuz.

# İpucu:

# rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"].head()  # champions

rfm[rfm["RFM_SCORE"] == "11"].head()  # hibernating


# Görev 4:
# RFM skorlarının segment olarak tanımlanması
# § Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları
# yapınız.
# § Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.
#
# İpucu:
# seg_map = {
#         r'[1-2][1-2]': 'hibernating',
#         r'[1-2][3-4]': 'at_risk',
#         r'[1-2]5': 'cant_loose',
#         r'3[1-2]': 'about_to_sleep',
#         r'33': 'need_attention',
#         r'[3-4][4-5]': 'loyal_customers',
#         r'41': 'promising',
#         r'51': 'new_customers',
#         r'[4-5][2-3]': 'potential_loyalists',
#         r'5[4-5]': 'champions'
#     }
#
#     rfm['rfm_segment'] = rfm['rfm_segment'].replace(seg_map, regex=True)
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()


# Görev 5:
# Aksiyon zamanı!
# § Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# - Hem aksiyon kararları açısından,
# - Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.
# § "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
rfm["Country"] = df["Country"]

rfm[["segment", "recency", "frequency", "monetary"]].groupby(["segment"]).agg(["mean","count"])

rfm.groupby(['segment',"Country"]).agg({"segment":"count"})


rfm[rfm["segment"] == "at_Risk"].head()
rfm[rfm["segment"] == "new_customers"].head()
rfm[rfm["segment"] == "potential_loyalists"].head()

new_df = pd.DataFrame()
new_df["loyal_customers"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

new_df.to_excel("loyal_customers.xlsx")

# Aksiyon Planları:
# İlk seçtiğim segment At Risk olanlar. Bu grubu tekrar işlem yaptırabilirsek Loyal Customer segmentine geçiş yapacaklardır. Bu segmentin parası var, işlem sıklığı da recency değerine bağlı olarak artacaktır. Örneğin 6 ay ve üzeri süredir müşterimiz olan ve 1000 birim para harcamış kişilere  konsol, bilgisayar, müzik sistemleri ve TV gibi fiyatı görece yüksek ve eğlenceye hizmet eden çeşitli teknolojik ürünlerde yapacağımız kampanyalarla bu kesimi yakalama şansımız bir hayli yüksektir.

# İkinci seçtiğim segment Potential Loyalists. Bu grubu da Loyal Customer segmentine yükseltebilmemiz için işlem sıklığı çok önemli. Bu grubun da günlük ev ihtiyaçları ve market alışverişi gibi ürünleri buradan satın almasını sağlamak için bu ürünlerde belli bir sayı bazında indirim yapılabilir. Örneğin; 3 paket makarna %15 indirimli ve kargo bedava gibi. Bu şekilde birim fiyatı düşük ama birden fazla adet satın alım yaptırarak artık günlük ihitiyaçları buradan satın aldırma alışkanlığını da kazandırırsak bu grubun işlem sıklığı artarak devam eder.

# Üçüncü seçtiğim segment New Customers. Bu müşteriler yeni müşteriler, bir şekilde burayı tercih etmeye başlamışlar. Bu grubun burada iyi hizmet almaya devam etmesi gerekir. Yeni müşteri memnun kaldığı yeri Word-of-Mouth Marketing prensibiyle yeni müşteri kazandıracak kişiler olarak görmek gerekir. Aldığı tatmin edici hizmet yeni müşterileri de buraya çekecektir ve kendisi de sadık müşteri olma yolunda ilerleyecektir. Bu müşteri türünü yakalamanın ve elde tutmanın yollarından birisi çeşitli hobi, kıyafet ya da ev tekstili gibi ürünleri avantajlı bir fiyata burada bulmasını sağlamaktır. Bu müşterilerin Monetary ortalaması 388, yani görece ucuz ürünü almışlar ve müşteri olmuşlar. Örneğin; kutu oyunları, halı, ya da kışlık ceket gibi bu segmentin giriş-orta düzey ürünleriyle bunlara bir alışkanlık kazandırmak bu müşterileri elde tutar.
