#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
import json
import string

#Alias for name of the path
ROOT_DICT_NAME = "root"

class DCT(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def safeGet(self, key):
        """Get value from dict. Return Value or None"""
        return self.get(key, None)

    def toJSONFile(self, fname):
        """Save to JSON file"""
        with open(fname, "wt") as f:
            json.dump(self, f, sort_keys=True,
                indent=4, separators=(',', ': ') )

    def fromJSONFile(self, fname):
        """Load from JSON file"""
        with open(fname, "rt") as f:
            self = json.load(f)
        return self


class BaseHash(object):
    #object for python2.7 support
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


class SHA1Hash(BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.sha1, data)

    def new(self, data=None):
        return SHA1Hash(data)


class SHA256Hash(BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.sha256, data)

    def new(self, data=None):
        return SHA256Hash(data)


class MD5Hash(BaseHash):
    def __init__(self, data=None):
        BaseHash.__init__(self, hashlib.md5, data)

    def new(self, data=None):
        return MD5Hash(data)


class System(object):
    #object for python2.7 support
    def __init__(self, hashObj=None):
        if hashObj == None:
            self.hashObj = MD5Hash
        else:
            self.hashObj = hashObj

    def calcAllHashes(self, path):
        """Calc hashes for all files in path. Return DCT object"""
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            raise Exception('Wrong path')
        storage = DCT()
        for root, dirs, files in os.walk(path):
            relativeDir = string.replace(root, path, "")
            if relativeDir == "":
                relativeDir = ROOT_DICT_NAME
                el = storage.get(ROOT_DICT_NAME, None)
                dd = storage
            else:
                dd = storage.get(ROOT_DICT_NAME, None)
                if isinstance(dd, list):
                    ddd = {}
                    dd.append(ddd)
                    dd = ddd
                if relativeDir.startswith(os.path.sep):
                    relativeDir = relativeDir[1:]
                el = dd.get(relativeDir, None)
            if not el:
                el = []
            for name in files:
                fullPath = os.path.join(root, name)
                #We are doing something with file here
                hashValue = self.getHash(fullPath)
                fileInfo = {"fname": name,
                "fsize": self.getSize(fullPath),
                "hash": hashValue,}
                el.append(fileInfo)
            dd[relativeDir] = el
        return storage

    def comparePathwHashes(self, path, hashStorage, prevPath=""):
        """Compare files in path with hashStorage (class DCT) data."""
        if not isinstance(hashStorage, dict):
            raise Exception ('hashStorage is not DCT storage')
        if len(hashStorage) == 0:
            raise Exception ('hashStorage has no elements')
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            raise Exception ('path is no directory')
        mesLost = '{oldName:s} lost'
        keyList = list(hashStorage.keys()) #list for Py3.3
        key = keyList[0]
        el = hashStorage.get(key, None)
        if prevPath == ROOT_DICT_NAME:
            prevPath = ""
        if "fname" in keyList:
            relName = hashStorage.get("fname", None)
            fullPath = os.path.join(path, prevPath)
            name = os.path.join(fullPath, relName)
            #We have file name here
            #hashStorage equivalent (=) fileInfo dict here
            if not os.path.exists(name):
                print('File: %s lost' %name)
                return
            oldHashValue = hashStorage.get("hash", None)
            curHashValue = self.getHash(name)
            if oldHashValue != curHashValue:
                print('File: %s is not original' %name)
        if isinstance(el, list):
            for e in el:
                self.comparePathwHashes(path, e, key)

    def copyPath(self, src, dst):
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
            return
        if self.getSize(src) != self.getSize(dst):
            shutil.copyfile(src, dst)
            print('File: %s updated' %dst)
            return
        if self.getHash(src) != self.getHash(dst):
            shutil.copyfile(src, dst)
            print('File: %s updated' %dst)

    def getHash(self, fileName):
        """Get hash of file"""
        _hash = self.hashObj()
        with open(fileName, 'rb') as f:
            for line in f:
                _hash.update(line)
        return _hash.hexdigest()

    def getSize(self, fileName):
        """Get file size"""
        return os.stat(fileName).st_size


availableHash = {
    'md5': MD5Hash,
    'sha1': SHA1Hash,
    'sha256': SHA256Hash,
}

if __name__ == '__main__':
    pass