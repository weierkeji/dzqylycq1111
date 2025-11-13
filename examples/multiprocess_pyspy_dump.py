import time
from pathlib import Path
from multiprocessing import Process
from pyspy import demo_error_capture
        
    
def worker_function(rank):
    demo_error_capture()
  
    if rank == 0:
        raise ValueError(
            f"ValueError from rank {rank}!\n"
            f"  Invalid parameter detected in worker 0"
        )
    elif rank == 1:
        raise RuntimeError(
            f"RuntimeError from rank {rank}!\n"
            f"  Runtime error occurred in worker 1"
        )
    elif rank == 2:
        # 模拟除零错误
        result = 10 / 0
    else:  # rank == 3
        raise TypeError(
            f"TypeError from rank {rank}!\n"
            f"Type mismatch in worker 3"
        )


def main():        
    processes = []    
    # 启动 4 个子进程
    for rank in range(4):
        p = Process(target=worker_function, args=(rank,))
        p.start()
        processes.append(p)        
        time.sleep(0.1)  # 稍微错开启动时间

    
if __name__ == "__main__":
    main()