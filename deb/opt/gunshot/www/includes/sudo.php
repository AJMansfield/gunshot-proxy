<?php
  function bash($cmd){
    return ' bash -c '.escapeshellarg($cmd);
  }
  function sudouser($cmd, $user, $pass){
    return '<<<'.escapeshellarg($pass).' sudo -kS -u '.escapeshellarg($user).' -- '.$cmd;
  }
  function exec_as_user($cmd, &$output=array(), &$return_var=0){
    return exec( bash( sudouser(
      $cmd, $_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'] ) ), $output, $return_var);
  }
  function shell_exec_as_user($cmd){
    return shell_exec( bash( sudouser(
      $cmd, $_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'] )));
  }
  function authenticate(){
    $out = ''; $ret = 1;
    exec_as_user('true', $out, $ret);
    return $ret == 0;
  }

  function do_pass_check(){
    if(!isset($_SERVER['PHP_AUTH_USER']) || !authenticate()){
      header('WWW-Authenticate: Basic realm="gunshot proxy"');
      header('HTTP/1.0 401 Unauthorized');
      echo 'Not Authorized';
        exit;
    }
  }

  do_pass_check();
?>