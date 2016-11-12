```
git config --global status.submoduleSummary true
# Makes status list changes within the submodule

git submodule init
# Checks .gitmodules and updates .git/config accordingly

git submodule update
# Actually updates submodule

git clone --recursive
# Does submodule init and submodule update when cloning

git config diff.submodule log
# Makes diff show the changes in submodules
```
