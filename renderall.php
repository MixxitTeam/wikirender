<?php

require "vars.php";

define("SOURCE_FILE", "blocks.txt");
define("DRIVER_DIR", "drivers/"); // IMPORTANT: Must end in a trailing slash!
define("MAX_BUFFER_LENGTH", 4096);

function strsw($h, $n) {
  return substr($h, 0, strlen($n)) === $n;
}

$drivers = array_map(function($i) {
  return basename($i);
}, glob(DRIVER_DIR . "*", GLOB_ONLYDIR));

foreach ($drivers as $driver) {
  echo "[>> Driver: ${driver} >>]\n";
  while (@ ob_end_flush());
  $cmd = BLENDER_PATH . " --factory-startup " . DRIVER_DIR . "${driver}/${driver}.blend -b -P " . DRIVER_DIR . "${driver}/${driver}.py";
  $proc = popen($cmd, "r");
  while (!feof($proc)) {
    echo fread($proc, MAX_BUFFER_LENGTH);
    @flush();
  }
}

echo "All done!\n";
