🐍 Python Web Editörü
Modern ve kullanıcı dostu arayüze sahip, tarayıcı tabanlı bir Python kod editörü. React ile geliştirilmiş olup, gerçek zamanlı kod yürütme ve sonuç görüntüleme özelliklerine sahiptir.

https://img.shields.io/badge/React-18.2.0-blue https://img.shields.io/badge/Python-3.10%252B-yellow https://img.shields.io/badge/License-MIT-green

✨ Özellikler
🎨 Modern ve kullanıcı dostu arayüz

⚡ Gerçek zamanlı kod yürütme

📁 Kod dosyalarını kaydetme ve yükleme

🎯 Söz dizimi vurgulama (Syntax Highlighting)

📱 Tamamen duyarlı (responsive) tasarım

🔄 Otomatik kod tamamlama önerileri

📊 Çalışma zamanı istatistikleri

🌙 Koyu/Açık tema desteği



![kayıt ekranı](https://github.com/user-attachments/assets/444d30da-d600-40bb-a53e-03f2cab90dfd)

![giriş ekranı](https://github.com/user-attachments/assets/4a3f5294-45e9-446b-9f8c-d88179702dc2)

![editor](https://github.com/user-attachments/assets/8bf46ae5-b9e0-4cea-ae4f-cdaf51d01221)



🚀 Hızlı Başlangıç
Ön Koşullar
Node.js (v14 veya üzeri)

npm veya yarn

Kurulum
Depoyu klonlayın:

bash
git clone https://github.com/kullanici-adi/python-web-editor.git
cd python-web-editor
Bağımlılıkları yükleyin:

bash
npm install
# veya
yarn install
Geliştirme sunucusunu başlatın:

bash
npm start
# veya
yarn start
Tarayıcınızda http://localhost:3000 adresine gidin.

🛠️ Kullanım
Sol taraftaki editör alanına Python kodunuzu yazın.

"Çalıştır" butonuna tıklayarak kodunuzu yürütün.

Sağ taraftaki panelde kodunuzun çıktısını görün.

Dosya menüsünden kodunuzu kaydedebilir veya daha önce kaydettiğiniz dosyaları açabilirsiniz.

📦 Proje Yapısı
text
src/
├── components/          # React bileşenleri
│   ├── Editor/         # Kod editörü bileşeni
│   ├── Output/         # Çıktı görüntüleme bileşeni
│   ├── Header/         # Üst navigasyon bileşeni
│   └── Sidebar/        # Yan menü bileşeni
├── hooks/              # Özel React hook'ları
├── utils/              # Yardımcı fonksiyonlar
├── styles/             # Stil dosyaları
└── App.js              # Ana uygulama bileşeni
🔧 Özelleştirme
Tema Değiştirme
Uygulama styles/themes.css dosyasından kolayca özelleştirilebilir tema desteğine sahiptir. Yeni bir tema eklemek için:

css
:root[data-theme="yeni-tema"] {
  --primary-color: #your-color;
  --background-color: #your-background;
  /* Diğer değişkenler... */
}
Dil Desteği Eklemek
Editöre yeni bir programlama dili desteği eklemek için:

utils/languages.js dosyasına dil tanımını ekleyin

CodeMirror veya kullandığınız editör kütüphanesine dil modülünü ekleyin

🌐 Canlı Demo
Projenin canlı demosuna buradan ulaşabilirsiniz.

🤝 Katkıda Bulunma
Katkılarınız her zaman welcome! Lütfen katkıda bulunmadan önce:

Fork işlemi yapın

Feature branch'i oluşturun (git checkout -b feature/AmazingFeature)

Değişikliklerinizi commit edin (git commit -m 'Add some AmazingFeature')

Branch'inizi push edin (git push origin feature/AmazingFeature)

Pull Request oluşturun

📝 Lisans
Bu proje MIT lisansı altında lisanslanmıştır. Detaylı bilgi için LICENSE dosyasını inceleyebilirsiniz.

👨‍💻 Geliştiriciler
Sem Samsum

🙏 Teşekkürler
React ekibine harika kütüphane için

CodeMirror ekibine mükemmel editör için

Tüm katkıda bulunanlara

