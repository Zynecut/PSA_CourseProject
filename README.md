# course_project_PSA
Code for the course project in Power System Analysis (TET4205)

Firstly we are going to make som scripts for the Newton Raphson Method (NRLF).
The we are going to incorporate DLF, FDLF and CDLF.

## How to navigate code
## How to download and run

### Unngår å commite alle filer, som venv.
.gitignore sørger for at det som er spesifisert inne i filen ikke blir commited

### Hvordan clone fra github!
kopier linken
```https://github.com/Zynecut/PSA_CourseProject.git```
i cmd, beveg deg til der du vil legge filen, gjerne under:
```C:\Users\dittPCnavn\dinmappe```
Når du da er inne i dinmappe, skriver du:
```git clone https://github.com/Zynecut/PSA_CourseProject.git```
da blir den clonet til dinmappe.


### Hvordan lage virtual envirement 
Dette er noe du burde ha lokalt i din egen mappe. Som du kanskje har sett 
```python -m venv venv```
For å gå inn i venv
```venv\Scripts\activate.bat```
For å gå ut av venv
```venv\Scripts\deactivate.bat```
Disse funksjonene går ut ifra at du bruker terminalen cmd, da de er litt annerledes i Powershell eller de andre.

###
You dont want to push to main, push to developer branch.
```
git checkout branch_name    "Change branch"
```

### Hvordan installere alle libraries du trenger
Her vises hvordan du kan installere alle libraries du trenger for dette prosjektet. 

```
pip install -r requirements.txt
```


### Hvordan pushe til github:
Skriv i commandline:
```
git add .
git commit -m "Skriv her hva du endret"
git push
```

### Hvordan hente ut endringer gjort av andre
Skriv ```git pull``` for å hente ut endringer i repository, for å oppdatere din lokale kode.
Git pull er en kombinasjon av ```git fetch og git merge```. Hvis du får en merge konflikt du ikke kan løse, eller hvis du bestemmer deg for å avslutte sammenslåingen, kan du bruke ```git merge --abort``` for å ta grenen tilbake til der den var i før du pulled.

### Some basic Git commands are:
```
git status
git add
git commit
git push
```

### Hvis du commiter "venv", fjern det ved å skrive:
```
git rm -r --cached venv/ -f
```
I command line, venv/ er det du fjerner her, for så å pushe til github på nytt.


