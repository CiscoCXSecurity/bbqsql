<html>
<head>
<title>My Vulnerable PHP/MySQL Application</title>
</head>
<body>
<?php
//Vulnerable PHP Web Application with MySQL Backend

$host = "localhost";
$username = "root";
$password = "qa55m0r?"

$link = mysql_connect($host, $username, $password);
if (!$link) {
    die('<b>Could not connect: ' . mysql_error() . "</b><br>");
}
echo '<b>Connected successfully</b><br>';
if (!mysql_select_db("test")){
    die('<b>dont have the db setup...: ' . mysql_error() . "</b><br>");
}

$tb = '';
if(isset($_POST['time_blind'])){
	$tb = $_POST['time_blind'];
	$query = "SELECT * FROM example id=$tb LIMIT 10";
}
echo "Query: $query <br>";
$result = mysql_query($query);

if (!$result){
    die('<b>dont have the table setup: ' . mysql_error() . "</b><br>");
}

while ($row = mysql_fetch_array($result)){
	for(i=0;i<count($row);i++){
		echo "$row[i]&nbsp;&nbsp;";
	}
	echo "<br>";
}
mysql_close($link);
?>
<br>
<form method='POST' action='vulnerable.php'>
	Time Blind:<input type='text' name='time_blind' value='<? echo $tb; ?>'>

</form>
</body>
</html>