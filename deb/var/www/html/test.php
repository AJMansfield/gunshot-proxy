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
    return bash('<<<'.$pass.$nl.$newpass.$nl.$newpass.' sudo -kS -u '.$user.' -- passwd');
  }
  header('Content-Type: text/plain');
  echo chpasswd($_GET["u"], $_GET["p"], $_GET["n"]);
?>