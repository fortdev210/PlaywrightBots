from libs.bot_manager import BotManager

Bot = BotManager(use_chrome=True)
Bot.start_playwright()
Bot.run_browser()
Bot.open_new_page()
Bot.go_to_link('https://quora.com')
