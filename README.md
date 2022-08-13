# PriceNotifier
This is a real business solution, implemented to track prices on competitor's websites.

Technologies/libs used:
Hosting - Amazon EC2 micro server
HTML scraping - requests, BeautifulSoup
Database - PostgreSQL
Telegram - python-telegram-bot
Log - logging

Every launch, the parser scrapes links inside 'config/sites.json' file. Pulls an array of items from HTML page, checks with database if the product already exists in it, and if the price changed. If either is true, message is sent to telegram users specified in the database. Logging is also implemented. 

This solution has worked non-stop for the past year, providing my client with immediate updates of his competition. Keeping competitive prices has helped to raise his market share of customers, which(as I was told) resulted in 5 to 15 percent growth of sales margin.

 <!-- sudo crontab set to
*/30 5-20 * * * /bin/python3 /git-projects/PriceNotifier/Run.py >/dev/null 2>&1 -->
