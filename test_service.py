"""
测试语音识别服务的客户端脚本
"""
import time
import requests
from pathlib import Path
from typing import Optional


class AudioTranscriptionClient:
    """语音识别服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:6006"):
        self.base_url = base_url
    
    def upload_audio(self, audio_file: str) -> str:
        """
        上传音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            task_id: 任务ID
        """
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise FileNotFoundError(f"文件不存在: {audio_file}")
        
        print(f"上传文件: {audio_path.name}")
        
        with open(audio_path, "rb") as f:
            files = {"file": (audio_path.name, f, "audio/wav")}
            response = requests.post(
                f"{self.base_url}/api/tasks/upload",
                files=files
            )
        
        response.raise_for_status()
        result = response.json()
        
        task_id = result["task_id"]
        print(f"✓ 任务已创建: {task_id}")
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        
        return task_id
    
    def get_task_result(self, task_id: str) -> dict:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果字典
        """
        response = requests.get(f"{self.base_url}/api/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        task_id: str,
        check_interval: int = 5,
        max_wait_time: Optional[int] = None
    ) -> dict:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒），None 表示无限等待
            
        Returns:
            任务结果
        """
        print(f"\n等待任务完成: {task_id}")
        start_time = time.time()
        
        while True:
            result = self.get_task_result(task_id)
            status = result["status"]
            
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] 状态: {status}", end="")
            
            if status == "completed":
                print(" ✓")
                return result
            elif status == "failed":
                print(" ✗")
                error_msg = result.get("error_message", "未知错误")
                raise RuntimeError(f"任务失败: {error_msg}")
            else:
                print()
            
            # 检查超时
            if max_wait_time and elapsed >= max_wait_time:
                raise TimeoutError(f"等待超时 ({max_wait_time}秒)")
            
            time.sleep(check_interval)
    
    def list_tasks(self, status: Optional[str] = None, limit: int = 10) -> dict:
        """
        列出任务
        
        Args:
            status: 过滤状态
            limit: 返回数量
            
        Returns:
            任务列表
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(f"{self.base_url}/api/tasks", params=params)
        response.raise_for_status()
        return response.json()
    
    def print_result(self, result: dict):
        """打印转录结果"""
        print("\n" + "=" * 60)
        print(f"任务ID: {result['task_id']}")
        print(f"文件名: {result['filename']}")
        print(f"状态: {result['status']}")
        print(f"创建时间: {result['created_at']}")
        print(f"更新时间: {result['updated_at']}")
        
        if result.get("error_message"):
            print(f"错误: {result['error_message']}")
        
        if result.get("speakers"):
            print("\n转录结果:")
            print("-" * 60)
            for speaker in result["speakers"]:
                print(f"\n[{speaker['speaker_id']}] "
                      f"{speaker['start']:.2f}s - {speaker['end']:.2f}s")
                print(f"  {speaker['text']}")
        
        print("=" * 60)


def main():
    """测试示例"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python {sys.argv[0]} <audio_file>")
        print(f"  python {sys.argv[0]} list")
        print(f"  python {sys.argv[0]} get <task_id>")
        sys.exit(1)
    
    client = AudioTranscriptionClient()
    
    command = sys.argv[1]
    
    if command == "list":
        # 列出任务
        result = client.list_tasks(limit=20)
        print(f"\n共 {result['count']} 个任务:")
        for task in result["tasks"]:
            print(f"  {task['task_id'][:8]}... | {task['status']:10} | {task['filename']}")
    
    elif command == "get":
        # 获取特定任务
        if len(sys.argv) < 3:
            print("错误: 需要提供 task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = client.get_task_result(task_id)
        client.print_result(result)
    
    else:
        # 上传音频文件
        audio_file = command
        
        try:
            # 步骤1: 上传音频
            task_id = client.upload_audio(audio_file)
            
            # 步骤2: 等待完成
            result = client.wait_for_completion(task_id, check_interval=3)
            
            # 步骤3: 显示结果
            client.print_result(result)
            
        except Exception as e:
            print(f"\n错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
