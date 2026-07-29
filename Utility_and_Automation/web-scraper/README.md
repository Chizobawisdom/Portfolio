
This project is a lightweight web-scraping tool that uses 'Selenium' to automatically collect football news headlines, subtitles, and article links from  
''https://www.thesun.co.uk/sport/football/''

It runs in 'headless mode', meaning it performs the scraping process without opening a visible browser window—ideal for automation and background execution.
This script is part of my utilities collection for 'automation, data extraction, and workflow optimisation.

---

What the Script Does

- Launches a headless Chrome browser using Selenium  
- Visits The Sun's Football page  
- Identifies article teaser blocks using XPath  
- Extracts:
  - 'Title'  
  - 'Subtitle'  
  - 'Article Link'
- Cleans and stores the results in a Pandas DataFrame  
- Automatically names the output file using the 'current date'  
- Saves the dataset as a CSV in the same directory as the script  
- Closes browser session gracefully  

---

Tools & Technologies

- Python 3.x
- Selenium WebDriver
- ChromeDriver
- Pandas
- datetime
- OS/sys modules
