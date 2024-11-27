from django.db import connection
from time import time
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class QueryMonitor:
    @staticmethod
    def log_slow_queries(threshold_ms=100):
        """Enhanced query monitoring"""
        slow_queries = []
        total_time = 0
        
        for query in connection.queries:
            duration = float(query['time']) * 1000
            total_time += duration
            
            if duration > threshold_ms:
                slow_queries.append({
                    'sql': query['sql'],
                    'time': duration,
                    'path': query.get('path', 'N/A')
                })
        
        if slow_queries:
            logger.warning(f"Found {len(slow_queries)} slow queries. Total time: {total_time}ms")
            for query in slow_queries:
                logger.warning(f"Slow query in {query['path']}: {query['sql']} ({query['time']}ms)")

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time()
        response = self.get_response(request)
        duration = (time() - start_time) * 1000
        
        if duration > 500:  # Log requests taking more than 500ms
            logger.warning(f"Slow request: {request.path} ({duration}ms)")
        
        return response 

class AuthenticationMonitor:
    @staticmethod
    def log_auth_metrics():
        """Enhanced authentication monitoring"""
        metrics = {
            'active_sessions': cache.get('active_sessions', 0),
            'failed_attempts': cache.get('failed_attempts', 0),
            'avg_response_time': cache.get('auth_response_time', 0),
            'token_refresh_count': cache.get('token_refresh_count', 0),
            'concurrent_users': cache.get('concurrent_users', 0)
        }
        
        # Alert on high failure rates
        if metrics['failed_attempts'] > 100:  # Threshold
            logger.error(f"High authentication failure rate: {metrics['failed_attempts']} attempts")
            
        # Monitor response times
        if metrics['avg_response_time'] > 200:  # ms
            logger.warning(f"Slow authentication response time: {metrics['avg_response_time']}ms")
            
        logger.info(f"Auth Metrics: {metrics}")

class PerformanceMonitor:
    @staticmethod
    def monitor_endpoint_performance(view_func):
        def wrapper(*args, **kwargs):
            start_time = time()
            result = view_func(*args, **kwargs)
            duration = time() - start_time
            
            if duration > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow endpoint: {view_func.__name__} took {duration:.2f}s"
                )
            
            return result
        return wrapper

class MemoryMonitor:
    """Add memory monitoring to track memory leaks"""
    
    @staticmethod
    def monitor_memory_usage():
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Log if memory usage is too high
        if memory_info.rss > 500 * 1024 * 1024:  # 500MB
            logger.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
            
        return {
            'memory_used': memory_info.rss,
            'memory_percent': process.memory_percent()
        }