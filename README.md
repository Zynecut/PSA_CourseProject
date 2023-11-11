# course_project_PSA
Code for the course project in Power System Analysis (TET4205)

### Specify format for excel inputs
The code inputs CSV files, so make sure to save your data files for bus data and line data as TWO separate .csv files. We use CSV to avoid utilizing the pandas library, as it can complicate debugging with excessive output.

## How to navigate code
## How to download and run

### Avoid committing all files, such as venv.
.gitignore ensures that specified files inside the file are not committed.

### How to clone from GitHub!
Copy the link `https://github.com/Zynecut/PSA_CourseProject.git` to your clipboard. In the command line, navigate to your desired location, e.g., `C:\Users\yourPCname\yourfolder`. Once in your folder, execute:
```bash
git clone https://github.com/Zynecut/PSA_CourseProject.git
```
This will clone the repository into your folder.

### How to create a virtual environment
This is something you should have locally in your own folder:
```bash
python -m venv venv
```
To activate the virtual environment:
```bash
venv\Scripts\activate.bat
```
To deactivate the virtual environment:
```bash
venv\Scripts\deactivate.bat
```
These commands assume the use of the cmd terminal; syntax may vary for PowerShell or other terminals.

### How to install all required libraries
Here's how you can install all the libraries needed for this project:
```bash
pip install -r requirements.txt
```

### How to push to GitHub
In the command line:
```bash
git add .
git commit -m "Describe your changes here"
git push
```
Remember not to push to the main branch but to your own branch. Verify your current branch using:
```bash
git checkout branch_name    # Change branch
```

### How to pull changes made by others
Run `git pull` to fetch changes from the repository and update your local code. `Git pull` combines `git fetch` and `git merge`. If you encounter a merge conflict you can't resolve or decide to abort, use `git merge --abort` to return the branch to its state before pulling.

### Git pull from a branch in GitHub to a local branch
Replace `{github_branch}` with the branch you want to pull from and `{local_branch}` with your local branch name.
```bash
git pull origin {github_branch}:{local_branch}
```

### Some basic Git commands
```bash
git status
git add
git commit
git push
```

### If you accidentally commit "venv," remove it by running:
```bash
git rm -r --cached venv/ -f
```
In the command line, `venv/` is what you're removing, then push to GitHub again.

### Remember to add the Jupyter extension in the venv (our environment)

## Cancelling a Commit in Git
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

Remember to replace `<commit-hash>` with the actual hash of the commit you want to cancel. Exercise caution when canceling commits, especially in a shared repository.
```

These adjustments aim to improve readability and maintain a consistent style throughout the document. Feel free to customize further based on your preferences.