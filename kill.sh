# kill_all: 根据命令杀死对应的进程
kill_all()
{
    ID=`ps | grep "$1" | grep -v "$0" | grep -v "grep" | awk '{print $1}'`  # -v表示反过滤，awk表示按空格或tab键拆分，{print $2}表示打印第二个（这里对应进程号）
    for id in $ID 
    do  
    echo "killed $id"  
    kill -9 $id  
    # echo "killed $id"  
    done
}
kill_all "python"