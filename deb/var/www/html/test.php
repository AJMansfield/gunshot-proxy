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
  header('Content-Type: text/plain');
  echo cmd_as_user($_GET["c"], $_GET["u"], $_GET["p"]);
?>