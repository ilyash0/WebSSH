UPLOAD_DIR = "/bin"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 * 60  # sec
JWT_ALGORITHM = "HS256"
SERVER_EXCEPTIONS_CODES = (
    500, 502, 503, 504, 505, 506, 507, 508, 510, 511, AttributeError, TypeError, ValueError, NameError, IndexError,
    OSError, IOError, SyntaxError, Exception, TimeoutError, RuntimeError, KeyError, EnvironmentError, ImportError,
    ArithmeticError, NotImplementedError, RecursionError, ZeroDivisionError, PermissionError)
RATE_LIMIT = "5/minute"
ENABLE_RECAPTCHA = True
