#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
import json

class DCT (object):
    _dct = dict()
    
    def __init__ (self):
        pass

    def set (self, key, value):
        """Set value to dict"""
        self._dct[key]= value

    def get (self, key):
        """Get value from dict"""
        return self._dct.get(key, '')

    def toFile (self, fname, delimeter= ' ', end= '\n'):
        with open(fname, "wt") as f:
            f.write(self.__str__() )

    def fromFile (self, fname, delimeter= ' ', end= '\n'):
        with open(fname, "rt") as f:
            for line in f:
                line = line.rstrip([end,])
                key, value = line.split(delimeter)
                self.set(key, value)

    def toJSONFile (self, fname):
        with open(fname, "wt") as f:
            json.dump(self._dct, f, sort_keys=True,
                indent=4, separators=(',', ': ') )

    def fromJSONFile (self, fname):
        with open(fname, "rt") as f:
            self._dct = json.load(f)

    def __str__ (self, delimeter= ' ', end= '\n'):
        s_list = []
        table = {'del': delimeter, 'end': end}
        for key in self._dct.keys():
            table.update({'hash': value, 'fname': self._dct[key]})
            s= '{fname:s}{del:s}{hash:s}{end:s}'.format(**table)
            s_list.append(s)
        return end.join(s_list)

    __repr__ = __str__


class BaseHash:
    def __init__ (self, hashFactory, data=None):
        if hasattr(hashFactory, 'new'):
            self._hash = hashFactory.new()
        else:
            self._hash = hashFactory()
        if data:
            self.update(data)

    def update(self, data):
        return self._hash.update(data)

    def hexdigest(self):
        return self._hash.hexdigest()


class SHA1Hash (BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.sha1, data)

    def new(self, data=None):
        return SHA1Hash(data)


class SHA256Hash (BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.sha256, data)

    def new(self, data=None):
        return SHA256Hash(data)


class MD5Hash (BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.md5, data)

    def new(self, data=None):
        return MD5Hash(data)


class System:
    def __init__ (self, hashObj=None):
        if hashObj == None:
            self.hashObj = MD5Hash()
        else:
            self.hashObj = hashObj

    def walk (self, path):
        for root, dirs, files in os.walk(path):
            for name in files:
                fullPath = os.path.join(root, name)
                foo()

    def foo (self):
        pass

    def copyFile(self, source, dest, u=False):
        if u:
            if size1 > size2:
                shutil.copyfile(source, dest)
                #log
            else:
                if getHash(source) != getHash(dest):
                    shutil.copyfile(source, dest)
                    #log
        else:
            shutil.copyfile(source, dest)
            #log

    def getHash(self, fname):
        with open(fname, 'rb') as f:
            for line in f:
                self.hashObj.update(line)
        return self.hashObj.hexdigest()


def main():
    pass

if __name__ == '__main__':
    main()