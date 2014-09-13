#bib-napper tool, written by jason mars

import os;
import urllib2;
from urllib import FancyURLopener;

os.system("cat *._html_ >> ids.clump; rm *._html_");

final=[];
f=open("ids.clump",'r').readlines();
for i in f:
  if(len(i.split("citation.cfm?id="))>1 and len(i.split("<td colspan=\"1\"><span style=\"padding-left:"))>1):
    tmp=i.split("citation.cfm?id=")[1].split("&")[0];
    if(tmp[len(tmp)-1:]=='\n'): continue;
    final.append(["http://portal.acm.org/exportformats.cfm?id="+tmp+"&expformat=bibtex", ' abstract = {},\n']);
  if(len(i.split("<span id=\"toHide"))>1):
    tmp=i;
    if(len(tmp.split("display:inline\">"))>1): tmp=i.split("display:inline\">")[1];
    if(len(tmp.split("display:none;\">"))>1): tmp=i.split("display:none;\">")[1];
    if(len(tmp.split("</div>"))>1): tmp=tmp.split("</div>")[0];

    tmp=tmp.replace("<p>", "");
    tmp=tmp.replace("</p>", "");
    tmp=tmp.replace("<i>", "");
    tmp=tmp.replace("<italic>", "");
    tmp=tmp.replace("</italic>", "");
    tmp=tmp.replace("<par>", "");
    tmp=tmp.replace("</par>", "");
    tmp=tmp.replace("         <span id=\"toHide", '');
    tmp=tmp.replace("\" style=\"display:none;\">", "");
    tmp=tmp.replace("<br />", "");
    tmp=tmp.replace("<span>", "");
    tmp=tmp.replace("</span>", "");
    tmp=tmp.replace("&ldquo;", "``");
    tmp=tmp.replace("&rdquo;", "\"");
    tmp=tmp.replace("&#215;", "x");
    tmp=tmp.replace("&", "\&");
    tmp=tmp.replace("%", "\%");
    tmp=tmp.replace("$", "\$");
    tmp=tmp.replace("}", "");
    tmp=tmp.replace("{", "");

    final[len(final)-1][1]=" abstract = {"+tmp+"},\n";


count =0;
out=open("master.bib",'w');
for i in final:
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  f = opener.open(i[0]); s=f.readlines(); f.close();
  success=0;
  for j in range(len(s)):
    if(len(s[j].split(" title = {"))>1): s.insert(j+1,i[1]); success=1;
  count +=1; print "Bib-napping", count,
  if(success): print "Success!";
  else: print "Fail!"
  do_print=0;
  for j in s:
    if len(j)<1: continue;
    if j[0]=="@": out.write(j); do_print=1; continue;
    if j[0]=="}": out.write(j+'\n'); do_print=0; continue;
    if do_print:
      print j,
      out.write(j);


out.close();
