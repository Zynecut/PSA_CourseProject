# Course Project - Load Flow Analysis
This github page is the collection of numerour algorithms used to convey load flow studies, for the course project in Power System Analysis (TET4205). 

## Getting started
To get a local copy of this project up and running, follow these steps:

### Prerequisites
Make sure you have Git installed on your machine. If not, you can download and install it from [Git Downloads](https://git-scm.com/downloads).

### Cloning the Repository

Open your terminal or command prompt and navigate to the directory where you want to store the project.

```bash
# Navigate by using:
cd YourRepository
# Clone the repository to your local machine
git clone https://github.com/YourUsername/YourRepository.git
```
### How to clone this project from GitHub!
Copy the link `https://github.com/Zynecut/PSA_CourseProject.git` to your clipboard. In the command line, navigate to your desired location, e.g., `C:\Users\yourPCname\yourfolder`. Once in your folder, execute:
```bash
git clone https://github.com/Zynecut/PSA_CourseProject.git
```
This will clone the repository into your folder. You should now have a local copy of the project on your machine.

### Create a virtual environment
A virtual environment is a useful place to download any libraries, so that they're contained within the given project. This must be in the same diectory/folder as the project:
```bash
# Create the virtual environment in the terminal:
python -m venv venv

# To activate the virtual environment:
venv\Scripts\activate.bat
```
These commands assume the use of the cmd terminal; syntax may vary for PowerShell or other terminals.
### Install Dependencies
Install all required libraries needed for this project by typing the following in the terminal:
```bash
pip install -r requirements.txt
# requirements.txt is a collection what is needed to run the code.
```



## How to navigate code
The numerical methods that are implemented are:
- [Newton Raphson Load Flow](NRLF.py)
- [Decoupled Load Flow](DLF.py) 
- [Fast Decoupeld Load Flow](FDLF.py)
- [DC Power Flow](DCPF.py)

All these algorithms can either be run one by one in their respective files, or run them all in one single Jupyter Notebook [main](main.ipynb) file.

The [Functions](functions.py) file contains all the background functions that are used in the four methods. This file is quite comprehensive, so proceed with caution.

### Input format 
The code inputs CSV files, so make sure to save any new data files for bus data and line data as TWO separate .csv files. We use CSV to avoid utilizing the pandas library, as this library complicates debugging with an excessive output. 

The system that this algorithm is built upon is the 5 bus system: ***Stagg's Test System***. The csv files containing the data for these files, is placed under `./files/given_network/`. Here you can find line data with and without operating capacitances, and bus data with `Slack Bus No. 1`, with and without reactive loads, and `Slack Bus No. 2`. 

### Output format
All the functions will at the current version give an output that contains the values wanted, but given in latex format. At least when it comes to Tables. What is also given is the number of iterations the method used, runtime and `Active and reactive loss`.



## Useful command tips
.gitignore ensures that specified files inside the project are not committed.
### How to push to GitHub
In the command line:
```bash
git add .
git commit -m "Describe your changes here"
git push
```
Remember not to push to the main branch but to your own branch. Verify your current branch using:
```bash
# Check branch
git branch

# Make new branch
git branch <new_branch_name>

# Change branch
git checkout <branch_name>

# Delete branch (force delete)
git branch -D <branc_name>
```

### How to pull changes made by others
Run `git pull` to fetch changes from the repository and update your local code. `git pull` combines `git fetch` and `git merge`. If you encounter a merge conflict you can't resolve or decide to abort, use `git merge --abort` to return the branch to its state before pulling.

### Git pull from a branch in GitHub to a local branch
Replace `{github_branch}` with the branch you want to pull from and `{local_branch}` with your local branch name.
```bash
git pull origin {github_branch}:{local_branch}
```

### If you accidentally commit "venv," remove it by running:
```bash
git rm -r --cached venv/ -f
```
In the command line, `venv/` is what you're removing, then push to GitHub again. This is not nessecary

### Remember to add the Jupyter extension in the venv (our environment)

### Cancelling a Commit in Git
To cancel a commit in Git, you can use several methods depending on the situation. Here are some common scenarios and how to cancel commits in each case:

1. Cancel the Last Commit (Local Only):
   - To cancel the commit but keep the changes in your working directory:
     ```bash
     git reset --soft HEAD~1
     ```
   - To cancel the commit and unstage the changes:
     ```bash
     git reset --mixed HEAD~1
     ```

2. Cancel a Commit and Discard Changes (Local Only):
   - To completely discard both the commit and the changes:
     ```bash
     git reset --hard HEAD~1
     ```
   Be cautious, as this permanently discards the changes.

3. Cancel a Commit and Create a New One:
   - To cancel a commit and create a new one with different changes:
     ```bash
     git reset --hard HEAD~2
     ```

4. Cancel a Commit and Push Changes (Remote Repository):
   - If you've pushed the commit to a remote repository, use `git revert`:
     ```bash
     git revert <commit-hash>
     ```
   Then, push the new commit to the remote repository.

Remember to replace `<commit-hash>` with the actual hash of the commit you want to cancel. Exercise caution when canceling commits, especially in a shared repository. These adjustments aim to improve readability and maintain a consistent style throughout the document. Feel free to customize further based on your preferences.