#! /bin/sh


ROOTDIR=/tmp/mylittledir
DIR1=$ROOTDIR/onemoredir
DIR2=$ROOTDIR/onemoredir/andevenonemorelevel
DIR3=$ROOTDIR/yetanotherdir

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


