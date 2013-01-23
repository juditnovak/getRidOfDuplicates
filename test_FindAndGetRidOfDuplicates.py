#! /usr/bin/python

import unittest
import os
import hashlib
import re

from FindAndGetRidOfDuplicates import FileDuplicates



class testFileDuplicatesCase(unittest.TestCase):



    def setUp(self):
        self.dirobj=FileDuplicates('/tmp/mylittledir')


    def testDispDirContents(self):
        self.dirobj.dispDirContents()


    def testIter(self):
    # All strings coming from the iterator should correspond to an existing file

        for file in self.dirobj:
            self.failUnless( os.path.exists(file) and os.path.isfile(file) and not os.path.islink(file))
        

    def testSame(self):
        self.dirobj.collectSame()
        for shaval in self.dirobj.arethesame:
            samelist = self.dirobj.arethesame[shaval]
            file = open(samelist.pop(0), 'rb').read()
            shaval = hashlib.sha1(file).hexdigest()
            for filename in samelist:
                file = open(filename, 'rb')
                filecontents = file.read()
                cur_shaval = hashlib.sha1(filecontents).hexdigest()
                file.close()
                self.failIf(cur_shaval != shaval)
                

                
    def testSamePerDev(self):
    # Checking invariants for the new data structure (dirobj.arethesame_perdevice)

        self.dirobj.collectSame()
        self.dirobj.groupSamePerDev()
        sameperdev=self.dirobj.arethesame_perdevice
        shavarl=""
        for filepath in sameperdev:
            with open(filepath, 'rb') as fh:
                filecontents=fh.read()
                shaval=hashlib.sha1(filecontents).hexdigest()

            for dev in sameperdev[filepath]:
                for idfilepath in sameperdev[filepath][dev]:

                    # Are the files really on the same device?
                    self.failIf(os.stat(idfilepath).st_dev != dev)
            
                    # To they have the same SHA1 value?
                    idshaval=""
                    with open(idfilepath, 'rb') as idfh:
                        idfilecontents=idfh.read()
                        idshaval=hashlib.sha1(idfilecontents).hexdigest()
                    self.failIf(idshaval != shaval)


    def testHardlinkSame(self):
    # Finally: checking if hard link creation went fine

        self.dirobj.collectSame()
        self.dirobj.groupSamePerDev()
        self.dirobj.hardlinkSame()

        for filepath in self.dirobj.arethesame_perdevice:

            for dev in self.dirobj.arethesame_perdevice[filepath]:

                if re.compile("ntfs|vfat").match(self.dirobj.devices[dev][1]):
                    continue

                pathperdevlist=self.dirobj.arethesame_perdevice[filepath][dev]
                rootlink=filepath
                if not os.access(filepath, os.W_OK) or dev !=os.stat(filepath).st_dev:
                    rootlink=pathperdevlist[0]
                rootinode=os.stat(rootlink).st_ino
                for curfilepath in pathperdevlist:

                    # Fail if the list contains a file that we couldn't have modified
                    self.failIf(not os.access(curfilepath, os.W_OK))
                    self.failUnless(rootinode == os.stat(curfilepath).st_ino)
        



def main():

    suite=unittest.TestSuite()
#    suite.addTest(testFileDuplicatesCase('testDispDirContents'))
    suite.addTest(testFileDuplicatesCase('testIter'))
    suite.addTest(testFileDuplicatesCase('testSame'))
    suite.addTest(testFileDuplicatesCase('testSamePerDev'))
    suite.addTest(testFileDuplicatesCase('testHardlinkSame'))
    unittest.TextTestRunner(verbosity=2).run(suite)



if __name__ == '__main__':
    main()
