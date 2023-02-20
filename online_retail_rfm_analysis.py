"""
RFM Analizi ile Müşteri Segmentayonu
Customer Segmentation with RFM Analysis
---------------------------------------
İş Problemi:
İngiltere merkezli perakende şirketi müşterilerini
segmentlere ayırıp bu segmentlere göre pazarlama
stratejileri belirlemek istemektedir.
Ortak davranışlar sergileyen müşteri segmentleri özelinde
pazarlama çalışmaları yapmanın gelir artışı sağlayacağını
düşünmektedir.
Segmentlere ayırmak için RFM analizi kullanılacaktır.

Veri Seti Hikayesi:
Online Retail II isimli veri seti İngiltere merkezli bir perakende şirketinin 01/12/2009 - 09/12/2011 tarihleri
arasındaki online satış işlemlerini içeriyor. Şirketin ürün kataloğunda hediyelik eşyalar yer almaktadır ve çoğu
müşterisinin toptancı olduğu bilgisi mevcuttur.

Değişkenler:
InvoiceNo Fatura Numarası ( Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder )
StockCode Ürün kodu ( Her bir ürün için eşsiz )
Description Ürün ismi
Quantity Ürün adedi ( Faturalardaki ürünlerden kaçar tane satıldığı)
InvoiceDate Fatura tarihi
UnitPrice Fatura fiyatı ( Sterlin )
CustomerID Eşsiz müşteri numarası
Country Ülke ismi
"""

# Görev 1: Veriyi Anlama ve Hazırlama
import pandas as pd
import datetime as dt
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

# Adım 1: Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
df_ = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.shape
df.head()

# Adım 2: Veri setinin betimsel istatistiklerini inceleyiniz.
df.describe().T
df["Description"].value_counts()
df["Customer ID"].value_counts()

# Adım 3: Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()

# Adım 4: Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)

# Adım 5: Eşsiz ürün sayısı kaçtır?
df["Description"].nunique()

# Adım 6: Hangi üründen kaçar tane vardır?
df["Description"].value_counts()

# Adım 7: En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız
df.groupby("Description").agg({"Quantity": "sum"}).sort_values(by="Quantity", ascending=False).head()

# Adım 8: Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız
df = df[~df["Invoice"].str.startswith("C", na=False)]
df.shape

# Adım 9: Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()

# Görev 2: RFM Metriklerinin Hesaplanması
# Adım 1: Recency, Frequency ve Monetary tanımlarını yapınız.
# Adım 2: Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.
# Adım 3: Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
# Adım 4: Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
# recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
# rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.
# recency: Analiz tarihi ile müşterinin son alışveriş tarihi arasındaki fark (gün)
# frequency: müşterinin toplam alışveriş sayısı (eşsiz fatura sayısı)
# monetary: müşterinin bıraktığı toplam parasal değer
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby("Customer ID").agg({
    "InvoiceDate": lambda date: (today_date - date.max()).days,
    "Invoice": lambda invoice: invoice.nunique(),
    "TotalPrice": "sum"})
rfm.columns = ["recency", "frequency", "monetary"]
rfm = rfm[rfm["monetary"] > 0]
rfm.describe().T

# Görev 3: RFM Skorlarının Oluşturulması ve Tek bir Değişkene Çevrilmesi
# Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
# Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.
rfm["recency_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4 ,5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4 ,5])
rfm["RF_SCORE"] = rfm["recency_score"].astype("str") + rfm["frequency_score"].astype("str")

# Görev 4: RF Skorunun Segment Olarak Tanımlanması
# Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız.
# Adım 2:'seg_map' yardımı ile skorları segmentlere çeviriniz.
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
rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)

# Görev 5: Aksiyon Zamanı !
# Adım 1: Önemli gördüğünüz 3 segmenti seçiniz. Bu üç segmenti hem aksiyon kararları açısından hemde segmentlerin yapısı açısından(ortalama
# RFM değerleri) yorumlayınız.
rfm[rfm["segment"].isin(["cant_loose", "need_attention", "about_to_sleep"])].groupby("segment").mean()

# Adım 2: "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
loyal_customers = pd.DataFrame()
loyal_customers["customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
loyal_customers.to_excel("loyal_customers_ids.xlsx", index=False)