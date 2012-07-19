#BBQSQL#
*A Blind SQL Injection Exploitation Tool*



## What is BBQSQL?##

Blind SQL injection can be a pain to exploit. When the available tools work they work well, but when they don't you have to write something custom. This is time-consuming and tedious.  BBQSQL can help you address those issues. 

BBQSQL is a blind SQL injection framework written in Python.  It is extremely useful when attacking tricky SQL injection vulnerabilities. BBQSQL is also a semi-automatic tool, allowing quite a bit of customization for those hard to trigger SQL injection findings.  The tool is built to be database agnostic and is extremely versatile.  It also has an intuitive UI to make setting up attacks much easier.  Python gevent is also implemented, making BBQSQL extremely fast.

## Overview of Readme ##
We tried to write the tool in such a way that it would be very self explanatory when seeing up an attack in the UI.  However, for sake of thoroughness we have included a detailed Readme that should provide you additional insight on the specifics of each configuration option.  One thing to note is that every configuration option in the UI has a description associated with it, so if you do choose to fire up the tool without reading this page you should be able to hack your way through an attack.  

## High Level Usage ##

Similar to other SQL injection tools you provide certain request information.  

Must provide the usual information:

- URL
- HTTP Method
- Headers
- Cookies
- Encoding methods
- Redirect behavior
- Files
- HTTP Auth
- Proxies

Then specify where the injection is going and what syntax we are injecting.  Read on for details.  

## BBQSQL Options ##

In the menu you will see a place for BBQSQL options.  Here you specify the following options:

### query ###

This is described in greater detail below [query syntax overview](#query-syntax-overview).

### csv\_output\_file ###

The name of a file to output the results to. Leave this blank if you dont want output to a file.

### technique ###

BBQSQL utilizes two techniques when conducting a blind SQL injection attack.  The first and default technique used is binary_search.  [See Wikipedia](http://example.net/) for more information.

The second technique you can use is frequency_search.  Frequency searching is based on an analysis of the English language to determine the frequency in which a letter will occur.  This search method is very fast against non-entropic data, but can be slow against non-english or obfuscated data.

You can specify either `binary_search1` or `frequency_search` as the value for this parameter.  

### comparison_attr ###

This specifies the type of SQL injection you have discovered.  Here you can set which attribute of the http response bbqsql should look at to determine true/false.  

You can specify: `status_code`, `url`, `time`, `size`, `text`, `content`, `encoding`, `cookies`, `headers`, or `history`

### concurrency ###

Concurrency is based on the gevent library in Python.  Functionally, it appears to act like threading but the specifics of how this works can be seen in our DefCon talk here [insert link here].  This setting controls the amount of concurrency to run the attack with. This is useful for throttling the requests and speeding up attack times.  For really high performance web-servers such as nginx, we have been able to set the concurrency to 75.  By default this is set to '30'.  

## Query Syntax Overview ##

If you run into a SQL injection vulnerability that has some weird quirks (such as certain characters can't be included or functions like ASCII/CHAR do not work), you have probably found yourself writing some sort of script with your custom injection syntax.  BBQSQL takes out the scripting part and provides a way for you to paste in your custom query syntax and exploit with ease.  

The query input is where you will construct your query used to exfiltrate information from the database.  The assumption is that you already have identified SQL injection on a vulnerable parameter, and have tested a query that is successful.

Below is an example query you can use to construct your query.

In this example, the attacker is looking to select the database version:

    vulnerable_parameter'; if(ASCII(SUBSTRING((SELECT @@version LIMIT 1 OFFSET ${row_index}) , ${char_index} ,1))) ${comparator:>}ASCII(${char_val}) WAITFOR DELAY '0\:0\:0${sleep}'; --


The query syntax is based around placeholders which tell BBQSQL how to execute the attack.  

You need to provide the following placeholders of information  in order for the attack to work.  Once you put these in your query, bbqSQL will do the rest:

- `${row_index}` = This tells bbqSQL to iterate rows here.  Since we are using LIMIT we can view n number of row depending on ${row_index} value.
- `${char_index}` = This tells bbqSQL which character from the subselect to query.  
- `${char_val}` = This tells bbqSQL where to compare the results  from the subselect to validate the result.
- `${comparator}` = This is how you tell BBQSQL to compare the responses to determine if the result is true or not.  By default, the > symbol is used. 
- `${sleep}` = This is optional but tells bbqSQL where to insert the number of seconds to sleep when performing time based SQL injection.

Not all of these place holders are required.  For example, if you have discovered semi-blind boolean based SQL injection you can omit the `__${sleep}__` parameter.  

## Custom Hooks ##

Sometimes you need to do something really crazy. Maybe do you need to encrypt the values going into a field before sending the request or maybe you need to triple URL encode. Regardless, these situations make other tools impossible to use. BBQSQL allows you to define "hook" functions that the tool will call at various points throughout the request. For example, you can specify a `pre_request` function that takes the request as its argument, does whatever mutations are necessary, and returns the modified request to be sent on to the server.

To implement this, just create a file named `bbqsql_hooks.py` in your current working directory. Here you can define your callback functions for the hooks. Then, at the bottom of this file, add a dict named `hooks` whose format is `{'hook_name':hook_function}`.

When you run BBQSQL, it will look in your current directory (as well as your normal Python path) for for file named `bbqsql_hooks.py` and will import from it the dict named `hooks`. 


The following hooks are made available:

`args`:
    - A dictionary of the arguments being sent to Request().

`pre_request`:
    - The Request object, directly before being sent.

`post_request`:
    - The Request object, directly after being sent.
    
`response`:
    - The response generated from a Request.

For more information on how these hooks work and on how your `hooks` dictionary should look, check out the [requests library documentation on its hooks](http://docs.python-requests.org/en/latest/user/advanced/#event-hooks)


## What's up with the name? ##

BBQ is absolutely delicious and so is SQL injection!
  
