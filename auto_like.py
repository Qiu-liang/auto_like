import requests
import time
import random
import threading
import gc
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List
import sys

# ========== 配置区 ==========
BASE_URL = "https://apiv4.720yun.com"
PRODUCT_ID = "edvkb9d7r8y"
APP_KEY = "eByjUyLDG2KtkdhuTsw2pY46Q3ceBPdT"
APP_AUTHORIZATION = ""  # 如果需要，请填写真实的授权令牌

# 如果接口依赖 Cookie 验证，也可以在这里填入
COOKIES = {
    "Hm_lvt_08a05dadf3e5b6d1c99fc4d862897e31": "1752546614",
    "Hm_lpvt_08a05dadf3e5b6d1c99fc4d862897e31": "1752546614",
    "HMACCOUNT": "3A2E0824E35050E7",
    "aliyungf_tc": "bdc22848318404e861e3fc660643a2767a7bfcc0504b6b7f248a22a8565f8842",
    "acw_tc": "ac11000117525466158412565e1545889346149c3d2dc1a37a37b218a434cb"
}

HEADERS = {
    "Host": "apiv4.720yun.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "App-Key": APP_KEY,
    "App-Authorization": APP_AUTHORIZATION,
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Origin": "https://www.720yun.com",
    "Referer": f"https://www.720yun.com/t/{PRODUCT_ID}?scene_id=95797282",
    "Accept-Encoding": "identity",  # 禁用压缩提升速度
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# 高速优化配置
DEFAULT_THREAD_COUNT = 50  # 默认高并发线程数
MIN_DELAY = 0.1  # 几乎无延迟
MAX_DELAY = 0.5  # 极短延迟
CONNECTION_POOL_SIZE = 100  # 大连接池
# =============================


@dataclass
class ThreadSafeStats:
    """线程安全的统计类"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def increment_total(self):
        with self._lock:
            self.total_requests += 1

    def increment_success(self):
        with self._lock:
            self.successful_requests += 1

    def increment_failure(self):
        with self._lock:
            self.failed_requests += 1

    def get_stats(self) -> Dict:
        with self._lock:
            return {
                'total': self.total_requests,
                'success': self.successful_requests,
                'failed': self.failed_requests,
                'success_rate': (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            }

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.end_time = time.time()

    def get_duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > self.start_time else 0.0

    def get_qps(self) -> float:
        duration = self.get_duration()
        return self.total_requests / duration if duration > 0 else 0.0


def create_session():
    """初始化高速会话"""
    session = requests.Session()
    
    # 优化连接适配器
    from requests.adapters import HTTPAdapter
    adapter = HTTPAdapter(
        pool_connections=CONNECTION_POOL_SIZE,
        pool_maxsize=CONNECTION_POOL_SIZE,
        max_retries=0  # 禁用重试
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    return session


def close_session(session):
    """安全关闭会话"""
    try:
        session.close()
    except:
        pass


def send_like(session, stats: ThreadSafeStats, request_id: int):
    """高速发送点赞请求"""
    url = f"{BASE_URL}/product/{PRODUCT_ID}/like"
    
    # 极短随机延迟
    random_delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(random_delay)
    
    try:
        resp = session.post(url, timeout=5)  # 缩短超时时间
        stats.increment_total()
        
        if resp.ok:
            stats.increment_success()
            if request_id % 1000 == 0:  # 每1000个显示一次
                print(f"[✔] #{request_id:06d} 成功", end='\r')
            return True
        else:
            stats.increment_failure()
            return False
    except Exception:
        stats.increment_total()
        stats.increment_failure()
        return False


def main():
    print("🚀 高速点赞程序启动 (极速模式)")
    print("="*50)
    
    try:
        total_times = int(input("请输入要发送的点赞次数: "))
        thread_count = int(input(f"请输入线程数 (默认 {DEFAULT_THREAD_COUNT}): ") or DEFAULT_THREAD_COUNT)
        
        if total_times <= 0 or thread_count <= 0:
            print("❌ 请输入正数！")
            return
            
    except ValueError:
        print("❌ 输入有误，请输入数字！")
        return

    # 创建统计对象
    stats = ThreadSafeStats()
    stats.start_timer()
    
    print(f"\n📋 任务配置:")
    print(f"   - 总请求数: {total_times}")
    print(f"   - 线程数: {thread_count}")
    print(f"   - 延迟: {MIN_DELAY}-{MAX_DELAY} 秒")
    print(f"   - 模式: 极速模式")
    print("\n⚡ 开始高速执行...\n")
    
    # 创建会话
    session = create_session()
    
    try:
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 一次性提交所有任务
            futures = []
            for i in range(1, total_times + 1):
                future = executor.submit(send_like, session, stats, i)
                futures.append(future)
            
            # 等待所有任务完成
            completed = 0
            for future in as_completed(futures):
                completed += 1
                future.result()
                
                # 每完成10%显示进度
                if completed % max(1, total_times // 10) == 0:
                    progress = (completed / total_times) * 100
                    print(f"📈 进度: {completed}/{total_times} ({progress:.1f}%)")
    
    finally:
        close_session(session)
    
    stats.stop_timer()
    
    # 最终统计
    print("\n" + "🎉 任务完成！最终统计")
    print("="*60)
    final_stats = stats.get_stats()
    duration = stats.get_duration()
    qps = stats.get_qps()
    
    print(f"✅ 总请求数: {final_stats['total']}")
    print(f"✅ 成功: {final_stats['success']} ({final_stats['success_rate']:.1f}%)")
    print(f"❌ 失败: {final_stats['failed']}")
    print(f"⏱️  总耗时: {duration:.2f} 秒")
    print(f"⚡ 平均QPS: {qps:.2f} 请求/秒")
    
    if final_stats['success'] > 0:
        avg_time_per_success = duration / final_stats['success']
        print(f"⏱️  平均每次成功请求耗时: {avg_time_per_success:.4f} 秒")
    
    print("="*60)


if __name__ == "__main__":
    main()
