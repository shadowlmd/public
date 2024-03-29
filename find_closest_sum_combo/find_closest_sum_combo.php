<!DOCTYPE html>
<html lang="ru">

<head>
    <meta charset="utf-8">
</head>

<body>

    <?php
    if (isset($_POST["submit"])) {
        $numbers = preg_split('/\s+/', str_replace(",", ".", $_POST["numbers"]));
        exec("timeout -k 1 10 " . __DIR__ . "/find_closest_sum_combo.py " . escapeshellcmd($_POST["goal"]) . " " . escapeshellcmd(implode(" ", $numbers)) . " 2>&1", $out, $rc);
        if ($rc == 0 && count($out) > 0) {
            $out = implode("</p>\n<p>", $out);
            echo "<p>Комбинация чисел с максимально близкой к {$_POST["goal"]} суммой:</p>\n";
            echo "<p>{$out}</p>\n";
        } else {
            echo "<p>Что-то пошло не так. :(</p>\n";
            echo "<p>Код возврата: {$rc}</p>\n";
            echo "<p>Подробности:</p>\n";
            echo "<pre>\n";
            var_dump($out);
            echo "</pre>\n";
        }
    } else {
    ?>

        <form action="" method="post">
            Потолок суммы чисел:
            <input type="number" name="goal" placeholder="Например: 300"><br>
            Числа:<br>
            <textarea name="numbers" cols="10" rows="10" placeholder="<?= "Например:\n\n12.3\n46\n73.00\n21,34" ?>"></textarea><br>
            <input type="submit" value="Поехали!" name="submit">
        </form>

    <?php
    }
    ?>

</body>

</html>
