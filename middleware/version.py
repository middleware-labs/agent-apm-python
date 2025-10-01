
"""Version and package information."""

print("[VERSION] Starting package detection...")

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("middleware-io").version
    __package_name__ = "middleware-io"
    print(f"[VERSION] ✓ Found: {__package_name__} v{__version__}")
    
except:
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("middleware-io-k8s").version
        __package_name__ = "middleware-io-k8s"
        print(f"[VERSION] ✓ Found: {__package_name__} v{__version__}")

    except:
        __version__ = "unknown"
        __package_name__ = "middleware-io"