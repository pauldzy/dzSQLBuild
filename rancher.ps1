#!powershell

$cuid='1000:1000' 

$targ = $args[0]
$targ = $targ.Replace('C:\','/mnt/c/')
$targ = $targ.Replace('D:\','/mnt/d/')
$targ = $targ.Replace('\','/')

$gitt = $args[1]
$gitt = $gitt.Replace('C:\','/mnt/c/')
$gitt = $gitt.Replace('D:\','/mnt/d/')
$gitt = $gitt.Replace('\','/')

$mloc = split-path -parent $PSCommandPath
$mloc = $mloc.Replace('C:\','/mnt/c/')
$mloc = $mloc.Replace('D:\','/mnt/d/')
$mloc = $mloc.Replace('\','/')

& rdctl shell sh -c "CURRENT_UID=`"$cuid`" TARGET=`"$targ`" GITTRG=`"$gitt`" docker-compose -f $($mloc)/docker-compose.yml up"
