# course_project_PSA
Code for the course project in Power System Analysis (TET4205)


### Specify format for excel inputs.
The code inputs csv files, so make sure to save your data files for bus data and line data as TWO seperate .csv files.
The reason for csv, is that we try to avoid using the pandas library, as it is annoying to debug when pandas gives you 4 million lines of uselessness in the debugger.

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
Du vil ikke pushe til main branch, men til egen branch. Derfor er det viktig at du sjekker hvilken branch du er i.
```
git checkout branch_name    "Change branch"
```


### Hvordan hente ut endringer gjort av andre
Skriv ```git pull``` for å hente ut endringer i repository, for å oppdatere din lokale kode.
Git pull er en kombinasjon av ```git fetch og git merge```. Hvis du får en merge konflikt du ikke kan løse, eller hvis du bestemmer deg for å avslutte sammenslåingen, kan du bruke ```git merge --abort``` for å ta grenen tilbake til der den var i før du pulled.

### Git pull fra en branch i github til lokal branch
Her vil du altså bytte ut {github_branch} med den branchen du vil hente koden fra. Så bytter du {lokal_branch} med navnet på din lokale branch.
```
git pull origin {github_branch}:{lokal_branch}
``` 

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

### Husk å legge til jupityr extension i venv (Vårt environment):


##
To cancel a commit in Git, you can use several methods depending on the situation. Here are some common scenarios and how to cancel commits in each case:

Cancel the Last Commit (Local Only):
If you want to cancel the most recent commit without affecting the remote repository, you can use the git reset command with the --soft or --mixed option.

To cancel the commit but keep the changes in your working directory, you can use:

css
Copy code
```
git reset --soft HEAD~1
```
To cancel the commit and unstage the changes, you can use:

css
Copy code
```
git reset --mixed HEAD~1
```
After executing one of these commands, the last commit will be removed, and the changes will be either in your working directory or staged for a new commit.

Cancel a Commit and Discard Changes (Local Only):
If you want to completely discard both the commit and the changes, you can use the git reset command with the --hard option. Be cautious when using this, as it permanently discards the changes.

css
Copy code
```
git reset --hard HEAD~1
```
This will remove the last commit and all changes associated with it.

Cancel a Commit and Create a New One:
If you want to cancel a commit and create a new one with different changes, you can use git reset to reset the branch and then make new commits with the desired changes.

For example, if you want to cancel the last two commits and start fresh:

css
Copy code
```
git reset --hard HEAD~2
```
Cancel a Commit and Push Changes (Remote Repository):
If you've already pushed the commit to a remote repository and want to cancel it, you should not use git reset as it can lead to issues in a shared environment. Instead, you can create a new commit that undoes the changes made in the commit you want to cancel.

First, use git revert to create a new commit that undoes the changes:

php
Copy code
```
git revert <commit-hash>
```
Then, push the new commit to the remote repository to effectively cancel the previous commit.

Remember to replace <commit-hash> with the actual hash of the commit you want to cancel.

It's important to exercise caution when canceling commits, especially in a shared repository, as it can affect others working on the project. Always communicate with your team when making significant changes to the commit history.