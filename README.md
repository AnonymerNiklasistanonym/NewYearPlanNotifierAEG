# NewYearPlanNotifierAEG

Python 3 script that scraps the website of the school and recognizes when a new year plan was published.

**Works also on Python 2, but on my Raspberry Pie 3 it made problems. That means use Python 3 if you can instead of Python 2.**



## How to use it?

Every time you execute this program it will say you in the console if the information have changed and displays the new text with links to the current year plan of this website:

http://www.aeg-boeblingen.de/index.php/aktuelles/stundenplan

## How to get email notifications?

If you also want to get email notifications each time the script recognizes that a change has happened you can use the [SendGmailSimplified](https://github.com/AnonymerNiklasistanonym/SendGmailSimplified) submodule:

1. Therefore follow first the instructions in the [README.md](https://github.com/AnonymerNiklasistanonym/SendGmailSimplified/blob/master/README.md) file of the submodule.
2. Set now in the [script.py](script.py) `USE_GMAIL = True`
3. And insert here your email address where the notification should be send:
   `RECIPIENTS = ["yourEmailAdress@sonstwas.com", "onemore@gmail.com"]`
4. If you want you can use it like me with the cron scheduler to specific times for changes (look for more [here](https://www.raspberrypi.org/documentation/linux/usage/cron.md) and [here](https://github.com/AnonymerNiklasistanonym/RaspiForBeginners)).