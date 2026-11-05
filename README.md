# Zarxon AutoTrader — mahalliy MVP

Faqat CSVdan SMA kesishuvini hisoblaydigan demo. Tarmoq, broker ulanishi,
API kaliti, order yuborish yoki avtomatik savdo qatlami yo'q.

Bu 2026-11-06 kuni shu kompyuterda qayta tayyorlangan draft. Boshqa chatdagi
vaqtinchalik draftning aynan nusxasi emas. GitHubga commit yoki push qilinmadi.

## Ishlatish

Python 3.11+ kerak. Tashqi paket o'rnatish talab qilinmaydi.
Terminalni shu papkada oching:

```powershell
python -m zarxon_autotrader
python -m zarxon_autotrader --json
python -m unittest discover -s tests -v
```

Windowsda Python `py` orqali ochilsa, yuqoridagi `python` o'rniga `py -3` yozing.

O'z CSV faylingiz uchun:

```powershell
python -m zarxon_autotrader --csv data/demo.csv --symbol DEMO-XAUUSD --short 3 --long 5 --stop-percent 1 --reward-ratio 2 --decimals 2 --json
```

CSV ustunlari: `timestamp,open,high,low,close,volume`.
Vaqtlar timezone bilan, takrorsiz va o'suvchi bo'lishi kerak. Narxlar musbat,
volume manfiy bo'lmasin; high/low open va closeni qamrab olishi kerak.
Kamida long+1 ta **yakunlangan** sham bering. Dastur sham yopilganini yoki
CSVning bozorga qanchalik yangi ekanini mustaqil tekshirmaydi.

## Natija

BUY/SELL faqat oxirgi ikkita SMA holati o'rtasidagi yangi kesishuvda chiqadi.
Kesishuv bo'lmasa HOLD qaytadi va savdo darajalari berilmaydi.
SL foiz masofasi va TP koeffitsiyenti faqat misol hisobidir.
JSON narxlarni o'nlik aniqligini saqlash uchun matn ko'rinishida beradi.
`demo_only=true`, `execution=disabled` barcha natijalarda mavjud.

Namunadagi tarix va narxlar sun'iy; joriy kotirovka emas. Komissiya, spred,
sirpanish, lot hajmi va strategiya rentabelligi bu MVPda hisoblanmaydi.
Bu paket mavjud Zarxon serveri yoki MT5 signal bridge'iga ulanmagan.

## Ko'rib chiqish uchun

GitHub bazasi 2026-11-06 tekshiruvida:
`Zarxon001/Zarxon_AutoTrader`, main, `c30d9e8d7c18e0ecf182b77d2df5a04191ede7ee`.
Repoda faqat boshlang'ich README mavjud edi. Ushbu draftni kiritishdan oldin
repo holati yana tekshiriladi va alohida commit/push tasdig'i olinadi.
