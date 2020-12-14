import os
import sqlite3
import smtplib
import requests
from bs4 import BeautifulSoup
import datetime

def insert_paper(entry):
    with conn:
        c.execute("INSERT INTO paper VALUES (:title, :citation)", {'title': entry[0], 'citation': entry[1]})

def get_citation(title):
    c.execute("SELECT citation FROM paper WHERE title=:title", {'title': title})
    return c.fetchone()

def update_citation(entry):
    with conn:
        c.execute("""UPDATE paper SET citation = :citation
                    WHERE title = :title""",
                  {'title': entry[0], 'citation': entry[1]})

def citation_sum():
    c.execute("SELECT SUM(citation) FROM paper")
    result=c.fetchone()[0]
    if result:
        return result
    else:
        return 0

def paper_sum():
    c.execute("SELECT COUNT(*) FROM paper")
    return c.fetchone()[0]

conn = sqlite3.connect('paper_citation.db')
#for development: conn = sqlite3.connect(':memory:')    

c = conn.cursor()

#only execute for the first time to create table
'''
c.execute("""CREATE TABLE paper (
            title text,
            citation integer
            )""")
conn.commit()
'''

html_file=requests.get('https://scholar.google.com/citations?user=Mzu7dWYAAAAJ&hl=en&oi=ao').text #use your own google scholar url
soup=BeautifulSoup(html_file,'lxml')

paper_list=[]
for article in soup.find_all('tr', class_="gsc_a_tr"):
    title=article.find('a', class_='gsc_a_at').text
    citation=article.find('td', class_='gsc_a_c').text
    if citation == '':
        citation = 0
    else:
        citation = int(citation)
    paper_list.append((title,citation))

subject=''
body=''
old_paper_sum=paper_sum()
old_citation_sum=citation_sum()
new_paper_sum=len(paper_list)
new_citation_sum=sum([paper[1] for paper in paper_list])
paper_diff=new_paper_sum-old_paper_sum
citation_diff=new_citation_sum-old_citation_sum
date_cur=datetime.datetime.today().strftime("%b %d, %Y")

#pre-create a "checkdate.txt" file in the folder
with open("checkdate.txt", "r+") as f:
    date_last = f.read()
    f.seek(0)
    f.write(date_cur)
    f.truncate()

if paper_diff==0 and citation_diff==0:
    diff_str=f' (no changes since {date_last})'
elif paper_diff==0:
    diff_str=f' (citation changes by {citation_diff} since {date_last})'
elif citation_diff==0:
    diff_str=f' (publication changes by {paper_diff} since {date_last})'
else:
    diff_str=f' (publication changes by {paper_diff} and citation changes by {citation_diff} since {date_last})'
subject='Your google scholar citation update'+diff_str
body=body+f'Total publications: {new_paper_sum} (change by {paper_diff})\n'
body=body+f'Total citations: {new_citation_sum} (change by {citation_diff})\n\n'
for paper in paper_list:
    title=paper[0]
    new_citation=paper[1]
    old_citation=get_citation(title)
    if old_citation:
        if new_citation>old_citation[0]:
            note=f'Citation increases by {new_citation-old_citation[0]}'
            update_citation(paper)
        elif new_citation>old_citation[0]:
            note=f'Citation decreases by {old_citation[0]-new_citation}'
            update_citation(paper)
        else:
            note=None
    else:
        note=f'This is a new publication'
        insert_paper(paper)
    body=body+f'Title: {title}\n'
    if new_citation == 0 or new_citation ==1:
        body=body+f'Cited by {new_citation} time\n'
    else:
        body=body+f'Cited by {new_citation} times\n'
    if note:
        body=body+f'Note: {note}\n'
    body=body+'\n' 

#save the senstive information as your environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
    
    msg=f'Subject: {subject}\n\n{body}'
    smtp.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL_ADDRESS, msg) #specify the receiver email address 

#use cron or anacron to push the citation update to your email periodically
