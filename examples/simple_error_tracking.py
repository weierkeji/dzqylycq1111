import os
import sys
import time
import json

os.environ["DLROVER_EVENT_ENABLE"] = "true"              # 启用事件系统
os.environ["DLROVER_EVENT_HOOK_ERROR"] = "true"         # 启用异常钩子（关键！）
os.environ["DLROVER_EVENT_FILE_DIR"] = "./simple_my_logs_minimal"  # 日志输出目录
os.environ["DLROVER_EVENT_EVENT_EXPORTER"] = "TEXT_FILE"  # 输出到文件
os.environ["DLROVER_EVENT_TEXT_FORMATTER"] = "LOG"     # 日志格式


# import dlrover.python.training_event
import util.stack_error_handler


def main():
    raise ValueError(
            f"ValueError: Invalid parameter detected!\n"
            f"  This is a test exception from rank 0"
        )

if __name__ == "__main__":
    main()