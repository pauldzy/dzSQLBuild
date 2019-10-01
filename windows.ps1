
$env:CURRENT_UID='1000:1000' 
$env:DZGITLOC=$args[0]
$env:DZSUBDIR=$args[1]

& 'docker-compose' 'up'
