# Jak wrzucić to portfolio na GitHub (instrukcja PL)

Repo zostało już **zainicjowane lokalnie** i zacommitowane (bez żadnych kluczy API).
Zostały 3 kroki, które musisz zrobić Ty, bo wymagają logowania na Twoje konto GitHub.

## ⚠️ Najpierw o „dostęp tylko z linkiem"
GitHub **nie ma** opcji „repo widoczne tylko z linkiem" (jak np. niepubliczne wideo na YT). Masz 2 realne opcje:
- **Public** — każdy z linkiem otworzy (i repo jest wyszukiwalne). **To standard dla portfolio pod pracę — polecam.** Rekruter klika link i widzi wszystko.
- **Private** — widzą tylko osoby, które zaprosisz imiennie (trzeba znać ich konto GitHub). Mniej wygodne dla aplikacji.

👉 Rekomendacja: **Public**. Kod jest oczyszczony z kluczy, więc nie ma czego się bać.

## Krok 1 — Załóż repo na GitHub
1. Wejdź na https://github.com/new
2. Nazwa: `portfolio` (albo `bartosz-gontarek-portfolio`).
3. Wybierz **Public**. NIE zaznaczaj „Add README" (mamy już swój).
4. Kliknij **Create repository**.

## Krok 2 — Połącz i wypchnij (wklej w terminalu)
W folderze `C:\Users\gonta\portfolio-booksy` otwórz terminal (Git Bash / PowerShell) i wklej
(podmień `TWOJ-LOGIN` na swój login GitHub):
```bash
git remote add origin https://github.com/TWOJ-LOGIN/portfolio.git
git branch -M main
git push -u origin main
```
Przy pierwszym pushu GitHub poprosi o logowanie (otworzy się okno przeglądarki / token).

## Krok 3 — Skopiuj link do formularza
Link `https://github.com/TWOJ-LOGIN/portfolio` wklej w aplikacji Booksy w polu
**„Please share a link to your portfolio (for example, GitHub)"**.

---
**Chcesz, żebym zrobił to za Ciebie?** Mogę zainstalować GitHub CLI (`gh`),
zalogujesz się raz, a ja utworzę repo i wypchnę wszystko jedną komendą. Powiedz słowo.
