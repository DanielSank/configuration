alias cls='printf "\033c"'

# To get the nice git prompt in bash, copy /usr/lib/git-core/git-sh-prompt
# to /home/<name>/.git-prompt.sh and modify your bashrc with the following
# code. There should already be a case block that looks like "case "$TERM"
# in xterm*|rxvt*) ... "  -- that gets replaced with this block of code.

##### Begin git bash addition
# This file normally lives in /usr/lib/git-core/git-sh-prompt on ubuntu systems
# Copy it into your home directory
if [ -f $HOME/.git-prompt.sh ]; then
        . $HOME/.git-prompt.sh
        #PS1='\u@\h:\w$(__git_ps1 " (%s)")\$ '
        PS1='[\u@\h \W$(__git_ps1 " (%s)")]\$ '
else
    echo "unable to find git PS1 script!"
    __git_ps1 () { true; }
fi

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\$(__git_ps1 \" (%s)\")\a\]$PS1"
    ;;
*)
    ;;
esac
###### End git bash addition
