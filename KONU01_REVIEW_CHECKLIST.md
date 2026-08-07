# Konu 01 Manual Review Checklist

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then check:

- [ ] `KONU 01` badge and title render correctly.
- [ ] Sidebar shows Topic 01 and text scale control.
- [ ] `%100`, `%110`, `%120`, `%130` scales do not create double scaling or clipping.
- [ ] Student data table shows 8 observations and 4 analytical variables.
- [ ] Variable-type classification feedback updates correctly.
- [ ] Measurement-level classification feedback updates correctly.
- [ ] Cross-sectional chart has **X: Öğrenci** and **Y: Sınav puanı (puan)**.
- [ ] Time-series chart has **X: Ay** and **Y: Fiyat endeksi (endeks puanı)**.
- [ ] No graph is present without explicit X and Y axis names.
- [ ] Data-source classification updates correctly.
- [ ] Descriptive/inference classification updates correctly.
- [ ] Sample-size slider changes `n` but does not claim that larger samples automatically remove selection bias.
- [ ] Ethics scenarios show the intended issue.
- [ ] `Cevabı göster / Cevabı gizle` works.
- [ ] `Yeni soru` changes the question and closes the previous answer.
- [ ] Changing text scale does not change the current question.
- [ ] No legend, label, card, table, or button overflows at `%130`.
- [ ] Narrow browser width remains usable.
- [ ] Browser console / Streamlit terminal shows no traceback.
