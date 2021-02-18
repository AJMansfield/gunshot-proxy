<?php
  function bash($cmd){
    return ' bash -c '.escapeshellarg($cmd);
  }
  function sudouser($cmd, $user, $pass){
    return '<<<'.escapeshellarg($pass).' sudo -kS -u '.escapeshellarg($user).' -- '.$cmd;
  }
  function cmd_as_user($cmd, $user, $pass){
    return bash(sudouser($cmd, $user, $pass));
  }
  function bcmd_as_user($cmd, $user, $pass){
    return bash(sudouser(bash($cmd), $user, $pass));
  }
  function chpasswd($user, $pass, $newpass){
    $nl = '$\'\\n\''; //fully-escaped newline for herestring concat
    $user = escapeshellarg($user);
    $pass = escapeshellarg($pass);
    $newpass = escapeshellarg($newpass);
    // herestring is: {sudo passwd}\n{current password for password channge}\n{enter new password}\c{confirm new password}
    return bash('<<<'.$pass.$nl.$pass.$nl.$newpass.$nl.$newpass.' sudo -kS -u '.$user.' -- passwd');
  }

  // parsing results from 
  header('Content-Type: text/plain');
  echo chpasswd($_GET["u"], $_GET["p"], $_GET["n"]);
?>