Giffgaff Scraper
================

Logs into Giffgaff, gets your balance / receipts

Installation
------------

Install into a local venv::

    python3 -m venv .
    ./bin/pip install -e .

Then to get your current balance information::

    ./bin/scrapegaff (my_username) balance

To fill a directory full of VAT receipts::

    ./bin/scrapegaff (my_username) receipts
