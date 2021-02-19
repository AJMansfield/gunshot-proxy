<?php
$settings_filename = "/opt/gunshot/settings.yaml"; // setting schema definition
$config_filename = "/opt/gunshot/config.yaml"; // output settings file
require 'includes/sudo.php';
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

  <!-- CodeMirror -->
  <script src="static/codemirror.min.js"></script>
  <link rel="stylesheet" href="static/codemirror.min.css">
  <script src="static/yaml.min.js"></script>

  <title>Gunshot Detector Proxy Configuration</title>
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
function refsToValues($arr) {
  return yaml_parse(yaml_emit($arr));
}

$settings_yaml = shell_exec_as_user('cat '.escapeshellarg($settings_filename));
$settings = yaml_parse($settings_yaml, 0);
$settings = refsToValues($settings);

$config_yaml = shell_exec_as_user('cat '.escapeshellarg($config_filename));
$ndocs = 0;
$config = yaml_parse($config_yaml, 0, $ndocs);
if ($ndocs == 0) {
  $config = null;
}
$config = refsToValues($config);

$token_name = "options-list-token";

function assignTokens(&$setting, $ctx) {
  global $token_name;
  foreach ($setting as $key => &$inner_setting) {
    if (is_iterable($inner_setting)) {
      $inner_ctx = hash_copy($ctx);
      hash_update($inner_ctx, $key);
      assignTokens($inner_setting, $inner_ctx);
    }
  }
  $setting[$token_name] = hash_final($ctx);
}
assignTokens($settings, hash_init("sha1"));

function get(&$var, $default=null) {
  return isset($var) ? $var : $default;
}

function displaySettingForm ($setting, $config, $name, $level=1) {
  global $token_name;
  $token = $setting[$token_name];
  $value = is_null($config) ? get($setting["default"], $config) : $config;

  $type = $setting["type"];
  if ($_GET["yaml"] ?? $_GET["debug"] ?? "0") { // pass yaml or debug params to fall back to raw yaml
    $type = "yaml";
  }

  switch ($type) {
    case "html":
      echo $setting["content"];
      break;

    case "section":
      switch ($level) {
        case 0:
        case 1:
          $d1cls = "";
          $hcls = "d-none";
          $d2cls = "";
          $pcls = "";
          break;
        case 2:
          $d1cls = "card";
          $hcls = "card-header h4";
          $d2cls = "card-body";
          $pcls = "card-text";
          break;
        default:
          $d1cls = "";
          $hcls = "h5";
          $d2cls = "";
          $pcls = "";
          break;
      }
      ?>
        <div id="<?=$token?>" class="<?=$d1cls?>">
          <div class="<?=$hcls?>"><a name="<?=$name?>"><?=get($setting["title"], $name)?></a></div>
          <div class="<?=$d2cls?>">
            <p class="<?=$pcls?>"><?=get($setting["descr"])?></p>
            <?php
              foreach ($setting["settings"] as $key => $inner_setting) {
                if (strcmp($key, $token_name) == 0)  continue;
                displaySettingForm($inner_setting, get($config[$key]), $key, $level+1);
              }
            ?>
          </div>
        </div>
      <?php
      break;

    case "select":
      ?>
        <div class="form-group row">
          <label for="<?=$token?>" class="col-4 col-md-3 col-lg-2 col-form-label text-right"><?=get($setting["label"], $name)?></label>
          <div class="col-8 col-md-9 col-lg-10">
            <select id="<?=$token?>" name="<?=$token?>" class="form-control">
              <?php
                foreach ($setting["options"] as $ovalue => $option) {
                  if (strcmp($ovalue, $token_name) == 0) continue;
                  $selected = (strcmp($ovalue, $value) == 0) ? "selected" : "";
                  ?>
                    <option value="<?=$ovalue?>" <?=$selected?>><?=$option?></option>
                  <?php
                }
              ?>
            </select>
            <?php if (isset($setting["descr"])) {?> <p class="text-muted"><?=$setting["descr"]?></p> <?php } ?>
          </div>
        </div>
      <?php
      break;


    case "checkbox":
      $checked = $value ? "checked" : "";
      ?>
        <div class="form-group row">
          <label for="<?=$token?>" class="col-4 col-md-3 col-lg-2 col-form-label text-right"><?=get($setting["label"], $name)?></label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="<?=$token?>" name="<?=$token?>" type="checkbox" <?=$checked?> class="form-control">
            <?php if (isset($setting["descr"])) {?> <p class="text-muted"><?=$setting["descr"]?></p> <?php } ?>
          </div>
        </div>
      <?php
      break;

    case "text":
    case "number":
      ?>
        <div class="form-group row">
          <label for="<?=$token?>" class="col-4 col-md-3 col-lg-2 col-form-label text-right"><?=get($setting["label"], $name)?></label>
          <div class="col-8 col-md-9 col-lg-10">
            <input id="<?=$token?>" name="<?=$token?>" class="form-control" type="<?=$setting["type"]?>" value="<?=$value?>"
              placeholder="<?=get($setting["hint"], $name)?>">
            <?php if (isset($setting["descr"])) {?> <p class="text-muted"><?=$setting["descr"]?></p> <?php } ?>
          </div>
        </div>
      <?php
      break;

    case "blocktext":
      ?>
        <div class="form-group row">
          <label for="<?=$token?>" class="col-4 col-md-3 col-lg-2 col-form-label text-right"><?=get($setting["label"], $name)?></label>
          <div class="col-8 col-md-9 col-lg-10">
            <textarea id="<?=$token?>" name="<?=$token?>" class="form-control"><?=$value?></textarea>
            <script>
            $(document).ready(function() {
              var editor = CodeMirror.fromTextArea(document.getElementById("<?=$token?>"), {
                mode: "text/raw",
                lineNumbers: true,
              });
            });
            </script>
            <?php if (isset($setting["descr"])) {?> <p class="text-muted"><?=$setting["descr"]?></p> <?php } ?>
          </div>
        </div>
      <?php
      break;

    case "yaml":
    default:
      ?>
        <div class="form-group row">
          <label for="<?=$token?>" class="col-4 col-md-3 col-lg-2 col-form-label text-right"><?=get($setting["label"], $name)?></label>
          <div class="col-8 col-md-9 col-lg-10">
            <textarea id="<?=$token?>" name="<?=$token?>" class="form-control"><?=yaml_emit($value)?></textarea>
            <script>
            $(document).ready(function() {
              var editor = CodeMirror.fromTextArea(document.getElementById("<?=$token?>"), {
                mode: "text/x-yaml",
                lineNumbers: true,
              });
            });
            </script>
            <?php if (isset($setting["descr"])) {?> <p class="text-muted"><?=$setting["descr"]?></p> <?php } ?>
          </div>
        </div>
      <?php
      break;
  }
}

function applySettings ($setting, &$config, &$restartcmds=array()) {
  // return whether a setting has changed
  global $token_name;
  $token = $setting[$token_name];
  $newcfg = $config;
  $changed = false;
  
  $type = $setting["type"];
  if ($_GET["yaml"] ?? $_GET["debug"] ?? "0") { // pass yaml or debug params to fall back to raw yaml
    $type = "yaml";
  }

  switch ($type) {
    case "html":
      break;
      
    case "section":
      if (is_null($newcfg)) {
        $newcfg = array();
      }
      foreach ($setting["settings"] as $key => $inner_setting) {
        if (strcmp($key, $token_name) == 0)  continue;
        if (!array_key_exists($key, $newcfg)) {
          $newcfg[$key] = null;
        }
        $inner_changed = applySettings($inner_setting, $newcfg[$key], $restartcmds);
        $changed = $changed || $inner_changed;
      }
      break;

    case "select":
      if (array_key_exists($token, $_POST) && array_key_exists($_POST[$token], $setting["options"])) {
        $newcfg = $_POST[$token];
      } else {
        $newcfg = get($setting["default"]);
      }
      break;

    case "text":
    case "blocktext":
      if (array_key_exists($token, $_POST)) {
        $newcfg = $_POST[$token];
      } else {
        $newcfg = get($setting["default"]);
      }
      break;

    case "checkbox":
      if (array_key_exists($token, $_POST)) {
        $newcfg = true;
      } else {
        $newcfg = false;
      }
      break;

    case "number":
      if (array_key_exists($token, $_POST) && is_numeric($_POST[$token])) {
        $newcfg = +$_POST[$token];
      } else {
        $newcfg = get($setting["default"]);
      }
      break;

    case "yaml":
    default:
      $newcfg = yaml_parse($_POST[$token]);
      $changed = $changed || gatherRestartCmdsRecursive($setting, $newcfg, $config, $restartcmds);
      break;
  }

  // TODO: need to recursively accumulate on_edit commands when editing raw YAML

  $changed = $changed || (strcmp(yaml_emit($newcfg), yaml_emit($config)) != 0);

  if ($changed) {
    if (array_key_exists("on_edit", $setting)) {
      if (is_iterable($setting["on_edit"])) {
        foreach ($setting["on_edit"] as $key => $cmd) {
          if (strcmp($key, $token_name) == 0) continue;
          array_push($restartcmds, $cmd);
        }
      } else {
        array_push($restartcmds, $setting["on_edit"]);
      }
    }
  }

  $config = $newcfg;
  return $changed;
}

function gatherRestartCmdsRecursive($setting, $newcfg, $oldcfg, &$restartcmds=array()) {
  global $token_name;

  $changed = strcmp(yaml_emit($newcfg), yaml_emit($oldcfg)) != 0;

  if ($changed){
    if (array_key_exists("on_edit", $setting)) {
      if (is_iterable($setting["on_edit"])) {
        foreach ($setting["on_edit"] as $key => $cmd) {
          if (strcmp($key, $token_name) == 0) continue;
          array_push($restartcmds, $cmd);
        }
      } else {
        array_push($restartcmds, $setting["on_edit"]);
      }
    }

    if ($setting["type"] == "section") {
      foreach ($setting["settings"] as $key => $inner_setting) {
        if (strcmp($key, $token_name) == 0) continue;
        gatherRestartCmdsRecursive($inner_setting, get($newcfg[$key]), get($oldcfg[$key]), $restartcmds);
      }
    }
  }
  return $changed;
}
?>

<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  $restartcmds = array();
  $changed = applySettings($settings, $config, $restartcmds);
  $restartcmds = array_unique($restartcmds);
  if ($changed) {

    
    $mktemp = trim(`mktemp`); // already know mktemp is clean , don't need to escape
    yaml_emit_file($mktemp, $config);
    `chmod 444 $mktemp`;
    shell_exec_as_user('cp -f '.escapeshellarg($config_filename).' '.escapeshellarg($config_filename.'.old'));
    shell_exec_as_user("cp -f $mktemp ".escapeshellarg($config_filename));
    `rm $mktemp`;

    // echo '<pre><code>'.htmlspecialchars(implode("\n",$restartcmds)).'</code></pre>';
    foreach ($restartcmds as $cmd) {
      exec_as_user($cmd);
    }
  }
}
?>

<div class="container">
  <div class="pb-2 mt-4 mb-2 border-bottom">
    <h1>Gunshot Proxy Config</h1>
  </div>
  <div class="card">
    <div class="card-body">
      <a href="<?=get($_GET["yaml"],0) ? "?yaml=0" : "?yaml=1"?>" class="btn <?=get($_GET["yaml"],0) ? "btn-info" : "btn-outline-info"?>">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-code-square" viewBox="0 0 16 16" style="vertical-align:-2;">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M6.854 4.646a.5.5 0 0 1 0 .708L4.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0zm2.292 0a.5.5 0 0 0 0 .708L11.793 8l-2.647 2.646a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708 0z"/>
        </svg>
        Edit Raw Config
      </a>
      <a href="password.php" class="btn btn-primary">
        User Management
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right" viewBox="0 0 16 16" style="vertical-align:-2;">
          <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
        </svg>
      </a>
    </div>
  </div>
  <form class="form" method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">
    <?= displaySettingForm($settings, $config, "config") ?>
    <div class="card position-sticky" style="bottom: 0; z-index: 4;">
      <div class="card-body">
        <button type="submit" class="btn btn-primary">Apply Settings and Restart Affected Services</button>
      </div>
    </div>
  </form>
</div>

<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="static/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="static/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="static/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</body>
</html>