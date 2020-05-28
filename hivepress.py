"""
Value add is to get a book in 3

Three clicks and a date range posts are in a print

Title=Tags
Author=Acct

Module pages:
https://pypi.org/project/EbookLib/
https://pyfpdf.readthedocs.io/en/latest/index.html
"""

from fpdf import FPDF

from beem import Hive
from beem.comment import Comment
from beem.exceptions import ContentDoesNotExistsException

from beem.nodelist import NodeList
from beem.account import Account
from bs4 import BeautifulSoup

import re

nodelist = NodeList()
nodelist.update_nodes()
nodes = nodelist.get_nodes(hive=True)
hive = Hive(node=nodes)

post_list= {}

'''
The PDF class is from https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html#minimal-example
'''

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        
        #self.set_draw_color(0, 80, 180)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(0)
        # Page number
        self.cell(0, 50, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def cover(self, bookname):
        self.add_page()
        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', 'B', 35)
        self.cell(0, 6, bookname, 0, 1, 'L', 1)

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(255, 255, 255)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name, img):
        # self.image(img)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0)
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        name = name.replace(u"\u2019", "'").replace(u"\u1110", "").replace(u"\u1111", "").replace(u"\u1112", "").replace(u"\u1113", "")
        name = name.replace(u"\u1110", "")
        name = name.replace(u"\u1111", "")
        name = name.replace(u"\u1112", "")
        name = name.replace(u"\u1113", "")
        self.multi_cell(0, 5, name)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0,5,name)

    def print_chapter(self, num, title, name, img):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name, img)

"""
Get book info
"""

print("Enter your hive username: ")
account = input()
print("Enter the title of your book: ")
title = input()
print("Enter a tagline to describe your book: ")
tagline = input()
print("How many posts would you like pressed? ")
max_posts = int(input())
acct = Account(account, blockchain_instance=hive)
count=-1

# save FPDF() class into a  
# variable pdf 
pdf = PDF() 
pdf.set_title(title)
pdf.set_author(account) 
pdf.cover(title)
for i in map(Comment, acct.history_reverse(only_ops=["comment"])):
    if i.permlink in post_list:
        continue
    try:
        i.refresh()
    except ContentDoesNotExistsException:
        continue
    post_list[i.permlink] = 1
    if not i.is_comment():
        
        if len(i.title) < 30:
            if 'POEM' in i.title: 
                count+=1
                i.title.replace("POEM: ","")
                print("processing... " +  str(i.title) + " ( " + str(count+1) + " of " + str(max_posts) + " )")
                text_only = BeautifulSoup(i.body, 'html.parser')
                link = text_only.get_text().split("(")
                try:
                    link = link[1] 
                    the_link = link.replace(")","")
                    # print("link: " + str(the_link)) 
                    if not the_link.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webm', '.tiff')):
                        the_link=''
                except:
                    the_link=''
                
                pdf.print_chapter(count+1, str(i.title), text_only.get_text(), the_link)
                
        if count == max_posts-1:
            break
filename = title + "_by_" + account + ".pdf"
pdf.output(filename, 'F')
