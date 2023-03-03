<!DOCTYPE html>
<html lang="ru">

<head>
    <meta charset="utf-8">
</head>

<body>
    <?php
    if (isset($_POST["submit"])) {
        $numbers = preg_split('/\s+/', $_POST["numbers"]);
        exec("timeout -k 1 60 " . __DIR__ . "/find_closest_sum_combo.py " . escapeshellcmd($_POST["goal"]) . " " . escapeshellcmd(implode(" ", $numbers)), $out, $rc);
        if ($rc == 0) {
            echo "<p>{$out}</p>" . PHP_EOL;
        } else {
    ?>
            <p>
                Что-то пошло не так. :(
            </p>
            <p>
                Подробности:
            </p>
        <?php
            echo "<pre>\n";
            var_dump($out);
            echo "</pre>\n";
        }
    } else {
        ?>
        <form action="" method="post" enctype="multipart/form-data">
            Потолок суммы чисел:
            <input type="number" name="goal"><br>
            Числа (по числу на строчку):<br>
            <textarea name="numbers" cols="10" rows="10"></textarea><br>
            <input type="submit" value="Поехали!" name="submit">
        </form>

    <?php
    }
    ?>
</body>

</html>
