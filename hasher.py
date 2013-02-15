#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
import json
import string

class DCT (object):
    #object for python2.7 support
    _dct = dict()

    def __init__ (self):
        pass

    def set (self, key, value):
        """Set value to dict"""
        self._dct[key]= value

    def get (self, key):
        """Get value from dict"""
        return self._dct.get(key, None)

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

    def clear (self):
        self._dct.clear()

    def size (self):
        return len(self._dct)

    __len__ = size


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
            self.hashObj = MD5Hash
        else:
            self.hashObj = hashObj

    def calcAllHashes (self, path):
        """Calc hashes for all files in path. Return DCT object"""
        if not os.path.isdir(path):
            raise Exception('Wrong path')
        storage = DCT()
        for root, dirs, files in os.walk(path):
            for name in files:
                fullPath = os.path.join(root, name)
                hashValue = getHash(fullPath)
                storage.set(hashValue, name)
        return storage

    def comparePathwHashes (self, path, hashStorage):
        """Compare files in path with hashStorage (class DCT) data."""
        if not isinstance(hashStorage, DCT):
            raise Exception ('hashStorage is not DCT storage')
        if hashStorage.size() == 0:
            raise Exception ('hashStorage has no elements')
        if not os.path.isdir(path):
            raise Exception ('path is no directory')
        mesMod = '{oldName:s} -> {newName:s} ({hashValue:s})'
        mesLost = '{oldName:s} lost'
        num = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                fullPath = os.path.join(root, name)
                num += 1
                hashValue = getHash(fullPath)
                oldName = hashStorage.get(hashValue)
                if not oldName:
                    table = {'oldName': oldName, 'hashValue': hashValue}
                    mes = mesLost.format(**table)
                    print(mes)
                if oldName != name:
                    table = {'oldName': oldName,
                    'hashValue':hashValue,
                    'newName':name }
                    mes = mesMod.format(**table)
                    print(mes)
        if num < hashStorage.size():
            delta = hashStorage.size() - num
            print('Num %d files be losted or been modified' %delta)

    def copyPath (self, src, dst):
        """Copy all files from path src to dst"""
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        if not os.path.isdir(src):
            raise Exception ('src is no directory')
        if not os.path.exists(dst):
            os.mkdir(dst)
        for root, dirs, files in os.walk(src):
            newDir = string.replace(root, src, dst)
            newPath = os.path.join(dst, newDir)
            for name in files:
                fullPath = os.path.join(root, name)
                if not os.path.exists(newPath):
                    os.mkdir(newPath)
                newPath = os.path.join(newPath, name)
                self.copyFile(fullPath, newPath)

    def copyFile(self, src, dst):
        """Copy src file to dst"""
        if not os.path.isfile(src):
            raise Exception('Not a file: %s' %src)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
            print('File: %s created' %dst)
        else:
            if self.getSize(src) > self.getSize(dst):
                shutil.copyfile(src, dst)
                print('File: %s updated' %dst)
            else:
                if self.getHash(src) != self.getHash(dst):
                    shutil.copyfile(src, dst)
                    print('File: %s updated' %dst)

    def getHash(self, fileName):
        _hash = self.hashObj()
        with open(fileName, 'rb') as f:
            for line in f:
                _hash.update(line)
        return _hash.hexdigest()

    def getSize (self, path):
        """Get File size"""
        return os.stat(path).st_size


availableHash = {
    'md5': MD5Hash,
    'sha1': SHA1Hash,
    'sha256': SHA256Hash,
}

if __name__ == '__main__':
    pass