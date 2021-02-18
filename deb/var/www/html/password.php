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
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    echo "password changed";
}
?>

<div class="container">
<form class="form" method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">

  <div class="form-group row">
    <label for="user" class="col-sm-3 col-form-label">Username:</label>
    <div class="col-sm-9">
      <input id="user" class="form-control"
        name="username" type="text" autocomplete="username" required
        value="<?=htmlspecialchars($_SERVER['PHP_AUTH_USER'])?>"/>
    </div>
  </div>

  <div class="form-group row">
    <label for="cur_pass" class="col-sm-3 col-form-label">Current Password:</label>
    <div class="col-sm-9">
      <input id="cur_pass" class="form-control"
        name="current password" type="password" autocomplete="current-password" required />
    </div>
  </div>

  <div class="form-group row">
    <label for="new_pass" class="col-sm-3 col-form-label">New Password:</label>
    <div class="col-sm-9">
      <input id="new_pass" class="form-control"
        name="new password" type="password" autocomplete="new-password" required />
    </div>
  </div>

  <div class="form-group row">
    <label for="conf_pass" class="col-sm-3 col-form-label">Confirm Password:</label>
    <div class="col-sm-9">
      <input id="conf_pass" class="form-control"
        name="confirm password" type="password" autocomplete="new-password" required />
    </div>
  </div>
  
  <div class="form-group row">
    <button type="submit" class="btn btn-primary">Change Password</button>
  </div>

</form>
</div>

<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="static/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="static/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</body>
</html>