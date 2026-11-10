Setup a new machine with Github, git, and ssh keys.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch master
```

```bash
ssh-keygen -t ed25519 -C "you@example.com" -f ~/.ssh/id_ed25519
```

```bash
cat >> ~/.ssh/config <<'EOF'
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
EOF
chmod 600 ~/.ssh/config
```

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

```bash
brew install gh
gh auth login
```

Manually upload SSH key.
```bash
gh ssh-key add ~/.ssh/id_ed25519.pub --title "macbook"
```

# Test the connection
```bash
ssh -T git@github.com
```
You should see Hi <username>! You've successfully authenticated....
