import os
import shutil
import subprocess
from urllib import request
import tarfile
import zipfile

from constants import KEYS, TYPES
from tools import js, files, tools, httpy

class MyBuilderBase:

    createFunc = None

    def __init__(self, buildType, *args):
        buildType = buildType.lower()
        self._separator = tools.get_separator()
        self._printTag = f"[build_{buildType}_tool]"
        self._projDir = os.getcwd() + self._separator
        self._rootDir = os.path.join(os.path.dirname(__file__), "..") + self._separator
        self._workDir = os.path.join(self._rootDir, "build") + self._separator
        self._buildDir = os.path.join(self._workDir, f"{buildType}_dir") + self._separator
        self._cacheDir = os.path.join(self._workDir, "cache") + self._separator
        self._libsDir = os.path.join(self._workDir, f"{buildType}_libs") + self._separator
        files.mk_folder(self._cacheDir)
        files.mk_folder(self._libsDir)
        self._needUpdate = False
        self._name = "UNKNOWN"
        self._isDebug = False
        self._isRelease = False
        self._inputNames = []
        self._inputFiles = []
        self._outputFile = None
        files.mk_folder(self._buildDir)
        MyBuilderBase.createFunc(self, *args)
        print(f"\n-----------------[JS {buildType} Builder]---------------------\n")
        self._print("PROJ_DIR", self._projDir)
        self._print("ROOT_DIR", self._rootDir)
        self._print("WORK_DIR", self._workDir)

    def _print(self, *args):
        print(self._printTag, self._name, *args)

    def _assert(self, v, msg):
        if not v:
            raise Exception(f"{self._printTag} {self._name} {msg}")

    def _error(self, msg):
        raise Exception(f"{self._printTag} {self._name} {msg}")

    def _downloadByGit(self, url, branch, directory):
        if not files.is_folder(directory):
            self._print('cloning...')
            cmd = f"git clone {url} {directory} --branch {branch} --single-branch"
            isOk, err = tools.execute(cmd)
            self._assert(isOk, f"git clone failed, err: {str(err)}")
        elif self._needUpdate:
            self._print('pulling...')
            cmd = f"cd {directory} && git pull"
            isOk, err = tools.execute(cmd)
            self._assert(isOk, f"git pull failed: {str(err)}")

    def _downloadByTar(self, url, directory):
        if files.is_folder(directory):
            self._print('downloaded!')
            return
        cacheFile = self._downloadByUrl(url)
        self._print('untarring...')
        files.mk_folder(directory)
        with tarfile.open(cacheFile, "r:gz") as tar:
            tar.extractall(path=directory)
        files.delete(cacheFile)
        self._print("untar succeeded!")

    def _downloadByZip(self, url, directory):
        if files.is_folder(directory):
            self._print('downloaded!')
            return
        cacheFile = self._downloadByUrl(url)
        self._print('unzipping...')
        files.mk_folder(directory)
        with zipfile.ZipFile(cacheFile, 'r') as zip_ref:
            zip_ref.extractall(directory)
        files.delete(cacheFile)
        self._print("unzip succeeded!")

    def _downloadByGzip(self, url, directory):
        if files.is_folder(directory):
            self._print('downloaded!')
            return
        cacheFile = self._downloadByUrl(url)
        self._print('gunzipping...')
        files.mk_folder(directory)
        with tarfile.open(cacheFile, "r:gz") as tar:
            tar.extractall(path=directory)
        files.delete(cacheFile)
        self._print("gunzip succeeded!")

    def _downloadByUrl(self, url, path=None):
        parts = url.split(".")
        ext = parts[-1]
        cacheFile = path or os.path.join(self._cacheDir, f"temp.{ext}")
        files.delete(cacheFile)
        self._print('downloading ...')
        isOk, err = httpy.download(url, cacheFile)
        if not isOk or files.size(cacheFile) <= 0:
            files.delete(cacheFile)
            self._error(f'download failed, err: {str(err)}')
        self._print('download succeeded.')
        return cacheFile

    def _readFile(self, path, isOnlyLocal, encoding="utf-8"):
        self._print(f"read file: {path}")
        isRemote = path.startswith("http")
        self._print(f"is remote: {str(isRemote)}")
        if isRemote:
            if isOnlyLocal:
                self._print("skip remote.")
                return
            self._print("downloading remote ...")
            path = self._downloadByUrl(path)
        self._assert(files.is_file(path), f"file not found: {path}")
        self._print("reading file ...")
        content = files.read(path, encoding)
        if isRemote:
            files.delete(path)
        self._assert(len(content) > 0, f"read file failed!, path: {path}")
        self._print("read file succeeded!")
        return content

    def setName(self, name):
        js.assert(js.is_text(name), 'invalid task name for builder')
        self._name = name

    def getName(self):
        return self._name

    def setDebug(self, value):
        js.assert(isinstance(value, bool), 'invalid task name for builder')
        self._isDebug = value

    def setRelease(self, value):
        js.assert(isinstance(value, bool), 'invalid task name for builder')
        self._isRelease = value

    def setInput(self, *args):
        self._print("input files ...")
        self._assert(len(self._inputFiles) == 0, "input files are already defined")
        inputArr = list(args)
        for v in inputArr:
            path = v
            if not files.is_file(path):
                path = os.path.join(self._projDir, v)
            self._assert(files.is_file(path) or files.is_folder(path), f"input file not found: {v}")
            self._print(f"input path: {v}")
            self._inputNames.append(v)
            self._inputFiles.append(path)
        return self

    def setOutput(self, path):
        self._print("output file ...")
        self._assert(self._outputFile is None, "output file is already defined")
        self._print(f"output file: {path}")
        self._outputFile = os.path.join(self._projDir, path)
        return self

    def _processBuild(self):
        self._error("please implement start func ...")

    def start(self):
        self._print('BUILD START:')
        self._processBuild()
        self._print('BUILD END!\n')
        return self


