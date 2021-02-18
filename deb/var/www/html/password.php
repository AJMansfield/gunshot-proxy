<?php
require 'includes/sudo.php';

function chpasswd($user, $curpass, $newpass){

  $nl = '$\'\\n\''; //fully-escaped newline for herestring concatenation

  $sudo_user = escapeshellarg($_SERVER['PHP_AUTH_USER']);
  $sudo_pass = escapeshellarg($_SERVER['PHP_AUTH_PW']);

  $user = escapeshellarg($user);
  $curpass = escapeshellarg($curpass);
  $newpass = escapeshellarg($newpass);

  // herestring is: {sudo passwd}\n{current password for password channge}\n{enter new password}\c{confirm new password}
  return bash('<<<'.$sudo_pass.$nl.$curpass.$nl.$newpass.$nl.$newpass.' sudo -kS -u '.$sudo_user.' -- passwd '.$user);
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

<pre><code>
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  // verify requested user is same as logged-in user
  $command = chpasswd($_POST["user"], $_POST["curpass"], $_POST["newpass"]);

  echo '$ passwd '.htmlspecialchars($user)."\n";

  $output = array();
  $return = 0;

  $lastline = exec($command, $output, $return);

  echo htmlspecialchars($lastline);
}
?>
</code></pre>

<div class="container">
<form class="form" method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">

  <div class="form-group row">
    <label for="user" class="col-sm-3 col-form-label">Username:</label>
    <div class="col-sm-9">
      <input id="user" class="form-control"
        name="user" type="text" autocomplete="username" required readonly
        value="<?=htmlspecialchars($_SERVER['PHP_AUTH_USER'])?>"/>
    </div>
  </div>

  <div class="form-group row">
    <label for="curpass" class="col-sm-3 col-form-label">Current Password:</label>
    <div class="col-sm-9">
      <input id="curpass" class="form-control"
        name="curpass" type="password" autocomplete="current-password" required />
    </div>
  </div>

  <div class="form-group row">
    <label for="newpass" class="col-sm-3 col-form-label">New Password:</label>
    <div class="col-sm-9">
      <input id="newpass" class="form-control"
        name="newpass" type="password" autocomplete="new-password" required />
    </div>
  </div>

  <div class="form-group row">
    <label for="conpass" class="col-sm-3 col-form-label">Confirm Password:</label>
    <div class="col-sm-9">
      <input id="conpass" class="form-control"
        name="conpass" type="password" autocomplete="new-password" required />
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