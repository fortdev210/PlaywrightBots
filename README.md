# Setup

```bash
git git@gitlab.com:or/repo.git
cd obpharma

# Create a virtualenv here named venv (strongly suggested)
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt
```
## Setup Hook

Check the hooks directory.

`pre-commit` is hook will be run before commit was applied
`post-commit` is hook will be run after commit was applied

To setup these hook

```
cd <top folder contains this repository>

cd .git/hooks

# add pre-commit hook
ln -s ../../hooks/pre-commit
```

## Run

`python order_status_buyproxies.py 0 20`
