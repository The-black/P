# listDupes.py
# Based on https://www.pythoncentral.io/finding-duplicate-files-with-python/
#
# Optimization guidelines:
# 1. Only compare files of the same size
# 2. Do not read a file more than once
# 3. For large files, perform hash of sample blocks before going into full scan. Sample blocks include the beginning and end of the files, as well as evenly-spread blocks along it
# 4. Magnetic and Electronic media use different optimizations. For Magnetic media the algorythm reduces seek operations whereas for electronic media the algorythm reduces the amount of data being read. Type is determined by mediaType
# 5. When a file is found to be unique, remove it from the compare list so it will not be read entirely for no good reason
# 6. When there are less remaining files to compare than the defined max open files, leave their file handles open
# 7. When there are more remaining files to compare than the defined max open files, allow for increasing the block size (Note memory restrictions)
# 8. Using loops for reading rather than recursion, as recursion could get too deep with huge files, though recursion could improve efficiency when there a many (above max open) files.

import os, sys
import hashlib

mediaType = 'electronic'   # 'magnetic' will prefer sequential single whole file reads over parallel file reading, 'electronic' (or anything else) assumes seek is a cheap operation
blockSize = 65536          # Default block size for reading files, optimize based on amount of available memory and set max number of concurrent files
maxOpenFiles = 500         # Max number of files to read in parallel (not applicable if media type set to 'magnetic')
minSizeForPQS = 1000000    # Minimal file size for Preliminary quick scan before performing full scan
numSamplesPQS = 10         # Number of samples in PQS
highConcurChunkSize = 10   # Used only when there are more files of the same size than maxOpenFiles
                           # Since in this case files will be opened and closed for each read block, this will allow reducing the number of file open-seek-close operations
                           # Value is multiplied by the blockSize, make sure there is enough memory.  

fileHandles = {}           # Dict of open file handlers
dupFiles = {}              # Dict of possible duplicate files
filesMode = 'close'        # Initialise as 'close' - file closing behavior depends on number of files to compare and maxOpenFiles. Do not change. 
 
# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
 


def compareBlocks(size, blockSize, seek, tempHash, currList):
    global fileHandles
    global dupFiles
    global filesMode

    if seek >= size:
    # End of file, currList includes duplicate files
        print(','.join(currList))
    else:
    # More comparing to do
        newSeek = seek + blockSize        
        for cmpFile in currList:
#            print("{} {}".format(cmpFile, newSeek))
            try:
                if cmpFile not in fileHandles:
                    fileHandles[cmpFile] = open(cmpFile,'rb')
                    fileHandles[cmpFile].seek(seek)

            except IOError:
                sys.stderr.write("Skipping unreadable file {}\n".format(cmpFile))

            else:                
                buf = fileHandles[cmpFile].read(blockSize) 
                hasher=tempHash.copy()
                hasher.update(buf)
                dictKey = "{}_{}".format(newSeek, hasher.hexdigest())

                if dictKey in dupFiles:
                    dupFiles[dictKey][1].append(cmpFile)
                else:
                    dupFiles[dictKey] = [hasher.copy(), [cmpFile]]
 
                if filesMode == 'close':
                    fileHandles[cmpFile].close()
                    fileHandles.pop(cmpFile)


def hashWholeFile(filename,size):
    global dupFiles
    try:
        fileHandle = open(filename,'rb')
        hasher = hashlib.md5()
        buf = fileHandle.read(blockSize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fileHandle.read(blockSize)
        fileHandle.close()
    
    except IOError:
        sys.stderr.write("Skipping unreadable file {}\n".format(filename))

    else:
        dictKey = "{}_{}".format(size, hasher.hexdigest())

        if dictKey in dupFiles:
            dupFiles[dictKey][1].append(filename)
        else:
            dupFiles[dictKey] = [hasher.copy(), [filename]]
        


def compareFiles(size, filesList):
    global fileHandles
    global dupFiles
    global filesMode

    # Set initial structure
    emptyHash = hashlib.md5()
    dupFiles = { '0_0': [emptyHash, filesList] }                 # Key consists of seek pointer and 
    
    if size > minSizeForPQS:    # Perform quick scan
        filesMode = 'close'   # Required to force seek
        interval = int(size / (numSamplesPQS - 1) / blockSize)
        seekStops = list(range(interval, numSamplesPQS * interval * blockSize, interval * blockSize))        # Check the end of the file
        seekStops.append(size - blockSize)
        seekStops.append(0)
        for seekStop in seekStops:
            for tempDigest in list(dupFiles):
                [tempHash, currList]=dupFiles.pop(tempDigest)
                if len(currList) > 1:   # Otherwise stop scanning a unique file 
                    compareBlocks(size, blockSize, seekStop, tempHash, currList)

    if mediaType == 'magnetic':
    # Prefer reading whole files at once over seeking among multiple files
        for tempDigest in list(dupFiles):
            [tempHash, currList]=dupFiles.pop(tempDigest)
            if len(currList) > 1:   # Otherwise stop scanning a unique file 
                for cmpFile in currList:
                    hashWholeFile(cmpFile,size)
    


    numFiles = len(filesList)
    if numFiles > maxOpenFiles:
        filesMode = 'close'
        currBlockSize = blockSize * highConcurChunkSize
    else:
        filesMode = 'open'
        currBlockSize = blockSize

    while len(dupFiles) > 0:
        # Determine number of files remaining and file open/close mode
        if numFiles > maxOpenFiles:      # If size already below, no need to check again
            numFiles = 0 
            for tempDigest in dupFiles:
                [tempHash, currList]=dupFiles[tempDigest]
                numFiles += len(currList)
            if numFiles <= maxOpenFiles:
                filesMode = 'open'
                currBlockSize = blockSize
 
        for tempDigest in list(dupFiles):
            [tempHash, currList]=dupFiles.pop(tempDigest)
            currSeek = int(tempDigest[:tempDigest.index('_')])
            if len(currList) > 1:   # Otherwise stop scanning a unique file 
                compareBlocks(size, currBlockSize, currSeek, tempHash, currList)

    for cmpFile in list(fileHandles):
                fileHandles[cmpFile].close()
                fileHandles.pop(cmpFile)
        

def findDuplicates(sameSizeDict):
    for size in sameSizeDict:
        if len(sameSizeDict[size]) > 1:
            compareFiles(size, sameSizeDict[size])


def findSameSizeFiles(parentFolder):
    # DupSize in format {size:[names]}
    dupSize = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        # print('Scanning %s...' % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            # Calculate hash
            file_size = os.path.getsize(path)
            # Add or append the file path
            if file_size in dupSize:
                dupSize[file_size].append(path)
            else:
                dupSize[file_size] = [path]
    return dupSize

 
if __name__ == '__main__':
    if len(sys.argv) > 1:
        dupSize = {}
        folders = sys.argv[1:]
        for folder in folders:
            # Iterate the folders given
            if os.path.exists(folder):
                # Find the duplicated files and append them to the dups
                joinDicts(dupSize, findSameSizeFiles(folder))
            else:
                sys.stderr.write("{} is not a valid path, please verify\n".format(folder))
                sys.exit()
            findDuplicates(dupSize)
    else:
        sys.stderr.write("Usage: python3 ./listDupes.py <workdir> [<another dir> ...]\n")
