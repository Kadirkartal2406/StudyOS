# StudyOS — Git Workflow

**Belge Durumu:** Aktif  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-06 — Meeting-008  
**Dil:** Türkçe  
**Kaynak:** `docs/development/coding-standards.md`

> Commit isimlendirme kuralları için bkz. `docs/development/coding-standards.md §6`.  
> Bu belge dal stratejisi, PR kuralları ve Definition of Done'ı tanımlar.

---

## 1. Dal (Branch) Stratejisi

### 1.1 Kalıcı Dallar

| Dal | Koruma | Amaç |
|-----|--------|------|
| `main` | 🔒 Koruma altında | Üretim kodu. Her commit deploy edilebilir durumda olmalıdır. Doğrudan push yasaktır. |
| `develop` | 🔒 Koruma altında | Aktif geliştirme. Feature dalları buraya merge edilir. CI geçmedikçe merge edilemez. |

**Kural:** `main`'e yalnızca `develop`'tan Pull Request ile geçilebilir. Doğrudan `main`'e push kesinlikle yasaktır.

### 1.2 Geçici Dallar

| Tip | Format | Kaynak Dal | Hedef Dal | Örnek |
|-----|--------|-----------|----------|-------|
| Özellik | `feature/{kodu}-{kısa-açıklama}` | `develop` | `develop` | `feature/S01-login-screen` |
| Hata Düzeltme | `fix/{kodu}-{kısa-açıklama}` | `develop` | `develop` | `fix/S17-fcm-token-null` |
| Acil Düzeltme | `hotfix/{kısa-açıklama}` | `main` | `main` + `develop` | `hotfix/jwt-expiry-crash` |
| Sürüm | `release/{versiyon}` | `develop` | `main` + `develop` | `release/1.0.0` |
| Altyapı | `infra/{kısa-açıklama}` | `develop` | `develop` | `infra/github-actions-setup` |
| Dokümantasyon | `docs/{kısa-açıklama}` | `develop` | `develop` | `docs/api-design-update` |

### 1.3 Dal Yaşam Döngüsü

```mermaid
gitGraph
   commit id: "init"
   branch develop
   checkout develop
   commit id: "proje kurulumu"
   branch feature/S01-login
   checkout feature/S01-login
   commit id: "auth modeli"
   commit id: "login endpoint"
   checkout develop
   merge feature/S01-login id: "PR #1 merge"
   branch feature/S02-register
   checkout feature/S02-register
   commit id: "register endpoint"
   checkout develop
   merge feature/S02-register id: "PR #2 merge"
   branch release/0.1.0
   checkout release/0.1.0
   commit id: "sürüm notları"
   checkout main
   merge release/0.1.0tag: "v0.1.0"
   checkout develop
   merge release/0.1.0
```

### 1.4 Dal Adlandırma Kuralları

- Tüm harfler küçük; kelimeler tire (`-`) ile ayrılır.
- Özellik kodu feature matrix'ten gelir: `S01`, `K07`, `E02`, `A04`.
- Açıklama kısa ve net olur (max 4 kelime).
- Türkçe karakter kullanılmaz (`ş`, `ğ`, `ü`, `ö`, `ç`, `ı`).

**Doğru:** `feature/S01-login-screen`, `fix/K07-schedule-null-check`  
**Yanlış:** `Feature/login`, `feature/çok-uzun-ve-açıklayıcı-bir-dal-adı`, `feature/S01`

---

## 2. Commit Konvansiyonu

> Ayrıntılar için bkz. `docs/development/coding-standards.md §6`.

### 2.1 Format

```
<tip>(<kapsam>): <ne yapıldı — geniş zaman Türkçe>

[opsiyonel gövde — neden yapıldı]

[opsiyonel alt bilgi — ilgili kart/issue]
```

### 2.2 Hızlı Başvuru Tablosu

| Tip | Ne zaman | Örnek |
|-----|---------|-------|
| `feat` | Yeni özellik | `feat(auth): JWT login endpoint eklendi` |
| `fix` | Hata düzeltme | `fix(student): null fcm_token hatası giderildi` |
| `refactor` | Davranış değişikliği olmayan yeniden yazım | `refactor(study-plan): repository katmanı ayrıldı` |
| `test` | Test ekleme | `test(auth): login service unit testleri eklendi` |
| `docs` | Dokümantasyon | `docs(api): /students endpoint güncellendi` |
| `style` | Biçimlendirme | `style: ruff format uygulandı` |
| `chore` | Bağımlılık, config | `chore: drift 2.5.0 güncellendi` |
| `ci` | Pipeline değişikliği | `ci: backend test adımı eklendi` |
| `perf` | Performans | `perf(statistics): composite index eklendi` |

### 2.3 Commit Kuralları

- Her commit tek bir mantıksal değişikliği kapsar.
- Commit mesajı 72 karakteri geçmez (başlık satırı).
- `WIP`, `düzeltme`, `test123` gibi anlamsız mesajlar yasaktır.
- Çalışmayan kod commit edilmez.
- Commit öncesi `dart format` / `ruff check` çalıştırılır.

---

## 3. Pull Request (PR) Kuralları

### 3.1 PR Oluşturma

Her PR açılmadan önce:

1. Yerel dal `develop`'tan güncellenmiş olmalıdır (`git rebase develop`).
2. Tüm testler yerel ortamda geçmelidir.
3. Linting hataları giderilmiş olmalıdır.
4. PR şablonu eksiksiz doldurulmalıdır.

### 3.2 PR Şablonu (`.github/PULL_REQUEST_TEMPLATE.md`)

```markdown
## Değişiklik Özeti

<!-- Ne değişti? Kısaca açıkla. -->

## Gerekçe

<!-- Neden bu değişiklik yapıldı? Hangi özellik veya hata ile ilgili? -->

## İlgili Özellik Kodu

<!-- Örnek: S-01, K-07, A-04 -->

## Test Edildi mi?

- [ ] Birim test yazıldı veya mevcut testler güncellendi
- [ ] Manuel test yapıldı
- [ ] CI pipeline geçti

## Definition of Done Kontrol Listesi

- [ ] Kod, kodlama standartlarına uygun
- [ ] Linting ve formatlama temiz
- [ ] Test kapsamı yeterli
- [ ] Dokümantasyon güncellendi (gerekiyorsa)
- [ ] Breaking change yok (varsa etiket eklendi)
- [ ] PR başlığı commit konvansiyonunu takip ediyor

## Ekran Görüntüsü / Video (UI değişikliği varsa)

<!-- Varsa ekle -->
```

### 3.3 PR Merge Kuralları

| Kural | Açıklama |
|-------|---------|
| **En az 1 onay** | Diğer geliştirici kodu incelemeli ve onaylamalıdır |
| **CI geçmeli** | Tüm GitHub Actions kontrolleri yeşil olmalıdır |
| **Conflict yok** | Tüm çakışmalar çözülmüş olmalıdır |
| **Squash merge** | `develop`'a merge'de squash kullanılır — temiz geçmiş |
| **Dal silinir** | Merge sonrası kaynak dal silinir |

### 3.4 PR Büyüklüğü

- İdeal PR: 200–400 satır değişiklik.
- 600+ satır değişiklik içeren PR'lar küçültülmek üzere iade edilir.
- Büyük özellikler birden fazla PR'a bölünür.

---

## 4. Sürüm Yönetimi

### 4.1 Semantic Versioning

StudyOS [Semantic Versioning 2.0](https://semver.org/) kullanır: `MAJOR.MINOR.PATCH`

| Bölüm | Anlamı | Örnek |
|-------|--------|-------|
| MAJOR | Geriye dönük uyumsuz API değişikliği | `2.0.0` |
| MINOR | Geriye dönük uyumlu yeni özellik | `1.1.0` |
| PATCH | Geriye dönük uyumlu hata düzeltme | `1.0.1` |

### 4.2 Etiket (Tag) Formatı

```
git tag -a v1.0.0 -m "StudyOS v1.0.0 — MVP sürümü"
```

### 4.3 Sürüm Dalı Akışı

```
develop → release/1.0.0 → (test + sürüm notları) → main (tag: v1.0.0) + develop
```

---

## 5. GitHub Actions CI/CD

### 5.1 Backend Pipeline (`.github/workflows/backend-ci.yml`)

Tetikleyici: `develop` ve `main`'e PR veya push

```
Adımlar:
  1. Python 3.12 kurulumu
  2. uv ile bağımlılık kurulumu
  3. ruff check (linting)
  4. mypy (tip kontrolü)
  5. pytest --cov (testler + kapsam raporu)
  6. Coverage eşiği kontrolü (%60 minimum)
```

### 5.2 Flutter Pipeline (`.github/workflows/mobile-ci.yml`)

Tetikleyici: `develop` ve `main`'e PR veya push

```
Adımlar:
  1. Flutter 3.27 kurulumu
  2. flutter pub get
  3. dart format --check (biçimlendirme)
  4. flutter analyze (statik analiz)
  5. flutter test (birim testleri)
```

### 5.3 Deploy Pipeline (`.github/workflows/deploy.yml`)

Tetikleyici: `main`'e merge

```
Adımlar:
  1. Backend CI başarılı
  2. Railway deploy (railway up)
  3. Sentry release bildirimi
```

> **Not:** Deploy pipeline Sprint-1 sonu için yapılandırılacaktır; başlangıçta manuel deploy yapılır.

---

## 6. Definition of Done (DoD)

Bir görev **tamamlandı** sayılmak için aşağıdaki tüm kriterleri karşılamalıdır:

### 6.1 Kod Kalitesi

- [ ] Kodlama standartlarına uygun (`docs/development/coding-standards.md`)
- [ ] Linting hatasız: `flutter analyze` / `ruff check` temiz
- [ ] Formatlama uygulandı: `dart format` / `ruff format`
- [ ] Tip hatası yok: `mypy` geçti (backend)
- [ ] Magic number / sabit değer doğrudan kodda yok

### 6.2 Test

- [ ] Yeni özellik için en az bir birim testi yazıldı
- [ ] Mevcut testler bozulmadı (regresyon yok)
- [ ] CI pipeline tamamen yeşil

### 6.3 Dokümantasyon

- [ ] Yeni endpoint varsa `api-design.md` güncellendi
- [ ] Yeni varlık varsa `database-design.md` güncellendi
- [ ] Kırıcı değişiklik varsa ADR oluşturuldu
- [ ] Kod içi yorum gerekiyorsa eklendi

### 6.4 Kod İnceleme

- [ ] PR en az 1 onay aldı
- [ ] İnceleme yorumları yanıtlandı veya çözüldü
- [ ] Squash merge yapıldı, dal silindi

### 6.5 İşlevsellik

- [ ] Özellik `feature-matrix.md`'deki tanımla örtüşüyor
- [ ] Hata durumları ele alındı (boş state, network hatası vb.)
- [ ] Manuel test senaryosu geçti

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-008 |
