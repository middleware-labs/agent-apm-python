
"""Version and package information."""

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("middleware-io").version
    __package_name__ = "middleware-io"
    
except:
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("middleware-io-k8s").version
        __package_name__ = "middleware-io-k8s"

    except:
        __version__ = "unknown"
        __package_name__ = "middleware-io"