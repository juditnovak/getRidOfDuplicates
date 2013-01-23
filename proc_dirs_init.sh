#! /bin/sh


ROOTDIR=/tmp/mylittledir
ROOTDIR2=/tmp/mylittledir_copy
DIR1=$ROOTDIR/onemoredir
DIR2=$ROOTDIR/onemoredir/andevenonemorelevel
DIR3=$ROOTDIR/yetanotherdir
DIR4=$ROOTDIR/otherfsdir
DIR5=$ROOTDIR/otherfsdir/otherfs2ndlev

rm -fr $ROOTDIR


mkdir $ROOTDIR

cp /etc/passwd $ROOTDIR
cp $ROOTDIR/passwd $ROOTDIR/passwd_other

mkdir -p $DIR1 $DIR2 $DIR3

echo "Bela" > $DIR1/testfile
ln -s $DIR1/testfile $DIR2
cp $DIR1/testfile $DIR3


cp $ROOTDIR/passwd $DIR3/passwd_yetanother

ln -s $DIR3/passwd_yetanother $DIR1 

echo "Geza" > $ROOTDIR/singlefile
ln -s $ROOTDIR/singlefile $DIR2


ln -s "/mnt/usbhd-sdc1/test" $DIR4 
mkdir $DIR5

cp $ROOTDIR/passwd $DIR4
cp $ROOTDIR/passwd $DIR4/passwd_yetanother_otherfs
cp $ROOTDIR/passwd $DIR5/passwd_yetanother_otherfs

mkdir -p $ROOTDIR2
cp $ROOTDIR/passwd $ROOTDIR2
cp $ROOTDIR/passwd $ROOTDIR2/passwd2
cp -r $DIR3 $ROOTDIR2
cp -r $DIR2 $ROOTDIR2




