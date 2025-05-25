#!/usr/bin/env python3

"""
Dify Plugin Entry Point: HTML to Markdown Converter
"""

import logging
import sys

# Configure logging to stderr to avoid JSON protocol conflicts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point - create plugin with comprehensive config."""
    try:
        # Import dify_plugin
        from dify_plugin import Plugin
        
        # Try to use the real DifyPluginEnv first
        try:
            from dify_plugin.config.config import DifyPluginEnv
            
            # Try to find the correct InstallMethod
            InstallMethod = None
            try:
                from dify_plugin.entities.install_method import InstallMethod
                logger.info("Found InstallMethod via entities.install_method")
            except ImportError:
                try:
                    from dify_plugin.config.install_method import InstallMethod  
                    logger.info("Found InstallMethod via config.install_method")
                except ImportError:
                    # Create compatible enum
                    from enum import Enum
                    class InstallMethod(Enum):
                        Local = "Local"
                        Remote = "Remote"
                        Serverless = "Serverless"
            
            # Try to create DifyPluginEnv with minimal required fields
            config = DifyPluginEnv(INSTALL_METHOD="local")  # Use string value, not enum
            logger.info("✓ Created DifyPluginEnv successfully")
            
        except Exception as e:
            logger.warning(f"Could not create DifyPluginEnv: {e}, creating comprehensive config")
            
            # Find InstallMethod
            InstallMethod = None
            try:
                # Look in the plugin module
                import dify_plugin.plugin
                plugin_module = dify_plugin.plugin
                for name, obj in vars(plugin_module).items():
                    if hasattr(obj, 'Local') and hasattr(obj, 'Remote'):
                        InstallMethod = obj
                        break
                        
                if InstallMethod is None:
                    from dify_plugin.entities.install_method import InstallMethod
                    
            except ImportError:
                # Create compatible enum
                from enum import Enum
                class InstallMethod(Enum):
                    Local = "Local"
                    Remote = "Remote"
                    Serverless = "Serverless"
            
            # Create comprehensive config with all common Dify attributes
            class PluginConfig:
                def __init__(self):
                    # Core plugin configuration
                    self.INSTALL_METHOD = "local"  # Use string value, not enum
                    
                    # Worker configuration
                    self.MAX_WORKER = 10
                    
                    # Daemon configuration  
                    self.DIFY_PLUGIN_DAEMON_URL = "http://localhost:5003"
                    
                    # Heartbeat configuration
                    self.HEARTBEAT_INTERVAL = 30
                    
                    # Plugin paths and directories
                    self.PLUGIN_PATH = "."
                    self.PLUGIN_DIR = "."
                    self.PLUGIN_DATA_DIR = "./data"
                    self.PLUGIN_LOG_DIR = "./logs"
                    
                    # Logging configuration
                    self.DEBUG = False
                    self.LOG_LEVEL = "INFO"
                    self.ENABLE_DEBUG_LOG = False
                    
                    # Network configuration
                    self.HTTP_TIMEOUT = 30
                    self.MAX_RETRIES = 3
                    
                    # Security configuration
                    self.PLUGIN_ID = "jake/html_to_markdown"
                    self.PLUGIN_VERSION = "0.1.0"
                    
                    # Environment configuration
                    self.ENV = "production"
                    self.PYTHON_VERSION = "3.12"
                    
                    # Tool configuration
                    self.TOOL_TIMEOUT = 60
                    self.MAX_TOOL_CALLS = 100
                    
                    # Plugin server configuration
                    self.HOST = "localhost"
                    self.PORT = 5003
                    self.PROTOCOL = "http"
            
            config = PluginConfig()
            logger.info("✓ Created comprehensive PluginConfig")
        
        logger.info(f"Config INSTALL_METHOD: {config.INSTALL_METHOD} (type: {type(config.INSTALL_METHOD)})")
        
        # Create plugin instance
        plugin = Plugin(config)
        logger.info("✓ Plugin created successfully!")
        
        # Start serving
        plugin.run()
        
    except Exception as e:
        logger.error(f"Plugin failed to start: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
