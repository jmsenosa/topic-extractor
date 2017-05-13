<?php 
    // print_r('arrrggggggg!!! deads na ako!!! oh ito oh, arggg.... (blood)');
    // die("\n");

    $fileitems = fopen("preDefinedFeatures/wordtags.txt",'r');
    $fileArray = array();
    if ($fileitems) {
        while (($line = fgets($fileitems)) !== false) {
            array_push($fileArray, strip_tags($line));
        }

        fclose($fileitems);
    } else {
        // error opening the file.
    } 

    $wordsTojson = array();

    foreach ($fileArray as $key => $value) { 
        $wordArray = explode(":", $value);
        $wordArray[0] = str_replace("\'", "", $wordArray[0]);
        
        $firstL = substr($wordArray[1],0,1);
        if (isset($firstL)) {
            if ($firstL == "'" || $firstL == '"') {
                $wordArray[1] = str_replace('" "', ", ", $wordArray[1]);
                $wordArray[1] = str_replace('"', "", $wordArray[1]);
                $wordArray[1] = str_replace("'", "", $wordArray[1]);
                $wordArray[1] = str_replace(" or ", ", ", $wordArray[1]);
                echo $wordArray[1];
            }
        } 
        $wordArray[1] = trim(preg_replace('/\s\s+/', ' ', $wordArray[1]));
        $wordsTojson[$wordArray[0]] = $wordArray[1];
    }


    fwrite(fopen("preDefinedFeatures/wordtags.json",'a'), json_encode($wordsTojson,true)); 
?>