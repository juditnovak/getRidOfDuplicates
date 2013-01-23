#! /usr/bin/python


import hashlib
import os, sys, shutil
import logging
import re



class FileDuplicates:



    logging.basicConfig(format="%(levelname)s:%(filename)s::%(funcName)s %(message)s")
    logger=logging.getLogger('ProcessDirs')
    logger.setLevel(logging.DEBUG)
    
    # Dictionary of affected devices 
    devices={}


    def __init__(self, topdir):
        try:
            self.topdir=topdir
            self.dirs = os.walk(self.topdir, followlinks=True)
            self.arethesame={}
            self.arethesame_perdevice={}
            self.actual_files=[]
            self.actual_dir=[]

        except OSError, e:
           self.logger.error("0!s".format(e)) 



    def __iter__(self):
    # It's an iterator!
        return self



    def next(self):
    # Raising next element of the dir. tree

        actual_file=""
        while not (actual_file and os.path.isfile(actual_file) and not os.path.islink(actual_file)):
            while not self.actual_files:
                (self.actual_dir, subdirs, self.actual_files) = self.dirs.next()
            actual_file=os.path.join(self.actual_dir, self.actual_files.pop(0))
        self.logger.debug("{0!s}".format(actual_file))
        return actual_file



    def dispDirContents(self):
            for (dirpath, dirnames, filenames) in self.dirs:
                sys.stdout.write("{0} contains:\n".format(dirpath))
                sys.stdout.write("{0!s}\n".format(filenames))
                      


    def collectSame(self):
    # Putting files with the same sha1 value in a dict.

        for filename in self:

            try: 
                file = open(filename, 'rb')
                filecontents = file.read()
            except IOError, e:
                self.__class__.logger.error("{0!s} -- (skipped)".format(e))
                continue

            shaval = hashlib.sha1(filecontents).hexdigest()
            file.close()
            if shaval in self.arethesame:
                self.arethesame[shaval].append(filename)
            else:
                self.arethesame[shaval]=[filename]
        keys = self.arethesame.keys()
        for shaval in keys:
            if not self.arethesame[shaval] or len(self.arethesame[shaval]) == 1:
                del self.arethesame[shaval]
        self.logger.debug("{0!r}".format(self.arethesame))

    

    def groupSamePerDev(self):
    # Create unite the identical files in case they are on the same filesystem

        for shaval in self.arethesame:

            samelist=self.arethesame[shaval]
            stdevdict={}
            for filepath in samelist:

                device = os.stat(filepath).st_dev
                minor=os.minor(device)
                major=os.major(device)
                devname=None

                pat=re.compile("^\s+{0!s}\s+{1!s}\s+\d+\s+(?P<devname>\w+)".format(major, minor))
                partitions=open('/proc/partitions', 'r')
                for line in partitions:
                    s=pat.search(line)
                    if s is not None:
                        devname=s.group('devname')
                partitions.close()

                pat2=re.compile("^[\w/:]+{0!s}\s+(?P<mountpoint>[\w/]+)\s+(?P<filesystem>\w+)".format(devname))
                mtab=open('/etc/mtab', 'r')
                for line in mtab:
                    s=pat2.search(line)
                    if s is not None:
                        filesystem=s.group('filesystem')
                        mountpoint=s.group('mountpoint')
                mtab.close()

                self.devices[device]=(devname, filesystem, mountpoint)

                if device in stdevdict:
                    stdevdict[device].append(filepath)
                else:
                    stdevdict[device]=[filepath]

            devices=stdevdict.keys()
            for device in devices:
                if len(stdevdict[device]) < 2:
                    del stdevdict[device]
            
            self.arethesame_perdevice[filepath]=stdevdict        
        self.logger.debug("Files grouped per device: {0!r}".format(self.arethesame_perdevice))




    def hardlinkSame(self):
    # Set up hard links to replace file duplicates (per filesystem)

        for filepath in self.arethesame_perdevice:
            for dev in self.arethesame_perdevice[filepath]:

                idlist=self.arethesame_perdevice[filepath][dev]

                # Making sure that 'dev' is not VFAT/NTFS, where links are not allowed
                # By concept arethesame_perdevice should contain all instances 
                # so we don't remove them from the dict just skip
                if re.compile("ntfs|vfat").match(self.devices[dev][1]):
                    self.logger.error("Can't create hard links on {0}, skipping device {1}".format(self.devices[dev][1], format(self.devices[dev][2])))
                    continue

                # The copy to keep
                remaining=""
                if filepath in idlist:
                    remaining=filepath
                    idlist.remove(filepath)
                else:
                    remaining=idlist.pop(0)
        
                while not os.access(remaining, os.W_OK):
                    self.logger.error("Can't write/remove {0}".format(remaining))
                    remaining=idlist.pop(0)

                for idfile in idlist:
                    if not os.access(idfile, os.W_OK):
                        self.logger.error("Can't write/remove {0}".format(idfile))
                        idlist.remove(idfile)
                        continue
                    tmpfile=idfile + ".orig"
                    self.logger.debug("Moving {0} to {1} (temp file)".format(idfile, tmpfile))
                    shutil.move(idfile, tmpfile)
                    self.__class__.logger.debug("Linking {0} to {1} (temp file)".format(idfile, remaining))
                    os.link(remaining, idfile)
                    self.__class__.logger.debug("Deleting temp file {0}".format(tmpfile))
                    os.unlink(tmpfile)

                # In case this was not on the same device as 'filepath' variable 
                # (practically: member of another device's list), now there's no record of it!
                if filepath != remaining:
                    idlist.append(remaining)

        # Now the lists only contains files that we had access for, that we dealt with
        self.__class__.logger.debug("Files grouped per device: {0!r}".format(self.arethesame_perdevice))






