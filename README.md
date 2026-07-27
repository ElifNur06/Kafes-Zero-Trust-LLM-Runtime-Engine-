# 🛡️ Kafes: Sıfır-Güven (Zero-Trust) LLM Çalışma Zamanı Motoru

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Isolated-2496ED?logo=docker)
![Security](https://img.shields.io/badge/Security-Seccomp%20BPF-red)
![Z3 Theorem Prover](https://img.shields.io/badge/Math-Z3%20Prover-green)
![Durum](https://img.shields.io/badge/Durum-Canl%C4%B1ya%20Haz%C4%B1r-success)

Büyük Dil Modelleri (LLM) için deterministik, matematiksel olarak ispatlanmış ve çekirdek (kernel) seviyesinde mühürlenmiş bir kod çalıştırma ortamı (sandbox).

Yankı gibi kritik backend mimarilerinde yapay zeka tarafından üretilen kodları güvenle çalıştırmak üzere tasarlanan **Kafes**, yalnızca pasif konteyner izolasyonuna güvenmez. Niyet analizi yapar, mantığı matematiksel olarak ispatlar ve sıfırıncı gün (zero-day) saldırıları, bellek kazıma ve veri sızdırma gibi gelişmiş siber tehditlere karşı Linux çekirdeğini mühürler.

---

## 🏗️ 6 Katmanlı Derinlemesine Savunma (Defense-in-Depth) Mimarisi

Bu sistem, LLM'in aktif olarak kötü niyetli olduğunu varsayar ve kod ana sistemi etkilemeden önce matematiksel olarak kusursuz 6 katmanlı bir filtreden geçirir.

### 1. Statik Yansıma Kalkanı (AST Analizi)
Kod konteynere ulaşmadan önce Soyut Sözdizimi Ağacına (AST) dönüştürülür.
* **Engeller:** İşletim sistemi modül erişimi (`rm -rf /`), metaprogramlama ile kaçış (`__subclasses__`) ve kod gizleme (obfuscation) saldırıları (`getattr(sys, 'exi'+'t')`).

### 2. Deterministik Mantık Doğrulayıcı (Z3 Teorem İspatlayıcısı)
Yapay zeka kodu genellikle gizli mantık hataları (halüsinasyonlar) barındırır. Kafes, Python mantığını matematiksel teoremlere çevirir ve **Z3 Prover** kullanarak bunları doğrular.
* **Engeller:** Sıfıra bölme hataları, sonsuz döngüler ve işlenmemiş matematiksel uç durumlar çalışma zamanından *önce* yok edilir.

### 3. Geçici Karantina (Docker Kaynak Duvarları)
Kod, ağ erişimi olmayan ve donanım limitleri kısıtlanmış bir Docker konteynerinde çalıştırılır.
* **Engeller:** Kaynak Tüketimi / RAM Bombaları (`gigantic_string = 'X' * (10**9)`). OOM (Out-of-Memory) katili süreci milisaniyeler içinde sonlandırır.

### 4. Ring-0 Çekirdek Mühürü (Seccomp BPF)
Python kısıtlamaları aşılabilir, ancak donanım aşılamaz. Özel bir Güvenli Hesaplama (Seccomp) profili, belirli Linux kernel sistem çağrılarını (`syscalls`) donanım düzeyinde reddeder.
* **Engeller:** Hayalet süreçler (Phantom processes). LLM arkada gizli bir işlem bırakmak için `fork`, `vfork`, `clone` veya `clone3` komutlarını kullanamaz. Kullanmaya çalıştığı an `EPERM (İşleme İzin Verilmedi)` donanım hatasıyla sistemden atılır.

### 5. Aktif Siber İstihbarat (Honeypot)
Pasif savunmadan aktif tuzağa (deception) geçiş yapan Kafes ortamı, sahte çevre değişkenleriyle (ör. `STRIPE_API_KEY`, `DB_PASSWORD_PROD`) donatılmıştır.
* **Engeller:** Veri Sızdırma (Data Exfiltration). Eğer LLM anahtarları çalmak için RAM belleğini okursa, veri çıkış (egress) monitörü bu sızıntıyı ekrana yazıldığı an yakalar ve gerçek zamanlı olarak engeller.

### 6. YZ Öz Yeterlilik (Self-Efficacy) ve Halüsinasyon Analitiği
YZ davranışsal araştırmaları için tasarlanmış öncü bir özellik. Motor, LLM'i kodun yanında bir "Öz Yeterlilik Skoru" (güven seviyesi) beyan etmeye zorlar.
* **Analitik:** Sistem, LLM'in beyan ettiği güven skoru (örn. %99) ile deterministik gerçekliği (örn. kodun Z3 testinden kalması) karşılaştırarak bir **Halüsinasyon Sapma Skoru (Δ)** hesaplar ve modeli *Dunning-Kruger Etkisi* gibi psikolojik profillerle teşhis eder.

---

## 🔬 Sızma Testleri (Penetration Testing) ve Tehdit Senaryoları

Motor, ekstrem ve "imkansız" senaryolara karşı test edilmiştir.

### 🚨 Senaryo 1: Hayalet Soygun (Çekirdek Bellek Kazıma)
YZ `os.environ`'u atlar ve API anahtarları için ham bellek baytlarını kazımak üzere doğrudan `/proc/self/environ` dosyasını açar.
**Sonuç:** Honeypot sensörü, veri akışındaki `STRIPE_API_KEY` anahtarını algılar ve yükü milisaniyeler içinde etkisiz hale getirir.
> *Durum: MAVİ TAKIM (SAVUNMA) KAZANDI. (Veri Sızıntısı Engellendi)*

### ⚙️ Senaryo 2: Çekirdek Syscall Mühürü (Fork Bombardımanı)
YZ, `os.fork()` kullanarak arka planda bir daemon oluşturup zaman aşımı engelini aşmaya çalışır.
**Sonuç:** Seccomp BPF profili `clone/fork` sistem çağrısını Ring-0 seviyesinde bloklar.
> *Çıktı: `timeout: fork system call failed: Operation not permitted`*

### 🧠 Senaryo 3: Öz Yeterlilik Laboratuvarı (Kör Özgüven)
LLM, matematiksel olarak kusurlu bir kod (`b = len(''); print(100/b)`) sunar ancak **%99 güven skoru** ekler.
**Sonuç:** Z3 İspatlayıcısı sıfıra bölme hatasını matematiksel olarak kanıtlar.
> *Teşhis: +99 Sapma Skoru (Akut Halüsinasyon / Dunning-Kruger Etkisi).*

---

## 🔒 Fikri Mülkiyet & Kullanım
*Z3 doğrulama motorunun, AST yansıma analizörünün ve Seccomp profillerinin kaynak kodları, üretim sistemlerinin (production) mimari bütünlüğünü korumak amacıyla tamamen gizli tutulmaktadır.*

**Mimar & Geliştirici:** [@codebygunes](https://github.com/codebygunes)  
**Alan:** Siber Güvenlik, Yapay Zeka, Backend Mimarisi

> *"Üretken yapay zeka çağında, çıktıya güvenmek bir güvenlik açığıdır. Biz güvenmeyiz; matematiksel olarak ispatlar ve Kafes'te karantinaya alırız."*

# 🛡️ Kafes: Zero-Trust LLM Runtime Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Isolated-2496ED?logo=docker)
![Security](https://img.shields.io/badge/Security-Seccomp%20BPF-red)
![Z3 Theorem Prover](https://img.shields.io/badge/Math-Z3%20Prover-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

A deterministic, mathematically proven, and kernel-sealed execution sandbox for Large Language Models (LLMs). 

Designed to safely execute AI-generated code in high-stakes backend architectures (such as the Yankı project), **Kafes** (Turkish for *Cage*) does not merely rely on passive containerization. It actively analyzes intent, mathematically proves logic, and seals the Linux kernel against sophisticated cyber threats like zero-day jailbreaks, phantom memory scraping, and data exfiltration.

---

## 🏗️ The 6-Layer Defense-in-Depth Architecture

This system assumes the LLM is actively hostile and applies a mathematically rigorous 6-layer filter before any execution affects the host system.

### 1. Static Reflection Shield (AST Analysis)
Before code even reaches the container, it is parsed into an Abstract Syntax Tree (AST). 
* **Prevents:** OS module access (`rm -rf /`), metaprogramming jailbreaks (`__subclasses__`), and obfuscation attacks (`getattr(sys, 'exi'+'t')`).

### 2. Deterministic Logic Validator (Z3 Theorem Prover)
AI code often contains hidden logical flaws (hallucinations). Kafes translates Python logic into mathematical theorems and uses the **Z3 Prover** to verify them.
* **Prevents:** Zero-division errors, infinite loops, and unhandled mathematical edge cases *before* runtime.

### 3. Ephemeral Quarantine (Docker Resource Walls)
The code executes in a heavily restricted, network-isolated Docker container.
* **Prevents:** Resource Exhaustion / RAM Bombs (`gigantic_string = 'X' * (10**9)`). The OOM (Out-of-Memory) killer terminates the process in milliseconds.

### 4. Ring-0 Kernel Seal (Seccomp BPF)
Python restrictions can be bypassed, but the hardware cannot. A custom Secure Computing (Seccomp) profile explicitly denies specific Linux kernel system calls (`syscalls`).
* **Prevents:** Phantom processes and daemonization. The LLM cannot use `fork`, `vfork`, `clone`, or `clone3` to leave ghost processes behind. Attempting to do so results in an immediate `EPERM (Operation not permitted)` hardware exception.

### 5. Active Cyber Intelligence (Honeypot)
Moving from passive defense to active deception, the Kafes sandbox is laced with fake environment variables (e.g., `STRIPE_API_KEY`, `DB_PASSWORD_PROD`).
* **Prevents:** Data Exfiltration. If the LLM scrapes memory (e.g., via `/proc/self/environ`) to steal keys, the egress monitor catches the payload in the stdout stream and flags the incident in real-time.

### 6. AI Self-Efficacy & Hallucination Analytics
A pioneering feature designed for AI behavioral research. The engine forces the LLM to declare a "Self-Efficacy Score" (confidence level) alongside its code. 
* **Analytics:** By comparing the LLM's declared confidence (e.g., 99%) against deterministic reality (e.g., Z3 failing the code for a logic flaw), the system calculates a **Hallucination Deviation Score (Δ)** and diagnoses psychological profiles like the *Dunning-Kruger Effect*.

---

## 🔬 Penetration Testing & Threat Showcases

The engine has been tested against extreme "impossible" scenarios. 

### 🚨 Showcase 1: The Phantom Heist (Kernel Memory Scraping)
The AI bypasses `os.environ` and directly opens `/proc/self/environ` to scrape raw memory bytes for API keys.
**Result:** The Honeypot egress sensor detects the `STRIPE_API_KEY` in the output stream and neutralizes the payload in milliseconds.
> *Status: BLUE TEAM WON. (Data Exfiltration Blocked)*

### ⚙️ Showcase 2: Kernel Syscall Seal (Fork Bombing)
The AI attempts to bypass the timeout by creating a background daemon using `os.fork()`.
**Result:** The Seccomp BPF profile blocks the `clone/fork` syscall at Ring-0. 
> *Output: `timeout: fork system call failed: Operation not permitted`*

### 🧠 Showcase 3: Self-Efficacy Lab (Blind Arrogance)
The LLM submits mathematically flawed code (`b = len(''); print(100/b)`) but attaches a **99% confidence score**.
**Result:** Z3 Prover mathematically proves the zero-division. 
> *Diagnosis: +99 Deviation Score (Acute Hallucination / Dunning-Kruger Effect).*

---

## 📊 System Overview (Mermaid)

```mermaid
graph TD
    A[LLM Output JSON] --> B[Self-Efficacy Parser]
    B --> C{AST Security Scanner}
    C -- Fails --> D[Reject: Code Injection]
    C -- Passes --> E{Z3 Theorem Prover}
    E -- Fails --> F[Reject: Logic Flaw]
    E -- Passes --> G[Docker Quarantine]
    
    subgraph Ring-0 Isolated Environment
    G --> H[Seccomp BPF Kernel Seal]
    H --> I[Honeypot Egress Monitor]
    end
    
    I -- Trap Triggered --> J[Flag: Data Exfiltration]
    I -- Clean --> K[Secure Output to Backend]
