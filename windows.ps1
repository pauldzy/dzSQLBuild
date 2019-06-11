
$env:CURRENT_UID='1000:1000' 
$env:TARGET=$args[0]

& 'docker-compose' 'up'
