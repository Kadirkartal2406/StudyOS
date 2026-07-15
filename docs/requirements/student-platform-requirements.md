# StudyOS Kurumsal Platform - Dershane Yönetim Sistemi

Bu doküman, öğrenci mobil uygulaması ile entegre çalışan ancak ayrı bir ürün olarak geliştirilecek Dershane Yönetim Platformunu tanımlar.

## Proje Tanıtımı

Dershaneler, kurslar ve eğitim kurumları için web tabanlı yönetim platformudur. Öğrenci mobil uygulamasıyla çift yönlü veri alışverişi yapar.

## Mimari

İki ayrı uygulama bulunur:

1. StudyOS Öğrenci Mobil Uygulaması
2. StudyOS Kurumsal (Dershane) Web Platformu

Her iki uygulama ortak API ve veritabanı servisleri üzerinden güvenli şekilde haberleşir.

## Fonksiyonel Gereksinimler

- Kurum kaydı
- Şube yönetimi
- Sınıf oluşturma
- Öğretmen oluşturma
- Öğrenci davet etme
- Öğrencileri sınıfa atama
- Ders programı oluşturma
- Dijital yoklama
- Ödev oluşturma ve teslim takibi
- Duyurular
- PDF, kitap ve doküman yükleme
- Video ders paylaşımı
- Deneme sınavı oluşturma
- Optik sonuç aktarımı
- Deneme analizleri
- Konu bazlı başarı analizi
- Öğrenci gelişim raporları
- Sınıf ve kurum istatistikleri
- AI akademik danışman
- Riskli öğrenci tespiti
- Veli erişimi
- Yetkilendirme ve rol yönetimi
- Rapor dışa aktarma

## Fonksiyonel Olmayan Gereksinimler

- Web tabanlı responsive tasarım
- Yüksek performans
- Güvenli kimlik doğrulama
- KVKK uyumu
- Günlük otomatik yedekleme
- Ölçeklenebilir mimari
- Loglama ve hata takibi
- %99 erişilebilirlik

## Öğrenci Uygulaması Entegrasyonu

- Çalışma süreleri senkronize edilir.
- Deneme sonuçları iki platformda görünür.
- Ödevler mobil uygulamaya düşer.
- PDF ve materyaller mobilde açılır.
- AI analizleri iki tarafta kullanılabilir.
- Öğrenci başarı grafikleri kurum paneline aktarılır.

## Sürümler

- **MVP:** Kurum, sınıf, öğrenci, öğretmen, PDF, deneme.
- **V2:** AI analiz, veli paneli, gelişmiş raporlama.
- **V3:** Canlı ders, mesajlaşma, ödev sistemi, optik okuma.
- **V4:** Çoklu kurum yönetimi, LMS özellikleri, API entegrasyonları.

## Gelir Modeli

- Kurum başına aylık/yıllık lisans
- Öğrenci başına lisans
- Premium AI modülleri
- Kurumsal raporlama paketleri

## Uzun Vadeli Vizyon

Öğrenci uygulaması ve kurumsal platform birbirinden bağımsız ürünlerdir ancak ortak kullanıcı hesabı, API ve veri altyapısı sayesinde tek eğitim ekosistemi olarak çalışırlar.
