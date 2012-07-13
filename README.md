#BBQSQL#
*A Blind SQL Injection Exploitation Tool*



## What is BBQSQL?##

Blind SQL injection can be a pain to exploit. When the available tools work they work well, but when they don't you have to write something custom. This is time-consuming and tedious.  BBQSQL can help you address those issues. 

BBQSQL is a blind SQL injection framework written in Python.  It is extremely useful when attacking tricky sql injection vulnerabilities. BBQSQL is also a semi-automatic tool, allowing quite a bit of customization for those hard to trigger sql injection findings.  The tool is built to be database agnostic and is extremely versatile.  It also has an intuitive UI to make setting up attacks much easier.  Python gevent is also implemented, making BBQSQL extremely fast.

## High Level Usage ##

Similar to other SQL injection tools you provide certain request information.  

Must provide the usual information:
<code>

URL

HTTP Method

Headers

Cookies

Encoding methods

Redirect behavior

Files

HTTP Auth

Proxies
</code>

Then specify where the injection is going and what syntax we are injecting.  Read on for details.  


## Query Syntax Overview ##

If you run into a SQL injection vulnerability that has some weird quirks (such as certain characters can't be included or functions like ASCII/CHAR do not work), you have probably found yourself writing some sort of script with your custom injection syntax.  BBQSQL takes out the scripting part and provides a way for you to paste in your custom query syntax and exploit with ease.  

The query input is where you will construct your query used to exfiltrate information from the database.  The assumption is that you already have identified SQL injection on a vulnerable parameter, and have tested a query that is successful.

Below is an example query you can use to construct your query.

In this example, the attacker is looking to select the database version:
<code>
vulnerable_parameter'; if(ASCII(SUBSTRING((SELECT @@version LIMIT 1 OFFSET ${row_index}) , ${char_index} ,1))) ${comparator:>}ASCII(${char_val}) WAITFOR DELAY '0:0:0${sleep}'; --
</code>

The query syntax is based around placeholders which tell BBQSQL how to execute the attack.  

You need to provide the following placeholders of information  in order for the attack to work.  Once you put these in your query, bbqsql will do the rest:

__${row_index}__ = This tells bbqsql to iterate rows here.  Since we are using LIMIT we can view n number of row depending on ${row_index} value 

__${char_index}__ = This tells bbqsql which character from the 
subselect to query.  

__${char_val}__ = This tells bbqsql where to compare the results 
from the subselect to validate the result

__${comparator}__ = This is how you tell BBQSQL to compare the responses to determine if the result is true or not.  By default, the > symbol is used. 

__${sleep}__ = This is optional but tells bbqsql where to insert
the number of seconds to sleep when performing time based sql  
injection

## What's up with the name? ##

BBQ is absolutely delicious and so is SQL injection!
  