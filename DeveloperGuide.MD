# CrewAI VSCode Uzantısı Geliştirme Rehberi

CrewAI tabanlı çoklu ajan sistemini VSCode'a entegre etmek için kapsamlı geliştirme rehberi.

## 📋 İçindekiler
- [Mimari Tasarım](#-mimari-tasarım)
- [Kurulum ve Başlangıç](#-kurulum-ve-başlangıç)
- [İletişim Protokolü](#-iletişim-protokolü)
- [Önemli Özellikler](#-önemli-özellikler)
- [Geliştirme Yol Haritası](#-geliştirme-yol-haritası)
- [Katkıda Bulunma](#-katkıda-bulunma)

## 🏗 Mimari Tasarım

### Sistem Mimarisi
```
├── VSCode Uzantısı (TypeScript)
│   ├── Webview Paneli
│   ├── Python IPC Katmanı
│   └── Dosya Yöneticisi
│
└── Python Arka Uç
    ├── 5 Temel Ajan
    ├── LangChain Entegrasyonu
    └── Araç Yönetim Sistemi
```

### Ana Bileşenler
- **Webview Panel**: Ajan etkileşimleri için GUI
- **IPC Katmanı**: JSON tabanlı mesajlaşma sistemi
- **Hafıza Yöneticisi**: Proje bazlı context saklama

## 🛠 Kurulum ve Başlangıç

### Ön Koşullar
- Node.js v18+
- Python 3.9+
- VSCode 1.85+

### Kurulum Adımları
```bash
# 1. Uzantı iskeletini oluştur
npm install -g yo generator-code
yo code

# 2. Python bağımlılıklarını yükle
pip install crewai langchain python-dotx

# 3. Geliştirme modunda başlat
code ./crewai-extension && F5
```

## 📡 İletişim Protokolü

### Temel Mesaj Formatı
```typescript
interface BaseMessage {
  type: 'task' | 'tool_request' | 'agent_response';
  timestamp: number;
  correlationId: string;
}
```

### Örnek Mesaj Akışı
```json
// Kullanıcı Görevi
{
  "type": "user_task",
  "content": "Merkezi yapılandırma yönetimi için bir modül oluştur"
}

// Araç Çağrısı
{
  "type": "tool_request",
  "tool": "create_file",
  "params": {
    "path": "src/config.js",
    "content": "export default {}"
  }
}
```

## 🌟 Önemli Özellikler

### Akıllı Hafıza Yönetimi
```python
# Hafıza kaydetme örneği
def save_agent_memory(project_path, agent_name, memory):
    memory_dir = os.path.join(project_path, ".crewai_memories")
    os.makedirs(memory_dir, exist_ok=True)
    
    memory_file = os.path.join(memory_dir, f"{agent_name}.json")
    with open(memory_file, 'w') as f:
        json.dump(memory, f)
```

### Güvenlik Önlemleri
- 🔑 API anahtarları için VSCode Secret Storage
- 🛡️ Tüm dosya işlemleri için izin denetimi
- ⏱️ API çağrı limit yöneticisi

## 🚀 Geliştirme Yol Haritası

### Aşama 1 - Temel İşlevler
- [x] Uzantı iskeleti oluşturma
- [x] Tek ajanlı prototip
  - [x] Python backend implementation with CrewAI
  - [x] WebSocket-based IPC layer
  - [x] VSCode Webview panel
- [x] Temel dosya işlemleri
  - [x] File operations tool implementation
  - [x] Natural language command parsing
  - [x] Memory-aware file handling

#### Desteklenen Dosya İşlemleri

```typescript
// Temel Komutlar ve Örnekler
{
  "create_file": "create a new file called example.js with content 'console.log(\"Hello\")'",
  "read_file": "show the contents of config.json",
  "list_files": "list all files in src/components",
  "delete_file": "delete the file temp.txt",
  "rename_file": "rename file old.js to new.js",
  "copy_file": "copy file source.txt to backup.txt",
  "create_directory": "create a new directory called test",
  "get_file_info": "show info about package.json"
}
```

Her dosya işlemi güvenlik kontrolleri ve hata yönetimi içerir:
- Yol doğrulama ve normalizasyon
- İzin kontrolleri
- Var olan dosya/dizin kontrolleri
- Hata ayıklama ve raporlama

#### Tek Ajanlı Prototip Yapısı

```
src/
├── backend/                 # Python backend
│   ├── agents/             # Agent implementations
│   │   └── base_agent.py   # CrewAI agent base class
│   ├── memory/             # Memory management
│   │   └── memory_manager.py
│   ├── tools/              # Agent tools
│   │   └── file_operations.py
│   ├── ipc/               # Inter-process communication
│   │   └── message_handler.py
│   ├── main.py            # Backend entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Configuration file
│
└── extension/             # VSCode extension
    ├── webview/          # Frontend implementation
    │   ├── panel.ts      # Webview panel
    │   └── types.ts      # TypeScript types
    ├── extension.ts      # Extension entry point
    ├── package.json      # Node.js dependencies
    └── tsconfig.json     # TypeScript config
```

##### Kurulum ve Çalıştırma

1. Python bağımlılıklarını yükleyin:
```bash
cd src/backend
pip install -r requirements.txt
```

2. Backend yapılandırması:
- `.env` dosyasında OpenAI API anahtarını ayarlayın:
```
WORKSPACE_PATH=.
HOST=localhost
PORT=3000
OPENAI_API_KEY=your_api_key_here
```

3. Node.js bağımlılıklarını yükleyin:
```bash
cd src/extension
npm install
npm run compile
```

4. Uygulamayı başlatın:
- Python backend'i başlatın: `python src/backend/main.py`
- VSCode'da F5'e basarak uzantıyı başlatın
- Command Palette'ten (Ctrl+Shift+P) "Open CrewAI Agent" komutunu çalıştırın

##### İletişim Protokolü Örneği

```typescript
// Görev gönderme
{
  "type": "task",
  "content": "Create a new file named example.js",
  "timestamp": 1708871234567
}

// Ajan yanıtı
{
  "type": "agent_response",
  "status": "success",
  "content": "Created file example.js",
  "timestamp": 1708871234568
}
```

### Aşama 2 - Gelişmiş Özellikler
- [ ] Hiyerarşik ajan yönetimi
- [ ] Gerçek zamanlı debug konsolu
- [ ] Otomatik test çerçevesi

## 🤝 Katkıda Bulunma

### Katkı Kuralları
1. `develop` branch'ine PR gönderin
2. Tüm yeni özellikler için test ekleyin
3. Kod still rehberine uyun:
   - Python: PEP8
   - TypeScript: Airbnb Style Guide

### Desteklenen Görevler
- [ ] Çeviri desteği ekleme
- [ ] Yeni ajan tipleri oluşturma
- [ ] Performans optimizasyonları

```

> 📝 **Lisans**: MIT License - Proje detayları ve katkı yönergeleri için [CONTRIBUTING.md](https://github.com/organizasyon/crewai-extension/blob/main/CONTRIBUTING.md) dosyasını inceleyin.
``` 

Bu MD dosyası, projenin tüm kritik yönlerini kapsarken aynı zamanda geliştiricilere net bir yol haritası sunmayı hedefler. Her bölüm detaylandırılabilir ve proje ilerledikçe güncellenmelidir.
