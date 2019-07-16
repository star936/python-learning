# coding: utf-8

from .squeue import SQueue


"""
迷宫问题: 给定一个迷宫图，包括图中的一个入口点和一个出口点，要求在途中找到一条从入口到出口的路径。
[[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1],
[1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
[1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
[1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
[1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
[1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
[1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
其中起点位置为(1, 1);终点位置为(10, 12)
对于点(i, j)而言，其四个相邻位置为上(i-1, j), 下(i+1, j), 左(i, j-1), 右(i, j+1)
为计算(i, j)相邻位置,设置一个而元组的表，其元素是从位置(i, j)得到其四邻位置应该加的数对：
    dirs = [[0, 1], [1, 0], [0, -1], [-1, 0]]
"""


dirs = [[0, 1], [1, 0], [0, -1], [-1, 0]]


def mark(maze, pos):
    """给迷宫maze的位置pos标2表示'到过了'"""
    maze[pos[0]][pos[1]] = 2


def passable(maze, pos):
    """检查迷宫maze的位置pos是否可行"""
    return maze[pos[0]][pos[1]] == 0


def find_path(maze, pos, end):
    """递归查找迷宫路径"""
    mark(maze, pos)
    if pos == end:  # 到达终点
        print(pos, end=',')  # 输出该位置
        return True  # 成功结束
    for i in range(4):  # 按四个方向顺序查找
        # 考虑下一个可能方向
        nextp = pos[0] + dirs[i][0], pos[1] + dirs[i][1]
        if passable(maze, nextp):  # 不可行的相邻位置不管
            if find_path(maze, nextp, end):  # 从nextp可达终点
                print(pos, end=" ")  # 输出该位置
                return True  # 成功结束
    return False


"""
回溯法解决迷宫问题: 
    算法框架如下：
        将start标记为已达
        start入队
        while 队列里还有未充分探索的位置:
            取出一个位置pos
            检查pos的相邻位置
                遇到end成功结束
                尚未探查的都mark并入队
        队列空，搜索失败
另外入栈的是序对(pos, nxt)分支点位置pos用行/列坐标的序对表示; nxt是整数，表示回溯到该位置的下一个搜索方向，4个方向分别为[0, 1, 2, 3]
"""


def maze_solver(maze, start, end):
    """基于队列的迷宫求解算法"""
    if start == end:
        print("Path finds")
        return
    queue = SQueue()
    path = {start: None}  # 记录新位置的前驱位置,若存在路径，则可以根据前驱关系找到该路径
    mark(maze, start)
    queue.enqueue(start)  # start位置入列
    while not queue.is_empty():  # 还有未探索位置
        pos = queue.dequeue()  # 取出下一个位置
        for i in range(4):  # 检查当前位置的四个方向
            nextp = (pos[0] + dirs[i][0], pos[1] + dirs[i][1])
            if passable(maze, nextp):  # 找到新的探索方向
                path[nextp] = pos
                if nextp == end:  # 出口
                    print("Path find.")
                    return
                mark(maze, nextp)
                queue.enqueue(nextp)  # 新位置入列
    print("No path.")  # 没有路径，失败
