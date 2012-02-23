#!/usr/bin/env python
# By Scott Behrens(arbit), 2012 

"""This is a simple webserver vulnerable to SQLi injection
make your query string look like this: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1

command line usage:
    python ./test_server.py [--rows=50 --cols=150]
        :rows   -   this controls how many rows of random data to use for the database
        :cols   -   this controls how many rows of random data to use for the database
"""

import eventlet 
from eventlet import wsgi
from eventlet.green import time
from urlparse import parse_qs
from random import random,choice

# Database constants
#datas = [':i1)4m<k17D+y{24~kuuA -6ToJv>sSkw1\\h;nLLsaL4t&DcRhp{ -g@\\])=LIe,.sV&,ao^$A24yLP[kr| n)2K|E{1kpS$tTJ@', "b(X;U@gE*i_)FdLpNIXFq:L4s>cLm>OI!:tMfD[e0NbLng<bIn{Fm^q3zY~};lz`\\dgn11MF.ewfBHR6]vH$+6fl#~s0[u'w.hos", '23ir{XV9aRC3UIM_!(@KPHVv0w5^2P:(Ad^c6c.5g#*:%j9eC;(O!WT\'X?+"b|%|J*t$|/7%]LkEzrGew;tYx1JD{2OzP8E"9xso', '~(-3{9dSeuqK9qL]W*GXaw8{!fYvvO~a^or.~8y|ru,Ydm%:UoKnxpar:|m/VDLZ\\D> V5*fcRl"Thv1R;#l;+(u&\\v[[kGVi}~g', ' +]33s~;cKn>hpPcENjf~MG2pQ&DrQ#P_"`AE!_rD~[WNGb:D\\~aWeEO|L_uDT+VZ(Q2/Lniq }NYE"<JGmZ3;\\UUNh60WD!&}gO', "8H(~x|$YbT+8mB5-!174WR@h>kX1w'q-]2R}G/t+fl9IS\\G8?M6='QO8?:X4b]=RrM'7})K_L9yB`{MWL(R1`W3U/K<1E!M{a8x ", 'sVr(.Q?D U4{cJeA}@(p@&ew:/L+G4@H5QnA"B.I\\k\':MvC!\\svL(gvWry#,oKT{G5EAP_9I_wSN+A9?GeBnYCB*Pg7D\'x^%l&C<', '"KSUaT"[+GXSIvM!/P|W4ZZ0Nv15qk:G,FU<I`oTII{BSBM2Jz<<o<jT%=F ]D[;;6E}@?R<agvTtYaM5+Ax4yiUi;oA}^L.IAg~', "g`#:Z!eg+b3jXrl2.s~z-2~[}d[3[%$trZ`i@}0Lhhel`CNld@na3{\\Lj0zT8\\9{E}=R@w1G^6'(Q~x`i6Mp00iqJ]eG*nFNF}h8", 'hbIgf=/TBb ujOw{DE$csVezGy@TQG8WLn5tk<"OZ7CV7O6q8sy\'-"LpU3J3s%t;M3A\\?sg#T))_,P~(!P%)4Y\\]{h|t 6=`ID4w', '=w<LYsi@2O6~l#gq07 9@3~|MmCho\\<"|lfjiG2;WVKd7,H]nC0~dC lZ9PZB:_BQftE!O8Jy^E];O5Ri ZIp`=J) 2*e.i8f;zf', ";O#d;0 .]wu=?Ym`RMBR(<-IKq>(\\_duJj@?K_k?P!s?EylR.1D~6p*9\\YD>SxEiQBBNad~Kc8lV~@JyCbMJL$&'fFbF?&H^kh:*", 'CJ"? zCFay;6[Y+iT#KJ!6cDwMz>;C`jL!P)t+w:.l^`E[*qevLfmGjX6EnAUIm>3LaV5SRex{Bn,fyqU+4;$qgitut9*0mfL~yl', ":bP|BAY,:GO:5kFH/%5]kLND\\^(Z?,+]\\VM6:l^B||}5/#]DKTVI9]1|7Bc]wPpVcUk,{{&\\r1?ic*00\\CR%'N3R\\2]J:mIJojKt", 'Bgva>l)0#%6o<t~I-Uvj,BSEdou%UHc#JLs@&t0utb?icQ~TM$P]{|M--byEPH9cr}"`>;HA4(Ke}bg,Rp~!WP/KV2!/YNC<"vAz', '9*~*$=.SX>1Wx<Tn,YN</c9Ob k\\JQLdrvH*g0B&_y)g]seb1yfaQdu{a/5A,vS<,)hU`%T`\'xPzl>"_?d;p1KOC;Qkl{|dav1Jv', 'y`yk{ODsiu\\Mqp<.g;v^\\OpDGmw9;}1H0(cql0rVc0@hd\'}|8e"?p2C4UAs7A;ecM3rMHnb~Mm3P4^?2A"SqVBa;b\\}{6^3IC+@Z', 'GFR~M1]s?=/HTiTNF24[ifk.a%]/8$<wrbzL(kB\\4y`1?j\\\'c!V=UXV{*a%8FzR\\EZW)5v"*}GT_F:}B.#,F0fb/=2<eh!:)?"8G', "/K ,A]R4M#n9xGJZN^Tr'P+TY&X[d*<[qOTz*rsoS~!@`,#GQ-q1NS8Jk|'R.bvtgGkA5px]-H5X=:*a=)fVdpZ(nTP,UDuI<w_d", "vM(*z28a[y9n>}/+@42{V9W<bm^4h<_x.;\\sG+W2',}\\ $]/DYk>q8KsFWakK4T|;2#(~S-gd|]!Bp(3{R<@%<td.h^1G(_$?IX-", "z'xrV{j3%$G__%\\7=ICW@iUc<ekAN'R/B{&&6e*4YYW%W0`<K@;q0siCr]&5mF$|xIDh6nCh`(Cow\\w;8XQbEC,vTy,8JEJ7P{<V", 'A8 =Z{aT9Yt_Hm;sS2?6aEef!u[d":bmEK;Ayfjc@2x&2E!a3OeSEwozc/4ccqrA/^)gRrO-[<suL|k#}}H,8`@aU#?Uw1"8M\\u#', 'UA2j<14)qNbpEpx]PHeFH!+\\\\\\U!W-e_[E.9^Z1,p{w|n549V;qB#Br"w6h}B!Qf_O%.(h|4_ucJ7i)}M|Aq_F!ebp4Vao!KHR@E', 'lBQ4T4~Z5b^1,sjASS2q:DsaK5e}7`DV=@x"<=mM)I.3Y0\'c|?viKaGqoP X=U_m$f6@xBrKp(5:~OyVfci*-<wN.Iq<nW"oTg6U', '!^K\'s! =Xe\'E.1hrBcZ*w*ND{, @{xEMXvmG`< ,S_qJANb7+a_jylHoSTO)Zy_&e_\'v#XCq~Tgzi(,}8^8{XLL5j@L\\(",\\\'e_G', 'h|bq~Qk4>J9-S>6B.Gz{^SluFk0Rti!W+ `w{t[\\}":]Iz3LCP^9JHRnc@<iR$k`.bk#b\'KD  $ZVtEwoarN3Eh?[}|D(.BJ7<R*', 'u}vw8ZGB bQ}!-yX_+6Yj+9wPkjKAaQ1!7\\e+,6D9wSVy):wUO1k`DDJ"Gs X\\yoHcOUizQ@\'49gwa7Lm\'`ll5!d257vG%H_ELTH', 'V5}}%+{]#zI^dQ@-;"o7UO\\c"a9+SE1%v9)DV<rOlFSRzHQx]_1W?*k^,a$?bG-`a*!rbw{D+/ Hms+287qivq8,}+UPaw07=k8b', '#}c:Eqez!\\Elx!ceWDh_wd=4?raTYw;YW9M\'U@/KiJ~qTW$ b`4Yy?AFRy1<=DhqZT7{v.iP!+#"1 ~li?5r8mhKuI3;3Va)\'<(r', 'q67%2>oYhfqPG.W<#&Ejm+H{a/#E(m+#L,533T!HlvTC?hrSHH[Lq$#JgpRbn~lw5/zkYtr1P;-v}u@%^j,#E`ER:z? N`]%/+cC', 'KG(1m0:R{%J0o^[EY-&nieiaVqJ[JXs{2Wg:28!fyITK:bf/]Zr7{^q?UriYY^-OwOBUmc;m*AC6GvfifWT37!;^kCwbD{l8ZK<$', 'Q_Ny6$PW0}`DXJk{DX/6MjLFyJB+edDU<Ph2a!H*p#:m1T~:dsbMvkLA<1Pu49q]*<&Jr<tr:,mdQ$L{"AA-6=`c8wVt0Y98Q^h@', "!7X\\kkO`R,~lC{&/m}xUPhpC*U]}Y^^U\\f-pxc/;x{e#~rZA0FDM/fKqFl1: PMF^eU6CTac.'[9P!-q$f|6r6>T$q&O^ mfGLLb", "Y`?l[J(6cgF3c*C?4b}cv?V7xcr8=j\\Uvu!XaRGytKCkaFnxE/TnH6\\Z&+pUs_$M]%5*#'}(]`6hucJ8.1HY<l|L.*ve#]LiuLDP", 'Cw,_F|qoR?MHo;Qb^{rnOmw{3?PnC`]>B6#Fx\\P[129rO/0"]Imw5Fn4RZxQ+3J3J`Vwy?;JTCXSgL>:7z3/D~z1bxb`D\'\\\'N!y[', 'Ta63Q.b>7f,W0a_g?\\rP6ZTTj^ Gu4`&IA"o%6;p4xHY|BC8A/_~:iCR+BGQXWbZp=fbD%oL9s%is&mh7(db%]NXt[@Y\\D+5>@|^', '0v|u<\\ufc#H}a%1e{Qvm2T8P@3SJ2ecXmQ`R@s!?7<8IES}iRr&$H%V`*`OHqm"MtoW0ASfsj{l#t9e(ZOAh|`wba[3I_2ZA=;V&', 'wC?BfL&A x\\@rqm0QG2t9bsY:]}{lj){Wcn&Ga#nwSbI{OUR;>%JK"bYvoihZ)JejWre1N;!MyFs?bOSgFoe/VHS,U[aG2d X|j*', "y1Q.80n$PF?4/F\\4@R/f%JT!#IpL4Sq|vg }(<RN`ebi>q~Fy&F~-ute[{&\\_f[Va &c!dqe9M[ok`J>viqMJ`g*?5#w_24'c\\c[", '9~qA<z-Gbcv_K"&(Tvn.=<97*/1U.\'2a6B]4#jIQe!M1w|\'J{?C<5P$SON=S-_8.^"Rq^A/yR$)CQ*zEjEWio-):1R~)}h\':8)w,', '9czv@r,9/oOrri,7+6>\\NnyWDvUNVVZO~fvl\\` BMf7){OMijDs(n~qKukG9QdX=BX,.~5v*(o>_o#MUSA_`0q9$_nc)fP+ZJ,}T', 'LM*t<S8)wvRvw3W1~^,j toA7D)_(/~aAH1XJ:52+QP&}CfT7H-<cC}@}o|UpZgu15(L(?w1&`<6/TXHghj8._vQ.(V@"Xr<#O"k', '. w<W$paYT5T0Jvokf3g0"G-HPT9|Hs8>)5xhE|S<eR1Fx9)*O |Z[;fNiv8W@5z{7zs46+((V4~1/KJ4fKE;U53BRB}3j_Kq=<U', "(Dm6/MafgY41kB/()X:NQw jJ 6eH,{&ZI?`lAnN20JX7,)y$OJJfTk%bN4M;kBe<-Qb2j>_1'+I<qpf&.L`e874s(n+.V9`s>EN", "TjkH^Px\\'L^PM7QZm*.r>%l1fk@<QftOhcg!I#HGYU`}$L^@&wMC).[pP7[79nvi`cy{An+UljjfWRk|]+ eCx8CIB4tp~CynP>;", 'wUu%&T*WFwSK&2"GLS;;WFC!iT<zz;gz*&_r0#4T>iY[m2"}*BH5ZEwy87!Xy+B <d" #`wNbE3"f)Nx]Us[8I`J:PbGuaS"9!:v', 'Hn%{RezI5>iJ$9nOEjIKDG}Hi<AJg KE#@~t\'W^+!qXbM675tI?#yc"p^pQVOP<nE-j6A4E dc-:Wl}WE?IkbH}t!nOn8*8A`n(6', 'i2"GP9nFkO-LqmZcr@isThiWGl@,q=H@!)eNELIpT656r+@y_] 2~0<F0Xq GJMuJmfHs}aMvE"puC=90)8znbhfAH"JvlIyQXoY', "1VMt\\%r]Wtq+0OUjj_Ar) }EX!. gUlU>(pIbGuo-]Dh<9!2UuT\\;\\<RfeE~#1^%?v*}GQ`A`i'2WC4(%1=|sC9 hEZ3/+<q\\.qh", "pC<Vsm#L'Sk&cd,Uxi@ZcQWP&0[+?cwdB<M.j2/?X$Xhw|)<]H7c[4be~Qes&w+%A,,&{zjU7^yac%#5u$$OGQqzN/eL5/8Z8S{$"]
datas = ['Strange women lying in ponds distributing swords is no basis for a system of government. Supreme executive power derives from a mandate from the masses, not from some farcical aquatic ceremony.', 'Three rings for the Elven kings under the sky, seven for the Dwarf lords in their halls of stone, nine for the mortal men doomed to die, one for the Dark Lord on his dark throne, in the land of Mordor where the shadows lie. One ring to rule them all, one ring to find them, one ring the bring them all, and in the darkness bind them. In the land of Mordor where the shadows lie.', 'Im sorry, Dave. Im afraid I cant do that.', 'Spock. This child is about to wipe out every living thing on Earth. Now, what do you suggest we do....spank it?', 'With great power there must also come -- great responsibility.', 'If you cant take a little bloody nose, maybe you oughtta go back home and crawl under your bed. Its not safe out here. Its wondrous, with treasures to satiate desires both subtle and gross; but its not for the timid.', 'Five card stud, nothing wild. And the skys the limit', 'If you think that by threatening me you can get me to do what you want... Well, thats where youre right. But -- and I am only saying that because I care -- theres a lot of decaffeinated brands on the market that are just as tasty as the real thing.', 'Were all very different people. Were not Watusi. Were not Spartans. Were Americans, with a capital A, huh? You know what that means? Do ya? That means that our forefathers were kicked out of every decent country in the world. We are the wretched refuse. Were the underdog.', 'If Im not back in five minutes, just wait longer.', 'Im going to give you a little advice. Theres a force in the universe that makes things happen. And all you have to do is get in touch with it, stop thinking, let things happen, and be the ball.', 'WE APOLOGIZE FOR THE INCONVENIENCE', 'Some days, you just cant get rid of a bomb!', 'Bill, strange things are afoot at the Circle K.', 'Invention, my dear friends, is 93% perspiration, 6% electricity, 4% evaporation, and 2% butterscotch ripple.', 'Didja ever look at a dollar bill, man? Theres some spooky shit goin on there. And its green too.', 'Alright, alright alright.', 'Heya, Tom, its Bob from the office down the hall. Good to see you, buddy; howve you been? Things have been alright for me except that Im a zombie now. I really wish youd let us in.', 'Never argue with the data.', 'Oooh right, its actually quite a funny story once you get past all the tragic elements and the over-riding sense of doom.']

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

if __name__ == "__main__":
    # Start the server
    print "\n"
    print "bbqsql http server\n\n"
    print "used to unit test boolean, blind, and error based sql injection"
    print "use the following syntax: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1"
    print "path can be set to /time,  /error, or /boolean"
    print "\n"

    from sys import argv    
    import re

    CHARSET = [chr(x) for x in xrange(32,127)]

    rre = re.compile(u'--rows=[0-9]+')
    cre = re.compile(u'--cols=[0-9]+')
    rows = filter(rre.match,argv)
    cols = filter(cre.match,argv)

    if rows and cols:
        rows = rows[0]
        cols = cols[0]

        CHARSET = [chr(x) for x in xrange(32,127)]
        datas = []
        for asdf in range(5):
            datas.append("")
            for fdsa in range(100):
                datas[-1] += choice(CHARSET)

    wsgi.server(eventlet.listen(('', 8090)), parse_response)
