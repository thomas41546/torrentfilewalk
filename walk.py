import os
import re
import sys
import codecs

def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)", re.UNICODE).match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i = i + int(s)
        else:
            yield s

def decode_item(next, token):
    if token == "i":
        # integer: "i" value "e"
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = next()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src: # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data

def decodex(text):
    if isinstance(text, str):
	text = unicode(text[:255], 'utf-8', errors='ignore')
    else:
        text = ""
    return text

of = codecs.open("/dht/out.txt","w", 'utf-8')
for root, dirs, files in os.walk("/dht/mldht/work/dump-storage/torrents/",topdown=False):
    print("Processing %s" % root)
    files = [(f.replace(".torrent",""),os.path.join(root, f)) for f in files]
    for fn, f in files:
        data = open(f, "rb").read()

	try:
            torrent = decode(data)
        except:
            print("ERROR!")
            continue

        if "info" not in torrent:
            continue

        hasy = fn
        if "name" not in torrent["info"]:
            continue

        name = decodex(torrent["info"]["name"])
        
        if "files" not in torrent["info"]:
            continue
        for file in torrent["info"]["files"]:
            if "length" not in file: continue
            path = decodex("/".join(file["path"]))
            out = u"{} || {} || {} || size={}\n".format(decodex(hasy),name,path,file["length"])
            of.write(out)
of.close()
