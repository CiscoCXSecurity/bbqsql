http = require 'http'
{parse} = require 'url'
DATAS = ['hello','world']
HOST  = "127.0.0.1"
PORT  = 1337
DEBUG = false


cmp = (x,y) ->
    r = 1 if x > y
    r = 0 if x == y
    r = -1 if x < y
    return r

debug = (message) ->
    if DEBUG then console.log message

server = http.createServer (req,res) ->
#this server parses query strings looking for the following:
    #charval: the integer character value we are testing against
    #charpos: the pos in the string we are looking at and testing against
    #row    : the index in the 'DATAS' array that we are working on
    #cmp    : how we are comparing the charval to DATAS[row][charpos] (gt,lt,eq)
    #sleep  : how long to sleep if cmp returns true
    #example request: http://127.0.0.1?charval=65&charpos=0&row=0&cmp=gt&sleep=1
    debug "\n---------------------------"
    debug "received request"

    #Parse the query string. It is really not good to eval it like this. Just don't
    #host this publicly.... I need to figure this out i guess.
    try
        debug "args: #{req.url}"
        args = parse req.url,true
        args = eval(args['query']['q'])
        args = args[0]
    catch err
        res.status = 200
        return res.end "you fucked up"
    try
        charval = args['charval']
        charpos = args['charpos'] - 1
        row = args['row']
        cmp_method = args['cmp']
        sleep = args['sleep']
        sleep = 0 if not sleep?

        #make sure we have enough to go on
        throw "NotEnoughArgsSet" if not ((charval=parseInt(charval))? and (charpos=parseInt(charpos))? and (row=parseInt(row))? and cmp?)

        #find the charcode we will compare with
        throw "OutOfArray" if not (cmp_char = DATAS[row][charpos].charCodeAt())
        debug "http_char: #{charval}"
        debug "db_char  : #{cmp_char}"

        #test to see if their sqli query was true.
        cmp_return = cmp(charval,cmp_char)
        debug "cmp_returns: #{cmp_return}"
        cmp_method = {'gt':1,'lt':-1,'eq':0}[cmp_method]
        debug "cmp_method: #{cmp_method}"
        throw "False" if cmp_return != cmp_method

        debug "\nstarting sleep"
        start = new Date().getTime()
        while (new Date().getTime() - start) < sleep * 1000
            123
        debug "done sleeping"

        res.status = 200
        res.end "yaya"
        return res
    catch err
        res.status = 200
        console.log err
        if err.type? then res.end err.type else res.end err
        return res
.listen PORT,HOST
