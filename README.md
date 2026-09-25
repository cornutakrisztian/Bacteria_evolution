# Evolúciós Szimulátor

Ez a projekt egy baktérium evolúciós szimulátor Pythonban, Tkinter grafikus felülettel.  
A szimuláció modellezi a mozgást, táplálkozást, szaporodást, mutációt, természetes szelekciót és a gének hosszú távú fejlődését.

A jobb oldali vezérlőpanel segítségével a futó szimuláció különböző paraméterei módosíthatók.

## Fő funkciók

- Baktériumok genetikai tulajdonságokkal:
  - sebesség
  - méret
  - érzékelési távolság (sense)
  - párosodási hajlam
  - emésztési hatékonyság
- Mutáció és természetes szelekció
- Étel megjelenése és elfogyasztása
- Szaporodás genetikai öröklődéssel
- Energia- és életkor rendszer
- Valós idejű statisztikák
- Grafikonok a gének hosszú távú alakulásáról

## Vezérlők és gombok

### Szünet / Folytatás
**Gomb:** „Szünet” / „Folytatás”  
Megállítja vagy újraindítja a szimulációt. Szünetben a baktériumok nem mozognak és nem fejlődnek.

### Gyorsítás
**Gomb:** „Gyorsítás”  
Megduplázza a szimuláció sebességét. Maximum 16× sebességig.

### Lassítás
**Gomb:** „Lassítás”  
Felezi a szimuláció sebességét. Minimum 0.25× sebességig.

### Újragenerálás
**Gomb:** „Újragenerálás”  
Teljes reset:
- új populáció
- új étel
- statisztikák törlése
- grafikonok törlése
- generációszámláló nullázása

### Étel Kínálat csúszka
**Csúszka:** „Étel Kínálat”  
Az étel megjelenési esélyét szabályozza (0–15%).  
Minél magasabb az érték, annál több étel jelenik meg idővel.

### Azonnali ételszórás
**Gomb:** „+ Étel szórása”  
Azonnal 30 ételt ad a pályára (a maximumig).

### Érzékelési sugár megjelenítése
**Jelölőnégyzet:** „Érzékelési sugár (Látótáv)”  
Megjeleníti a baktériumok körül a látótávolságot jelző kört.

### Energia sávok megjelenítése
**Jelölőnégyzet:** „Energiaszintek”  
Kis energiasávot rajzol minden baktérium fölé.

### Evolúciós grafikonok
**Gomb:** „Evolúciós Grafikonok”  
Külön ablakot nyit, amelyben folyamatosan frissülő grafikonok láthatók:
- populáció mérete
- átlagos sebesség
- átlagos méret
- átlagos érzékelési távolság
- átlagos párosodási hajlam
- átlagos emésztési hatékonyság

A grafikonok 0.5 másodpercenként frissülnek.

## A szimuláció működése

### Mozgás
A baktériumok:
- véletlenszerűen mozognak,
- ételt keresnek,
- párt keresnek szaporodáshoz.

### Táplálkozás
Ha a baktérium elég közel kerül az ételhez, elfogyasztja, és energiát nyer az emésztési hatékonysága alapján.

### Szaporodás
Két baktérium akkor szaporodik, ha:
- mindkettőnek elég energiája van,
- nincs szaporodási cooldown,
- közel vannak egymáshoz.

A gyermek minden gént 50–50% eséllyel örököl, majd mutáció történhet.

### Mutáció
Minden gén kis eséllyel módosulhat a mutációs erősség alapján.

### Halál
A baktérium meghal, ha:
- elfogy az energiája,
- eléri a maximális életkort.

### Automatikus újrakezdés
Ha a populáció teljesen kihal, új kezdő populáció jön létre.

Python 3.x és Tkinter szükséges (alapból része a legtöbb Python telepítésnek).

## Szerző

cornutakrisztian

