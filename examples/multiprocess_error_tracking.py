import os
import sys
import time
import multiprocessing
from multiprocessing import Process

# 在主进程中设置全局配置（子进程会继承这些环境变量）
os.environ["DLROVER_EVENT_ENABLE"] = "true"              # 启用事件系统
os.environ["DLROVER_EVENT_HOOK_ERROR"] = "true"         # 启用异常钩子（关键！）
os.environ["DLROVER_EVENT_FILE_DIR"] = "./multiprocess_my_logs"  # 日志输出目录
os.environ["DLROVER_EVENT_EVENT_EXPORTER"] = "TEXT_FILE"  # 输出到文件
os.environ["DLROVER_EVENT_TEXT_FORMATTER"] = "LOG"     # 日志格式


def worker_function(rank):    
    """
    子进程入口函数
    
    关键问题：multiprocessing.Process 在 Windows spawn 模式下会捕获
    目标函数中的所有异常，
    异常被 multiprocessing 捕获后，用于设置进程退出码，但不会传播到 sys.excepthook
    导致 sys.excepthook 不会被自动调用，
    从而ErrorHandler._handle_exception() 永远不会被调用无法记录异常堆栈。
    
    sys.excepthook 只在以下情况被调用：
        1. 异常没有被任何 try-except 捕获
        2. 异常一路传播到 Python 解释器的最顶层
    
    解决方案：手动捕获异常并调用 sys.excepthook。
    """
    # 在子进程中设置 RANK 环境变量（用于区分日志文件）
    os.environ["RANK"] = str(rank)    
    import util.stack_error_handler
    
    print(f"[Rank {rank}] Worker process started, PID: {os.getpid()}")
    
    # 必须用 try-except 手动捕获异常，然后调用 sys.excepthook
    try:
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
                f"  Type mismatch in worker 3"
            )
    except Exception:
        # ★ 关键：手动调用 sys.excepthook 来触发错误记录
        import traceback
        exc_type, exc_value, exc_tb = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_tb)        
        # 重新抛出异常（让 multiprocessing 知道进程失败了）
        raise

def main():      
    processes = []    
    # 启动 4 个子进程
    for rank in range(4):
        p = Process(target=worker_function, args=(rank,))
        p.start()
        processes.append(p)        
        time.sleep(0.1)  # 稍微错开启动时间


if __name__ == "__main__":        
    multiprocessing.set_start_method('spawn', force=True)    
    main()


