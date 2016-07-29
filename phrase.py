'''
Created on Jul 27, 2012

testing the directory change touch

@author: avneeshsarwate
'''
import string
import subprocess
import random
import OSC

class Chord:
    def __init__(self, *args):  #list, root, name
        self.n = list()
        self.type = "chord"
        self.root = 0
        
        if(len(args) > 2):
            self.name = args[2]
        else:
            self.name = ""
        if(len(args) > 0):
            if (type(args[0]) == list):
                self.n = args[0] #[i for i in args[0]]
                self.n.sort()
                self.root = self.n[0]
            else: #if first arguement is not a list it must be a chord
                for i in args[0].n:
                    self.n.append(i)
                self.root = args[0].root
        if(len(args) > 1):
            self.root = args[1]  #should it be the index or the note val
    
    def __getitem__(self, i):
        return self.n[i] 
    
    def __len__(self):
        return len(self.n)
    
    def __str__(self):
        return  str(self.n).replace("[", "(").replace("]", ")") + " [" + str(self.root) + " " + self.name + "]"
    
    def append(self, note):
        if note in self.n:
            return
        self.n.append(note)
        self.n.sort()
        if self.root == 0:
            self.root = note
    
    def invert(self, arg):
        for i in range(abs(arg)):
            if arg > 0:
                self.n.append(self.n[0] + 12)
                self.n.pop(0)
            if arg < 0:
                self.n.insert(0, self.n[len(self.n)-1]-12)
                self.n.pop()
        for i in self.n:
            if i%12 == self.root%12:
                self.root = i
        self.n.sort()
        
        
class Progression:
    def __init__(self, *args):
        self.c = list()
        self.t = list()
        self.names = list()
        self.type = "progression" 
        if(len(args) > 0 and args[0].type == "progression"):
            for i in range(len(args[0])):
                self.c.append(Chord(args[0].c[i]))
                self.t.append(args[0].t[i])
        
    def append(self, arg):
        #print arg[0]
        self.c.append(arg[0])
        self.t.append(arg[1])
        
    def __len__(self):
        return len(self.c)
    
    def __str__(self):
        string = list()
        if (len(self.c) == len(self.names)):
            for i in range(len(self.c)):
                string.append("("+self.names[i] + ", " + str(self.t[i]) + ")")
            return ".".join(string)
        else:
            for i in range(len(self.c)):
                string.append("("+str(self.c[i]) + ", " + str(self.t[i]) + ")")
            return ".".join(string)

class Phrase:
    
    
    #problem - cant have 2 diff instances
    def __init__(self, *args):
        self.n = list()
        self.t = list()
        self.key = ""
        self.type = "phrase"
        if len(args) > 0 and isinstance(args[0], Phrase):
#            if len(self.n) > 0:
#                self.empty()
            for i in range(len(args[0].n)):
                self.n.append(args[0].n[i])
                self.t.append(args[0].t[i])  
        if len(args) > 1 and isinstance(args[0], list) and isinstance(args[1], list) and len(args[0]) == len(args[1]):
            for i in range(len(args[0])):
                self.n.append(args[0][i])
                self.t.append(args[1][i])
        #initialize through 2 lists, check validity
        #initialize through copy constructor
        #isinstance, all, length
        return
    def __str__(self):
        string = list()
        for i in range(len(self.n)):
            string.append(str((self.n[i], self.t[i])))
        return ".".join(string).replace("), (", ").(")
    
    def __getitem__(self, b):
        return (self.n[b], self.t[b])
        
    def __getslice__(self, a, b): #define __len__ object for robustness
        new = Phrase()
        new.n = self.n[a:b]
        new.t = self.t[a:b]
        return new
    
    #probs
    def __add__(self, b):
        if isinstance(b, Phrase):
            new = Phrase()
            new.n = self.n + b.n
            new.t = self.t + b.t
            return new
        else:
            #throw exception
            x = 5
        return
    
    def __setitem__(self, ind, item):
        self.n[ind] = item[0]
        self.t[ind] = item[1]
        return
    
    def __len__(self):
        return len(self.n)
    
    def append(self, tup):
        self.n.append(tup[0])
        self.t.append(tup[1])
        return
    
    def insert(self, ind, tup):
        self.n.insert(ind, tup[0])
        self.t.insert(ind, tup[1])
    
    def pop(self, ind=0):
        self.n.pop(ind)
        self.t.pop(ind)
        
    def empty(self):
        del self.n[:]
        del self.t[:]
#make a key transpose    
#make an "apply to subsection" method/interface

def cycle(*args): #arguments phrase, n, [start, [stop
    p = args[0]
    n = args[1]
    if len(args) == 2 :
        j = 0
        k = len(p)
    if len(args) == 4:
        j = args[2]
        k = args[3]
    new = Phrase(p)[j:k]
    for i in range(0, n):
        new.n.insert(0, new.n.pop())
        new.t.insert(0, new.t.pop())
    return p[0:j] + new + p[k:len(p)]
    
def cycleN(*args): #arguments phrase, n, [start, [stop
    p = args[0]
    n = args[1]
    if len(args) == 2 :
        j = 0
        k = len(p)
    if len(args) == 4:
        j = args[2]
        k = args[3]
    new = Phrase(p)[j:k]
    for i in range(0, n):
        new.n.insert(0, new.n.pop())
    return p[0:j] + new + p[k:len(p)]
    
def cycleT(*args): #arguments phrase, n, [start, [stop
    p = args[0]
    n = args[1]
    if len(args) == 2 :
        j = 0
        k = len(p)
    if len(args) == 4:
        j = args[2]
        k = args[3]
    new = Phrase(p)[j:k]
    for i in range(0, n):
        new.t.insert(0, new.t.pop())
    return p[0:j] + new + p[k:len(p)]
    
def transpose(*args): #arguments phrase, n, [start, [stop
    p = args[0]
    n = args[1]
    if len(args) == 2 :
        j = 0
        k = len(p)
    if len(args) == 4:
        j = args[2]
        k = args[3]
    new = Phrase(p)[j:k]
    for i in range(0, len(new.n)):
        new.n[i] += n
    return p[0:j] + new + p[k:len(p)]

def keyTranspose(*args): #arguments phrase, n, keystring [start, [stop
    p = args[0]
    n = args[1]
    if len(args) == 3 :
        j = 0
        k = len(p)
    if len(args) == 5:
        j = args[3]
        k = args[4]
    new = Phrase(p)[j:k]
    vals = key(args[2]) #sorted(args[2].values()) for char-note dic
#    print vals
    for i in range(0, len(new)):
        
        if new.n[i] in vals:
            f = vals.index(new.n[i])
#            print "found    " + str(f)
        else:
            if new.n[i] < vals[0]:
                f = vals[0]
            if new.n[i] > vals[len(vals)-1]:
                f = vals[len(vals)-1]
            if not (new.n[i] < vals[0] or new.n[i] > vals[len(vals)-1]):
                m = 0
                while not(vals[m] < new.n[i] and new.n[i] < vals[m+1]):
                    m += 1
                f = m
#        print str(new.n[i]) + "   " + str(vals[(f+n)%len(vals)]) + "    " + str(f)
        new.n[i] = vals[(f+n)%len(vals)]
#    print new
#    print
#    print
#    print
    for i in new.n:
        if not i in vals:
            print "out of key"
    return p[0:j] + new + p[k:len(p)]
    
def retrograde(*args): #arguments phrase, [start, [stop
    p = args[0]
    if len(args) == 1:
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase(p)[j:k]
    new.n.reverse()
    new.t.reverse()
    return p[0:j] + new + p[k:len(p)]
    
def retrogradeN(*args): #arguments phrase,  [start, [stop
    p = args[0]
    if len(args) == 1 :
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase(p)[j:k]
    new.n.reverse()
    return p[0:j] + new + p[k:len(p)]
    
def retrogradeT(*args): #arguments phrase [start, [stop
    p = args[0]
    if len(args) == 1 :
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase(p)[j:k]
    new.t.reverse()
    return p[0:j] + new + p[k:len(p)]

#do or do not keep first note?            
def inversionN(*args): #arguments phrase, root, [start, [stop
    p0 = args[0]
    root = p0.n[0]
    if len(args) == 1 :
        j = 0
        k = len(p0)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    p = p0[j:k]
    new = Phrase()
    new.n.append(p.n[0])
    o = p.n[0]
    print o
    for i in range(0, len(p.n) - 1):
        print str(o) + " " + str(p.n[i]) + " " + str(p.n[i+1]) + " "
        o = (o + p.n[i] - p.n[i + 1]) % (root + 48)
        print o
#        if o < root:      why is this here? to prevent going too low? how do you set threshold?
#            o += root
        new.n.append(o)
        new.t.append(p.t[i])
    new.t.append(p.t[len(p.t) - 1])
    return p0[0:j] + new + p0[k:len(p0)]

#needs testing, handle note not in key    
def keyInvert(*args):  #arguments phrase, keystring, [start, [stop
    p0 = args[0]
    if len(args) == 2:
        j = 0
        k = len(p0)
    if len(args) == 4:
        j = args[2]
        k = args[3]
    p = p0[j:k]
    new = Phrase()
    vals = key(args[1]) #sorted(args[1].values()) for char-note dic
    root = vals.index(p.n[0])
    #print "start root" + str(root)
    new.n.append(p.n[0])
    for i in range(len(p.n) - 1):
#        if p.n[i] in vals and p.n[i+1] in vals:
#            root += vals.index(p.n[i]) - vals.index(p.n[i + 1])
        if p.n[i] in vals:
            f = vals.index(p.n[i])
        else:
            if p.n[i] < vals[0]:
                f = vals[0]
            if p.n[i] > vals[len(vals)-1]:
                f = vals[len(vals)-1]
            if not (p.n[i] < vals[0] or p.n[i] > vals[len(vals)-1]):
                m = 0
                while not(vals[m] < p.n[i] and p.n[i] < vals[m+1]):
                    m += 1
                f = m
        #print f
        if p.n[i+1] in vals:
            g = vals.index(p.n[i+1])
        else:
            if p.n[i+1] < vals[0]:
                g = vals[0]
            if p.n[i+1] > vals[len(vals)-1]:
                g = vals[len(vals)-1]
            if not (p.n[i+1] < vals[0] or p.n[i+1] > vals[len(vals)-1]):
                m = 0
                while not(vals[m] < p.n[i+1] and p.n[i+1] < vals[m+1]):
                    m += 1
                g = m
        #print g
        root += f - g
        #print "root" + str(root)
            
        new.n.append(vals[root%len(vals)])
        new.t.append(p.t[i])
    new.t.append(p.t[len(p.t) - 1])
    for i in new.n:
        if not i in vals:
            print "out of key"
    return p0[0:j] + new + p0[k:len(p0)]
        
    
    #arrithmatic or geometric differene 
def inversionT(*args):
    return

def shuffle(*args):
    p = args[0]
    if len(args) == 1:
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase()
    seg = Phrase(p)[j:k]
    nums = list()
    for i in range(len(seg)):
        nums.append(i)
    random.shuffle(nums)
    #print nums
    for i in range(len(seg)):
        new.append(seg[nums[i]])
    return p[0:j] + new + p[k:len(p)]

def shuffleN(*args):
    p = args[0]
    if len(args) == 1:
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase()
    seg = Phrase(p)[j:k]
    nums = list()
    for i in range(len(seg)):
        nums.append(i)
    random.shuffle(nums)
    #print nums
    for i in range(len(seg)):
        new.append((seg.n[nums[i]], seg.t[i]))
    return p[0:j] + new + p[k:len(p)]

def shuffleT(*args):
    p = args[0]
    if len(args) == 1:
        j = 0
        k = len(p)
    if len(args) == 3:
        j = args[1]
        k = args[2]
    new = Phrase()
    seg = Phrase(p)[j:k]
    nums = list()
    for i in range(len(seg)):
        nums.append(i)
    random.shuffle(nums)
    #print nums
    for i in range(len(seg)):
        new.append((seg.t[nums[i]], seg.n[i]))
    return p[0:j] + new + p[k:len(p)]

majPri = list()
#0,7,9,5,4,11,2
majPri.append(0)
majPri.append(12)
majPri.append(7)
majPri.append(19)
majPri.append(24)
majPri.append(31)
majPri.append(9)
majPri.append(21)
majPri.append(33)
majPri.append(5)
majPri.append(4)
majPri.append(17)
majPri.append(16)
majPri.append(29)
majPri.append(29)
majPri.append(11)
majPri.append(2)
majPri.append(14)
majPri.append(26)
majPri.append(23)
majPri.append(35)
majPri.append(36)
majPri.append(38)
majPri.append(40)
majPri.append(41)
majPri.append(43)

modes = {}
modes["ionian"] =      [0, 2, 4, 5, 7, 9, 11]
modes["dorian"] =      [0, 2, 3, 5, 7, 9, 10]
modes["phrygian"] =    [0, 1, 3, 5, 7, 8, 10]
modes["lydian"] =      [0, 2, 4, 6, 7, 9, 11]
modes["mixoldydian"] = [0, 2, 4, 5, 6, 7, 10]
modes["aeolian"] =     [0, 2, 3, 5, 7, 8, 10]
modes["locrian"] =     [0, 1, 3, 5, 6, 8, 10]
modes["major"] = modes["ionian"]
modes["minor"] = modes["aeolian"]
modes["min5"] = [0, 3, 5, 7, 10]
modes["maj5"] = [0, 2, 4, 7, 9]



roots = {}
#a thru g#
roots['ab'] = 56
roots['a'] = 57
roots['a#'] = 58
roots['bb'] = 58
roots['b'] = 59
roots['b#'] = 60
roots['cb'] = 59
roots['c'] = 60
roots['c#'] = 61
roots['db'] = 61
roots['d'] = 62
roots['d#'] = 63
roots['eb'] = 63
roots['e'] = 64
roots['e#'] = 65
roots['fb'] = 64
roots['f'] = 65
roots['f#'] = 66
roots['gb'] = 66
roots['g'] = 67
roots['g#'] = 68

dic2 ={}
#times
dic2['a'] = 4
dic2['b'] = 8
dic2['c'] = 2
dic2['d'] = 2
dic2['e'] = 2
dic2['f'] = 4
dic2['g'] = 4
dic2['h'] = 4
dic2['i'] = 8
dic2['j'] = 8
dic2['k'] = 8
dic2['l'] = 4
dic2['m'] = 2
dic2['n'] = 8
dic2['o'] = 4
dic2['p'] = 8
dic2['q'] = 2
dic2['r'] = 8
dic2['s'] = 8
dic2['t'] = 8
dic2['u'] = 8
dic2['v'] = 4
dic2['w'] = 8
dic2['x'] = 2
dic2['y'] = 2
dic2['z'] = 2


def OneCharStatMap(txt, root):
    map1 = {}
    for i in string.ascii_lowercase:
        map1[i] = 0
    for i in txt:
        if i in string.ascii_letters:
            map1[string.lower(i)] += 1
    map2 = sorted(map1, key = map1.get, reverse = True)
    for i in range(0, 26):
        map1[map2[i]] = root+majPri[i]
    return map1


def key(keystr):
    string = keystr.split(" ")
    root = roots[string[0].lower()]
    mode = modes[string[1]]
    keynotes = []
    for i in range(root-24,root+48, 12):
        for k in mode:
            keynotes.append(i+k)        
    return keynotes
        
    


def fillPhrase(phr, txt, root):
    
    phr.empty()
    cmap = OneCharStatMap(txt, root)
    l = len(txt)
    for x in range(l):
        if txt[x%l] in string.ascii_letters: 
            k = 1
            while not txt[x%l-k] in string.ascii_letters:
                k += 1 
            phr.append((cmap[txt[x%l]], dic2[txt[x%l-k]]))
    return cmap

# KEWORDS
#   toggle - should be "on" or "off" (need to enforce this) - if defined, it means chord is from a piano key down/up
#   channel - if defined, tells what channel to play object(s) on  - can be a single number (when len(args) == 1) or a list (when len(args) > 1)
# 
# ONLY BLOCK IN (obj.type == "chord") is relevant to SkipStep 
def play(*args, **kwargs):    #send object type to reciever 
    #print "                kwargs len",  len(kwargs)
#    if len(kwargs) > 0:
#        print "toggle message ", kwargs["toggle"]
#        print [i.type for i in args[0]]
        
    if "list" in kwargs.keys(): args = args[0]
    
    
    client = OSC.OSCClient()
    client.connect( ('127.0.0.1', 6449) )  
    
    for i in range(len(args)): #for multiloop, instead of i in loop, have it be the looper index, send as an arguement 
        start = OSC.OSCMessage()
        start.setAddress("start")
        start.append("started")
        client.send(start)
        
        obj = args[i]
        
        if (obj.type == "skip"):
            print "SKIPPED"
            mtype = OSC.OSCMessage()
            mtype.setAddress("type")
            mtype.append(obj.type)
            client.send(mtype)
        if(obj.type == "phrase"):
            noteA = obj.n
            timeA = obj.t
            n = len(noteA);
            print "phrase.play: " + str(n)
            print noteA
            print timeA 
            
            mtype = OSC.OSCMessage()
            mtype.setAddress("type")
            mtype.append(obj.type)
            nums = OSC.OSCMessage()
            nums.setAddress("nums" + str(i))
            nums.append(n);
            
            nums2 = OSC.OSCMessage()
            nums2.setAddress("nums2" + str(i))
            
            
            client.send(mtype)
            client.send(nums)
            for j in range(n):
                nums.clearData()
                nums.append(noteA[j])
                client.send(nums)
                nums2.clearData()
                nums2.append(timeA[j]*1.0)
                client.send(nums2)
                print noteA[j], timeA[j], "phrase data sent"
        if(obj.type == "chord"):
            objs = OSC.OSCMessage()
            objs.setAddress("objs")
            #print "args", len(args)
            if "channel" in kwargs.keys():
                if "list" in kwargs.keys() or len(args) > 1:
                    chan = kwargs["channel"][i]
                else:
                    chan = kwargs["channel"]
            else:
                chan = i
            objs.append(chan) #channel number
            
            client.send(objs)
            
            noteA = obj.n
            n = len(noteA);
            #print "chord play: " + str(n)
            #print noteA
             
            
            mtype = OSC.OSCMessage()
            mtype.setAddress("type")
            if len(kwargs) == 0 or "toggle" not in kwargs or kwargs["toggle"] == "": 
                mtype.append(obj.type)
            else:
                mtype.append(kwargs["toggle"])
                print "                           piano", kwargs["toggle"], "channel ", i 
            nums = OSC.OSCMessage()
            nums.setAddress("objLen" + str(chan)) #channel number
            nums.append(n);
            
            client.send(mtype)
            client.send(nums)
            
            #print nums.address, "  was sent yo, with val ", nums[0]
            
            nums.setAddress("nums" + str(chan)) #channel number
            #print "nums" + str(i)
            for j in range(n):
                nums.clearData()
                nums.append(noteA[j])
                client.send(nums)
                
            #print "chord data sent"
        if(obj.type == "progression"):
            n = len(obj)
            
            mtype = OSC.OSCMessage()
            mtype.setAddress("type")
            mtype.append(obj.type)
            nums = OSC.OSCMessage()
            nums.setAddress("nums" + str(i))
            nums.append(n);
            
            nums2 = OSC.OSCMessage()
            nums2.setAddress("nums2" + str(i))
            
            client.send(mtype)
            client.send(nums)
            for i in range(n):
                chordlen = len(obj.c[i])
                print "chordlen " + str(chordlen)
                print obj.t[i]
                nums.clearData()
                nums.append(chordlen)
                client.send(nums)
                nums.clearData()
                nums2.append(obj.t[i]*1.0)
                client.send(nums2)
                nums2.clearData()
                for k in range (chordlen):
                    nums.clearData()
                    nums.append(obj.c[i].n[k])
                    client.send(nums)
                    #print obj.c[i].n[k]
        
    
     
#    notes = "[" + ",".join(str(a) for a in noteA) + "] @=> int n[]; \n"
#    times = "[" + ",".join(str(a) for a in timeA) + "] @=> int t[]; \n"
#    progtxt = notes + times + open("cktxt.txt", "r").read()
#    exfile = open("exfile.ck", "w+")
#    exfile.write(progtxt)
#    exfile.close()
#    #subprocess.call("cat exfile.ck", shell=True)
#    call = subprocess.Popen("chuck exfile.ck", shell=True)
#    call.wait()
    
    
