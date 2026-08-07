# İKT 207 İstatistik — Etkileşimli Ders Uygulaması

İkinci sınıf iktisat öğrencileri için Streamlit tabanlı Türkçe istatistik uygulaması.
Ders notları içerik, terminoloji, notasyon, matematiksel seviye ve konu sırası açısından bağlayıcı kaynaktır.

## Current scope

- Application foundation
- Topic 01: Veri ve İstatistiğe Giriş
- Shared text scaling (%100–130)
- Shared question component
- Mandatory X/Y axis-title chart renderer
- pytest + Streamlit AppTest
- GitHub Actions CI

## Local setup (Windows PowerShell)

```powershell
cd E:\Github\istatistik
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Validate

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py core topics tests
git diff --check
```

## Graph standard

Every data chart must have explicit, human-readable X and Y axis titles. Topic modules may not call `st.plotly_chart()` directly; they use the shared `render_plotly()` component.

## Development sequence

- `feature/konu01-app-foundation`
- `feature/konu02-04`
- `feature/konu05-07`
- `feature/konu08-10`
- `feature/konu11-12`
- `fix/final-application-audit`
