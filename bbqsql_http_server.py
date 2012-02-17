#!/usr/bin/env python
# By Scott Behrens(arbit), 2012 

"""This is a simple webserver vulnerable to SQLi injection
make your query string look like this: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1
"""

import eventlet 
from eventlet import wsgi
from eventlet.green import time
from urlparse import parse_qs
from random import random

# Database constants
#datas = ['<g)`"S[FSx->ZXcN p<g"nX[533c1oYg', '|A1v.N}_n.DSX3)q;r\\K2T;X`d3yo2di', "7Qe'9lRhfqD=}%G7Ce\\lh!>1\\\\3|NsfX", "WDZ@0N^n1>v'@ Rt5I;HCb4;kpWF\\EFI", 'rFd!R%e>|S:3;k`uYRYQbtxn=IANUAKl', '\\z)]KB9&.}dhV0Dp#giWA2b0|4Jn3;!M', 'x\'mG*I-T.dTkeP"]4YlrTY2pE|70<x`\'', "8hSW&4x9zoZ}5IRZ)'VOJi_zJXQceT6e", '@ByGnWT$spE{Q{Wt.}NQMC8 *Ij%~UVc', ':u63&Uzlhfprb66Hpf%ER-ns:lbj:o9]', '.Yz]VrG%`.2\\zb:OJG"U)TW/@H[EN~8{', "u;2V-cpZ3$-Q,#XBr2s([Y9@Fg'Opt.U", 'SPp!n2pdf~dq+bc#lsn;)8Sw2uR\\\\t[O', '/FR/v(SCO;&+FV6s1f7!t@SV1)Bf&oPE', 'HqY@8O\\Af]4 &Ukf"5OXeMuFJ-Vc0,9E', 'C;x]?[_:\\@defVV4T_*[.-XxJ4SoLI96', 'fN"vuH=VYQ*?6PXw"P(bcBVlXGI-(,8C', '34o%N|#0(JtfBVFlO*{zItFUeyGte|c~', 'X(gU|+ ^/X=fl\'Q7&]6>`"=;d!^Og.l4', "(1#/0v81OqkNR&)viHqd3Q#,he2!>vB'", "@ X'@2_c@vVKU6XstPQuIa'zp7T^2_>T", "lBnO]'Un$1+syI=Vs,=S8#aIVGS!<\\1l", 'ys.1>wV}=;|I:3+R~mLQ,Xxk3GSy<W7G', 'hIi4\\rJ^iqok>h>\\eP*S^62OV0S{|[m(', '"U~Y!]FMM4vF sU7%Y5\\IR1h#`X#LK#b', 'pEDJ2F)|f~qW:rL&zJV+hsR[[L\\Nm}Ft', 'C{?pk2,/|F#N?%]I/"?wgE<h$u/h)"qx', 't"$QqE?voi1#1TU&I0(Ap({PTGHC`s7-', 't|MvQkUU<wGQ.DJse]Jvpt!Y5s0zwc&v', 'u]!?g)Ry>~?,PN#B_G;S:|eqmJ}xOOX{', 'C}^hX&jS.8I:4I*+A`q}T[k]Js:{fV`8', 'lKEITjix[qHBN8%YTU* 0#*3.okknzIO', ']l~iEjtL~9fW#pTl"L|l[s\\G$u!Q$vjJ', 'NS=r-wIGHBL<mC&CN@eaFg(eBx;(t\\Uy', 'KZ7gdIo\\w;bks_;K,/+ #C1c7tD+q7g<', "k<+W*pF}^P='jD+h}qZp/]Pi!NYtv(m|", '%neCTS2-zi9Q;T,NJR"kK!{#AI~BS`]\\', "AtVjG-[IZNN<;m'[tCYq?FqdYY^{Z<~ ", "Xyk_0'q,ES<$vx@J6ogJl(GDg&OLl 5.", 'SyX5Y^jyZjTY{szmbP}^vFcZT>|{AFNm', 'Z8b(mz~d[=gp?JIZEIV6d:4oivfVe&p?', 'o :6rG3E;Hz]o-=QwO/Q3(ulL!5"hieo', '5mYn;hjP][,w10Sa?@i1&(?zB=,<\\Z!|', 'zZzS?{Cy7U$7_GNSr&Ha8*{*CxU7RiK`', 'Eku;"4L^6[g*JeP%,k]h DZm7dyd~T8i', '5^;<;{oB#O*uK*ovR,(X9B\\(U%B=X\\.g', "^k<Gz'NAF::5Txjt*x1j,U09mS/b^v^u", "b]t5>9)\\'aY:yLB3F++X3_pA<}>>XlX~", 'l_m`RgfwbHJ2/6vk:~Kx$L${(l?%PeQp', 'm)C@^SG8F;6; r9IwH JSC\\OgG"[I:j3', '+ pY,l"Q]d(@f)d34;z(zHw\\,`,9qGk(', 'h8\'zi!?M;,O"z$ s#$|_ HX%F/VmS+(Q', ':~z{Yi _|XD=1MUOuQ:Oz0~=Q%M$AKG8', "m9gj'c:eXAT_fg3jt9Oya)#O13mb$R='", "Q< -n[\\!FQr@{Mb2}::aWaPc'i}$XH c", '$,@/c.Q5*fvF$QHPH`)&xu\\nzM].vv22', 'EXa{d\\HPq<Y;zWfERPE`FhKxsLl!v5p{', "J][I*}PqH'W[Q0E,<]7]t<vQPYBD5TB:", 'x:6F"cShCpiG\'\\hyZP$[57=@aSg}H:*M', 'a8bS=#rX<)["wL?i.cC@D*XgQJ\\\\%G$m', 'l?-/FxGlN9m%PzO`<L0nm=2|*aVb{OSc', '!dyu:v lt.%osmt?J.4*5rT_V#+<numf', 'uVlb!&xtdB!y!Q+BP^0]xYB;IVaXj3Yk', 'YfKI|Le)kpr8PnF/\'W]#>J,6|;"SwGo-', '/Z}{=YD9T;\\De9gez.\\-_JU[;=[SWY.#', 'S/-Tx%$#9"ad#io-8y,"0,BI&kha?)%l', 'df[&o,`qAAdh1dO@:Ur~K/>[}${5XQJ.', "_,'/j-;vWWvh>e@~yiR02LrJL=u088u3", 'l3kbn$0Uj;S%`!=]^*Te4IV}ia2,Gn`Z', 'CI%AxcHT-Fcw]k-Ug4Q8^+9OkrzBCkA|', 'r`3f=jYuM:SdSmX$)|#LevaIzzk6#wK1', '=VPJtK3v`ESRg|co/9[K|qP>Ec73:p>A', 'x9i#^im4/*\'Y*"-#9lL`a&b(Br-%\'#C}', "FI9[hZ,x+=:D%%#$ONJ_<'1&sGU[zA|B", "y~Nc'k-A8pa2gP34FLWSBZm3)/:f0pP1", 'Z4r)T{\',s82G7gQ=m*\\UM}4N"7Wy:D~5', "6x/{LtrBpIg{p=VMgE_TO,'-L/Q.+? 5", '+w@d(gOZ"et[_P{h.^~J*`xYR0P<|gv4', '`<,</!O{+=WI)_{UgM* 3H Ys@&P73`H', "X=yt?j'Up-a~w`S?c(=|dO{ZUL2~%W-v", "%4@/*'ic=@x]sAB&G\\jZ,N50srftHrKO", "#Cs6-_8%'#LR$ZXw*r+/r8YAt6_$E;Ag", "F512?i?#Tr&'=Mm\\b[\\oTUzYSfcy47q~", 'ahp`{yOAu&"Gfnm2i%&.3u+WpMO1&3[Q', '>Z7HnGE8Lcr0?9ss`gXZuSd}*Njg]H0R', 's M.mU<{7t&"JTb9F*Ek7N8Z8A<WLfob', "J3fA'*41wTdM+-xA*Uegn PqeZA|]alS", 'GuPMDch_}KSxG"{Kwku"@lUUANe<7|i_', 'O?. OXC}bd})u,aOhp[K#LZC$CsBN4KY', 'OL=:a`L|pJM*_Adi>o}>vVwKxr:3wwut', ']a]_cn7l:q,RTq=?M)a@KJ:[uQ}H,fx4', "2a0c;rW|> k~Wtgb pam+Ic7T`'a]p?n", 'c*ubf0ay.|BCjy,vf*wQC[ec56%d/HXo', 'rS$CuH}W*woB/Zm}D"a]_-noM4eIa+/z', 'bnQs84.eN%aJqg>0vJ4r?NY|?2^8/Zk5', 'G!zA![y >-`EP7pNC`8 nfKNo7<5CCb@', '/skp!EPqMb)a65l!A\\#^_nMcT1]-k3a\\', '11JQ~JrF3:+ [l^i)<mtwR8gb;R??a>n', 'Xh,,0+X /2=w~T#dA,L~ Jy]HdI\\c@}b', '*#%h~`8o5d[j\'kk";gDY%NlboGT,e<l:']
datas = ['hello','world']
# Different comparators BBsql uses
comparators = ['<','=','>','false']


def parse_response(env, start_response):
    '''Parse out all necessary information and determine if the query resulted in a match'''

    #add in some random delay
    #delay = random()
    #time.sleep(delay/10)

    try:
        params =  parse_qs(env['QUERY_STRING'])

        # Extract out all of the sqli information
        row_index =  int(params['row_index'][0])
        char_index = int(params['character_index'][0]) - 1
        test_char = int(params['character_value'][0])
        comparator = comparators.index(params['comparator'][0]) - 1
        sleep_int = int(params['sleep'].pop(0))

        # Determine which character position we are at during the injection
        current_character = datas[row_index][char_index]

        # figure out if it was true
        truth = (cmp(ord(current_character),test_char) == comparator)

        #some debugging
        #print "\n\n"
        #print "%d %s %d == %s" % (ord(current_character),params['comparator'][0],test_char,str(truth))
        #print "char_index       : %d" % char_index
        #print "row_index        : %d" % row_index

        # Call the function for what path was given based on the path provided
        response = types[env['PATH_INFO']](test_char, current_character, comparator, sleep_int, start_response,truth)

        return response
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['error\r\n']


def time_based_blind(test_char, current_character, comparator, sleep_int, start_response,truth):
    # Snage the query string and parse it into a dict
    sleep_time = float(sleep_int) * truth
    time.sleep(sleep_time)
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello!\r\n']


def boolean_based_error(test_char, current_character, comparator, env, start_response,truth):
    # Snage the query string and parse it into a dict
    if truth:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, im a bigger cheese in this cruel World!\r\n']
    else:
        start_response('404 File Not Found', [('Content-Type', 'text/plain')])
        return ['file not found: error\r\n']


def boolean_based_size(test_char, current_character, comparator, env, start_response,truth):
    # Snage the query string and parse it into a dict
    if truth:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, you just submitted a query and i found a match\r\n']
    else:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, no match!\r\n']
        
# Dict of the type's of tests, so pass your /path to execute that type of test
types = {'/time':time_based_blind,'/error':boolean_based_error,'/boolean':boolean_based_size} 

# Start the server
print "\n"
print "bbqsql http server\n\n"
print "used to unit test boolean, blind, and error based sql injection"
print "use the following syntax: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1"
print "path can be set to /time,  /error, or /boolean"
print "\n"

wsgi.server(eventlet.listen(('', 8090)), parse_response)
