# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced

# History file maxlength
export SAVEHIST=999999999
# History search (in-memory) lookback
export HISTSIZE=100000

plugins=(git zsh-autosuggestions)

source $ZSH/oh-my-zsh.sh

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=2"

## Aliases

# zsh
alias .z="source ~/.zshrc"

# Git
alias gs="git status"
# enable -uno in large repos
#alias gs="git status -uno"
alias gc="git commit -m"
alias gp="git push"
alias gpl="git pull"
alias gpf="git push -f --force-with-lease"
alias gcm="git checkout master"
alias gcb="git checkout -b"
alias gd="git diff"
alias gdc="git diff --cached"
alias ga="git add"
alias gct="git checkout"
alias gplrm="git pull --rebase origin master"
alias gpom="git pull origin master"

alias gb="git branch --show-current"

function gsb() {
  if [[ "$#" -lt 1 ]]; then
    echo 'No branch specified' >/dev/stderr
    return 1;
  fi
  branch="$1"
  git fetch origin "${branch}";
  git checkout "${branch}";
  git pull origin "${branch}";
}

export ANSIBLE_HOST_KEY_CHECKING=False

export PATH="$PATH:/usr/local/bin"
export PATH="$HOME/.local/bin:$PATH"

# Never export secrets from ~/.zshrc directly
[[ -f ~/.secrets/env ]] && source ~/.secrets/env
