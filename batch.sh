max=10
for (( i=1; i <= $max; ++i ))
do
    echo python3 game.py -a1 search -a2 search "$i"
    python3 game.py -a1 search -a2 search > gamelog"$i".txt
done
