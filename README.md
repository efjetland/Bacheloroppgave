# Bacheloroppgave
### System for logging av hjertedata

Mappen datalogger inneholder programkoden og bildefiler for knapper.
Filen [app.py](https://github.com/efjetland/Bacheloroppgave/blob/master/datalogger/app.py) inneholder selve programmet med oppsett av grafisk brukergrensesnitt og lagring av filer.
Filen [bluetooth.py](https://github.com/efjetland/Bacheloroppgave/blob/master/datalogger/bluetooth.py) inneholder klasser som brukes for å kommunisere via Bluetooth Low Energy(BLE), det blir laget objekter av disse klassene i [app.py](https://github.com/efjetland/Bacheloroppgave/blob/master/datalogger/app.py).
Filen [hrv.py](https://github.com/efjetland/Bacheloroppgave/blob/master/datalogger/hrv.py) inneholder funksjoner for å kalkulere hjerteratevariablilitet ut i fra en serie med RR-intervaller og disse funskjonene brukes av [app.py](https://github.com/efjetland/Bacheloroppgave/blob/master/datalogger/app.py).

I mappen [images](https://github.com/efjetland/Bacheloroppgave/tree/master/datalogger/images) finnes bildefilene til alle knappene som blir brukt i programmet.
