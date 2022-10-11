#!/bin/bash

# 创建一个管道
mkfifo mylist
# 给管道绑定文件描述符4
exec 4<>mylist
# 再创建一个管道（锁文件），用于解决线程安全问题
mkfifo mylock
# 绑定文件描述符5
exec 5<>mylock

# 事先向锁文件中插入1条数据（解锁）
echo >mylock

# 开启45个子进程
for ((i = 0; i < 45; i++)); do
  # 这里的 & 会开启一个子进程执行
  {
    # 先读取锁文件（加锁），由于锁文件中只有1条数据，读取完之后锁文件空了其他子进程再读取时只能等待
    while read -t 1 <mylock && read -t 1 url <mylist; do
      # 读取到业务数据后立即向写入1条数据到锁文件（解锁），让其他子进程继续读取数据
      echo >mylock

      echo "doing: ${url}"
      ${url}
      echo "done: ${url}"
    done
  } &
done
# 将img.txt中的链接全部插入到管道中
cat todo_cmd.txt | while read url; do
  echo ${url} >mylist
done

# 使用 wait 命令阻塞当前进程，直到所有子进程全部执行完
wait
echo "you have doing all cmds"

# 全部结束后解绑文件描述符并删除管道
exec 4<&-
exec 4>&-
rm -f mylist
exec 5<&-
exec 5>&-
rm -f mylock
