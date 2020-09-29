#!/bin/bash

php -r 'echo filter_var(iconv_mime_decode("'"$*"'", ICONV_MIME_DECODE_CONTINUE_ON_ERROR), FILTER_UNSAFE_RAW, FILTER_FLAG_STRIP_LOW)."\n";'
