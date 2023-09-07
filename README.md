# keyword_scraping

'''text
Main thread
   |
   v
SiteGroup thread
   |
   v
Fetch main page thread
   |
   v
Create child sites thread
   |
   v
Start child threads
   |
   v
Child threads (running in parallel)
   |
   v
Wait for main page thread
   |
   v
Wait for child threads
'''