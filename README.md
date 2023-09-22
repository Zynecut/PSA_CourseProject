# course_project_PSA
Code for the course project in Power System Analysis (TET4205)

Firstly we are going to make som scripts for the Newton Raphson Method (NRLF).
The we are going to incorporate DLF, FDLF and CDLF.


### Unngår å commite alle filer, som venv.
.gitignore sørger for at det som er spesifisert inne i filen ikke blir commited

### Hvordan clone fra github!
kopier linken
> https://github.com/Zynecut/PSA_CourseProject.git
i cmd, beveg deg til der du vil legge filen, gjerne under:
> C:\Users\dittPCnavn\dinmappe
Når du da er inne i dinmappe, skriver du:
> git clone https://github.com/Zynecut/PSA_CourseProject.git
da blir den clonet til dinmappe.


### Hvordan lage virtual envirement 
Dette er noe du burde ha lokalt i din egen mappe. Som du kanskje har sett 
> python -m venv venv
For å gå inn i venv
> venv\Scripts\activate.bat
For å gå ut av venv
> venv\Scripts\deactivate.bat
Disse funksjonene går ut ifra at du bruker terminalen cmd, da de er litt annerledes i Powershell eller de andre.

### Hvordan pushe til github:
Skriv i commandline:
```
git add .
git commit -m "Skriv her hva du endret"
git push
```

### Some basic Git commands are:
```
git status
git add
git commit
git push
```

### Hvis du commiter "venv", fjern det ved å skrive:
> git rm -r --cached venv/ -f
I command line, venv/ er det du fjerner her, for så å pushe til github på nytt.