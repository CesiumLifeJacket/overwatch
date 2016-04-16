<?php
	ob_start();
	error_reporting("E_STRICT");
	$json = file_get_contents("../JSON/ncreview.json");
	$code = file_get_contents("../CODE/ncreview.py");
	$gar = ob_get_clean();
	echo '<!DOCTYPE html>
<html>
	<head>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
		<script src="../JS/parsejson.js"></script>
		<link rel="stylesheet" type="text/css" href="../CSS/styles.css">
	</head>
	<body>
		<pre id="output">';
		echo $json;
		echo '</pre><pre id = "new"></pre><pre id="code">'.$code.'<pre>
	</body>
</html>';