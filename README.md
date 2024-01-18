# magit

This is my minimal recreation of git, currently supports creating a repository, adding files to staging, 
commiting, creating/switching branches, merging, log and diff. This is only used for learning puposes about the internals of git and is no way should be used for production.

## How to use 

Don't

## Key differences b/w git and magit:

### Staging Area 
Git: Uses an 'index' file to track changes that are to be committed. This is a binary file that represents the state of the working directory.

Magit: Manages a 'staged' directory. Each file to be committed is stored here with its content hashed. It's more like a collection of files rather than a  file. 

This has been done for simplicity as git uses a tree structure which is a bit more complicated to implement.

#### Git's Tree Structure
Blob Objects: The contents of each file are stored as blob objects.

Tree Objects: Git uses "tree" objects to represent the structure of directories, it contains pointers to blob objects.

Commits Point to Trees: Each commit in Git points to a tree object

#### Magit's Approach
Direct Staging: when you add a file in magit, the content of the file is stored directly in the staged directory. 

Commit Structure: the commit object itself stores the changes. This is different from Git wwhere a commit points to a tree object representing the repository's directory structure and changes
Thus magits approach is not efficient for large file sizes 


This has been only done for simplicity, as I am not going to implement remote tracking, tags. 

### Merging 

Right now merging does not take into account for merge conflicts, nor does it fix divergent branches.



## Todo:
- [ ] handle uncommited changes when switching branches
- [ ] rebase 



## Resources 
https://www.youtube.com/watch?v=fCtZWGhQBvo
