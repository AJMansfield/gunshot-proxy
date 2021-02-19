<?php
require 'includes/sudo.php';

function chpasswd($user, $curpass, $newpass1, $newpass2){

  $nl = '$\'\\n\''; //fully-escaped newline for herestring concatenation

  $sudo_user = escapeshellarg($_SERVER['PHP_AUTH_USER']);
  $sudo_pass = escapeshellarg($_SERVER['PHP_AUTH_PW']);

  $user = escapeshellarg($user);
  $curpass = escapeshellarg($curpass);
  $newpass1 = escapeshellarg($newpass1);
  $newpass2 = escapeshellarg($newpass2);


  // herestring is: {sudo passwd}\n{current password for password channge}\n{enter new password}\c{confirm new password}
  return bash('2>&1 <<<'.$sudo_pass.$nl.$curpass.$nl.$newpass1.$nl.$newpass2.' sudo -kS -u '.$sudo_user.' -- passwd '.$user);
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


<div class="container">
  <div class="pb-2 mt-4 mb-2 border-bottom">
    <h1>User Management</h1>
  </div>
  <div class="card">
    <div class="card-body">
      <a href="index.php" class="btn btn-primary">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
        </svg>
        Proxy Configuration
      </a>
    </div>
  </div>
  <form class="form" method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">
    <div class="card">
      <div class="card-header h4">Change Password</div>
      <div class="card-body">
        <div class="form-group row">
          <label for="user" class="col-4 col-md-3 col-lg-2 col-form-label text-right">Username:</label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="user" class="form-control"
              name="user" type="text" autocomplete="username" required readonly
              value="<?=htmlspecialchars($_SERVER['PHP_AUTH_USER'])?>"/>
          </div>
        </div>

        <div class="form-group row">
          <label for="curpass" class="col-4 col-md-3 col-lg-2 col-form-label text-right">Current Password:</label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="curpass" class="form-control"
              name="curpass" type="password" autocomplete="current-password" required />
          </div>
        </div>

        <div class="form-group row">
          <label for="newpass" class="col-4 col-md-3 col-lg-2 col-form-label text-right">New Password:</label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="newpass" class="form-control"
              name="newpass" type="password" autocomplete="new-password" required />
          </div>
        </div>

        <div class="form-group row">
          <label for="conpass" class="col-4 col-md-3 col-lg-2 col-form-label text-right">Confirm Password:</label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="conpass" class="form-control"
              name="conpass" type="password" autocomplete="new-password" required />
          </div>
        </div>
        
        <div>
          <button type="submit" class="btn btn-primary">Change Password</button>
        </div>
      </div>
      <?php
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
          $command = chpasswd($_POST["user"], $_POST["curpass"], $_POST["newpass"], $_POST["conpass"]);
          exec($command, $output, $return);

          if ($return == 0) {
            ?><div class="card-footer alert-success" role="alert">
              <p>Password successfully updated!</p>
            </div><?php
          } else {
            ?><div class="card-footer alert-danger" role="alert">
              <p>Password change not accepted!</p>
              <ul>
                <li>Ensure the current password you entered is correct.</li>
                <li>Ensure you typed the new password correctly.</li>
                <li>Ensure your new password meets the password length and complexity requirements for this system.</li>
              </ul>
            <?php

            $pass_output = array();
            foreach ($output as $line) {
              if(preg_match("/passwd: .*$/", $line, $matches)){
                array_push($pass_output, $matches[0]);
              }
            }

            ?><pre><code><?php
              echo '$ passwd '.htmlspecialchars($_POST["user"])."\n";
              foreach ($pass_output as $line) {
                echo htmlspecialchars($line)."\n";
              }
            ?></code></pre><?php

            ?></div><?php
          }
        }
      ?>
    </div>
  </form>
</div>

<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="static/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="static/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</body>
</html>