Herkese merhaba bu Python scripti, Azure DevOps üzerinde belirli bir proje için son iki haftada çalıştırılan pipeline'ların maliyetini ve başarı/başarısızlık oranlarını hesaplamak ve görselleştirmek için tasarlanmıştır. Göreselleştirmek için matplotlib.pyplot kullanılmıştır. Kısacası Azure DevOps pipeline'larının performansı ve maliyeti hakkında bilgi sağlamak ve bunları görselleştirmek amacıyla kullanılır. Aşağıdaki adımlar script içerisinde uygulanmaktadır.

  -  Azure DevOps organizasyonundaki pipeline'ları ve bu pipeline'ların çalıştırma verilerini almak için API'ye istekte bulunur.
  -  Script, son iki hafta içinde çalıştırılan pipeline'ların süresini dakika cinsinden hesaplar.
  -  Her bir pipeline çalıştırması için Microsoft tarafından barındırılan bir aracı kullanıldığında, toplam sürenin belirli bir eşiği (örneğin, 1800 dakika) aşması durumunda pipeline çalıştırmaları için bir maliyet hesaplar. Eşiğin aşılmadığı sürelerde maliyet hesaplanmaz.
  -  Script, çalıştırılan pipeline'ların kaçının başarılı ve kaçının başarısız olduğunu sayar ve bu oranları hesaplar.
  -  Çalıştırma verilerini tarih bazında gruplar ve bir çubuk grafikle gösterir, böylece son iki haftadaki pipeline çalıştırma sıklığını görselleştirir.
  -  Son olarak, toplam pipeline süresini, bu süre zarfında oluşan toplam maliyeti ve başarısız pipeline çalıştırmalarının toplam maliyetini özetler.

