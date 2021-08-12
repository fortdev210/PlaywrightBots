# PlayWright Bots


## Setup

```bash
git git@github.com:STLPROINC/PlaywrightBots.git
cd PlaywrightBots

virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

Install playwright browsers

This is for Mac osx, for other please follow this link https://playwright.dev/python/docs/installation/
```bash
pip install playwright
PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers python -m playwright install
```

`pre-commit` setup

```bash
pre-commit install
```

Copy file `.env.example` to `.env` and change to your credentials

```bash
cp .env.example .env
```

## Add logs directories

```bash
mkdir -p logs/walmart/
mkdir -p logs/homedepot/
```


## Run

`python walmart/wm_order_status_buyproxies.py 0 20`


## How to work on this project

### Source code structure

1. `contants`: all constant classes
2. `homedepot`: all HomeDepot bots
3. `walmart`: all Walmart bots
4. `libs`: all needed libraries, customized code

# Start Walmart scraper

## Start Walmart product scraper
- Run: 
  
  `python walmart/product_scraper.py active_status(0 or 1) start_range end_range`
  
- Example 
  
`python walmart/product_scraper.py 0 0 20`

## Start Walmart category detail scraper
- Run: 
  
  `python walmart/category_scraper.py start_range end_range`
  
- Example 
  
`python walmart/category_scraper.py 0 20`
