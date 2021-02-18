<?php
require 'includes/sudo.php';

function chpasswd($user, $pass, $newpass){
  $nl = '$\'\\n\''; //fully-escaped newline for herestring concat
  $user = escapeshellarg($user);
  $pass = escapeshellarg($pass);
  $newpass = escapeshellarg($newpass);
  // herestring is: {sudo passwd}\n{current password for password channge}\n{enter new password}\c{confirm new password}
  return bash('<<<'.$pass.$nl.$pass.$nl.$newpass.$nl.$newpass.' sudo -kS -u '.$user.' -- passwd');
}

?>
<!doctype html>
<html lang="en">
<head>
  <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

  <!-- Bootstrap CSS -->
  <link rel="stylesheet" href="static/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">

  <!-- jQuery -->
  <script src="static/jquery-3.4.1.min.js"></script>

  <title>Gunshot Detector Password Change</title>
</head>
<body>

<?php
ini_set('display_errors',1); error_reporting(E_ALL);
?>

<?php
if (!function_exists('is_iterable')) { // fix for PHP < 7.1.0
  function is_iterable($var)
  {
      return is_array($var) || $var instanceof \Traversable;
  }
}
?>

<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    echo "password changed"
}
?>

<div class="container">
  <form class="form" method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">

  <label for="user">Username:</label>
  <input id="user" name="username" type="text" autocomplete="username" required value="<?=htmlspecialchars($_SERVER['PHP_AUTH_USER'])?>"/>

  <label for="cur_pass">Current Password:</label>
  <input type="password" id="cur_pass" name="current password" autocomplete="current-password" required>

  <label for="new1_pass">New Password:</label>
  <input type="password" id="pass" name="new password" autocomplete="new-password" required>

  <label for="new2_pass">Confirm Password:</label>
  <input type="password" id="pass" name="confirm new password" autocomplete="new-password" required>
  
  <button type="submit">Change Password</button>
  </form>
</div>

<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="static/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="static/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</body>
</html>