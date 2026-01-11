"""
Utility decorators for production-grade error handling and monitoring.

Includes retry logic, performance monitoring, and error tracking.
"""

import time
import functools
from typing import Callable, Any, TypeVar, ParamSpec

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = None,
    initial_delay: float = None,
    backoff_factor: float = None,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default from config)
        initial_delay: Initial delay between retries in seconds (default from config)
        backoff_factor: Multiplier for delay after each retry (default from config)
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function
        
    Example:
        @retry_with_backoff(max_retries=3, exceptions=(OpenAIError,))
        def call_api():
            return client.chat.completions.create(...)
    """
    max_retries = max_retries or Config.MAX_RETRIES
    initial_delay = initial_delay or Config.RETRY_DELAY
    backoff_factor = backoff_factor or Config.RETRY_BACKOFF
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    
                    time.sleep(delay)
                    delay *= backoff_factor
            
            # This should never be reached, but mypy needs it
            raise last_exception
        
        return wrapper
    return decorator


def timeit(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to measure and log function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function
        
    Example:
        @timeit
        def slow_function():
            time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            if elapsed_time > 1.0:
                logger.info(
                    f"{func.__name__} completed in {elapsed_time:.2f}s"
                )
            else:
                logger.debug(
                    f"{func.__name__} completed in {elapsed_time:.3f}s"
                )
            
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {elapsed_time:.2f}s: {e}"
            )
            raise
    
    return wrapper


def log_errors(
    func: Callable[P, T],
    reraise: bool = True
) -> Callable[P, T]:
    """
    Decorator to log exceptions with full context.
    
    Args:
        func: Function to wrap
        reraise: Whether to re-raise the exception after logging
        
    Returns:
        Decorated function
        
    Example:
        @log_errors
        def risky_function():
            raise ValueError("Something went wrong")
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(
                f"Exception in {func.__name__}: {type(e).__name__}: {e}",
                exc_info=True
            )
            if reraise:
                raise
            return None
    
    return wrapper


def cache_result(ttl_seconds: int = 3600) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Simple cache decorator with time-to-live.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        
    Returns:
        Decorated function
        
    Example:
        @cache_result(ttl_seconds=300)
        def expensive_computation(x):
            return x ** 2
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Create cache key from args and kwargs
            cache_key = str((args, sorted(kwargs.items())))
            current_time = time.time()
            
            # Check if we have a valid cached result
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    logger.debug(f"{func.__name__} cache hit")
                    return result
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            logger.debug(f"{func.__name__} cache miss, computed new result")
            
            # Clean old cache entries
            cache_keys_to_delete = [
                key for key, (_, timestamp) in cache.items()
                if current_time - timestamp >= ttl_seconds
            ]
            for key in cache_keys_to_delete:
                del cache[key]
            
            return result
        
        return wrapper
    return decorator


def validate_inputs(**validators) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to validate function inputs.
    
    Args:
        **validators: Keyword arguments mapping parameter names to validation functions
        
    Returns:
        Decorated function
        
    Example:
        @validate_inputs(
            age=lambda x: 0 < x < 150,
            email=lambda x: '@' in x
        )
        def create_user(age: int, email: str):
            ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for parameter '{param_name}' "
                            f"with value {value}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

