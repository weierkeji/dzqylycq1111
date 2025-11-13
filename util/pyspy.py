"""
py-spy 堆栈捕获工具函数
提供堆栈捕获和保存功能
"""
import os
import time
import socket
import subprocess
from pathlib import Path


def get_ip_address():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_pyspy(native=False, rank=None):
    pid = os.getpid()
    ip = get_ip_address()
    
    cmd = ["py-spy", "dump", "--pid", str(pid)]
    if native:
        cmd.append("--native")
    
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        timeout=10
    )
        
        # 检查是否成功
    if result.returncode != 0 or (not result.stdout.strip()):
        return {
            "success": False,
            "ip_pid": f"{ip}:{pid}",
            "rank": rank,
            "error": result.stderr or "No output from py-spy"
        }
        
        # 成功返回
    return {
        "success": True,
        "ip_pid": f"{ip}:{pid}",
        "dump": result.stdout,
        "rank": rank,
        "timestamp": time.time()
    }


def demo_error_capture():            
    stack_info = run_pyspy()
        
    if stack_info["success"]:
        # 创建输出目录
        output_dir = Path("./stack_outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存到指定目录
        filename = output_dir / f"error_stack_{os.getpid()}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"IP:PID = {stack_info['ip_pid']}\n")
            f.write(f"Timestamp = {stack_info['timestamp']}\n")
            f.write("="*70 + "\n")
            f.write(stack_info["dump"])
            # print(f"✅ 堆栈已保存到: {filename}")
