<?php

require "vars.php";

$arg_lookup = [
  "--only-group" => [
    "hasValue" => true,
    "valueType" => "string"
  ]
];

if(!defined('STDIN'))  define('STDIN',  fopen('php://stdin',  'rb'));
if(!defined('STDOUT')) define('STDOUT', fopen('php://stdout', 'wb'));
if(!defined('STDERR')) define('STDERR', fopen('php://stderr', 'wb'));

define("SOURCE_FILE", "blocks.txt");
define("DRIVER_DIR", "drivers/"); // IMPORTANT: Must end in a trailing slash!

function strsw($h, $n) {
  return substr($h, 0, strlen($n)) === $n;
}

$drivers = array_map(function($i) {
  return basename($i);
}, glob(DRIVER_DIR . "*", GLOB_ONLYDIR));

$args = [];

for ($i = 1; $i < $argc; ++$i) {
  $arg = $argv[$i];
  if (array_key_exists($arg, $arg_lookup)) {
    $def = $arg_lookup[$arg];
    if ($def["hasValue"]) {
      if ($i + 1 === $argc) {
        fwrite(STDERR, "Warning: No value specified for '$arg', ignoring...". PHP_EOL);
        continue;
      } else {
        $val = $argv[$i + 1];
        ++$i;
        $args[$arg] = $val; // TODO Parse type
      }
    } else {
      $args[$arg] = true;
    }
  } else {
    fwrite(STDERR, "Warning: Unknown command line option '$arg', ignoring...". PHP_EOL);
  }
}

$onlyGroup = false;

if (isset($args["--only-group"])) {
  fwrite(STDERR, "Only running group " . $args["--only-group"] . PHP_EOL);
  $onlyGroup = $args["--only-group"];
}

foreach ($drivers as $driver) {
  fwrite(STDERR, "[>> Driver: ${driver} >>]" . PHP_EOL);
  $cmd = BLENDER_PATH . " --python-use-system-env --factory-startup " . DRIVER_DIR . "${driver}/${driver}.blend -b -P " . DRIVER_DIR . "${driver}/${driver}.py";
  if ($onlyGroup !== false)
    $cmd .= " -- --only-group " . escapeshellarg($onlyGroup);
  passthru($cmd);
  fwrite(STDERR, "[<< OK <<]" . PHP_EOL);
}

fwrite(STDERR, "All done!". PHP_EOL);
