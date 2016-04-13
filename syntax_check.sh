#!sh
pep8 $1 > errors.txt
python syntax_check.py errors.txt $1 > errors.html
xdg-open errors.html