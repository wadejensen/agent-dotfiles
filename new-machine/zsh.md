Install Oh My zsh

Install plugins:
* git
* zsh-autosuggestions

Setup aliases

Use [.zshrc](./.zshrc) as a template, adding in an existing entries in .zshrc which are likely intentional customisations from the default.

## Secrets

Secrets and API keys do not belong in `.zshrc`.
Allowing agents to read and edit `.zshrc` is too useful.

Put them in `~/.secrets/env` instead, and lock it down:

```bash
mkdir -p ~/.secrets && chmod 700 ~/.secrets
touch ~/.secrets/env && chmod 600 ~/.secrets/env
```
