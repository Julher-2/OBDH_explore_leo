How to use git:

Cloning repository: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository

Before starting to work oon your alway make sure to do command:

    git pull
  
or sync through vscode. This will make sure you have the latest version of the code.

When you want to upload your code:

    git add .
  
    git commit -m "message"
  
    git push
  
or you can do it throught the menu in vs code. You can check the repository to make sure it was uploaded correctly :)

Branches:

  When working you can switch branch using
  
    git switch name_of_branch

  New branches can be made in the repository or by using 
  
    git branch name_of_branch

  New branches are identical to main when you copy them and allow people to work on there own version of the code. Branches can then be merged to main through the repository her on git.

  You can see what branch you are in using
  
    git status
