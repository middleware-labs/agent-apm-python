import unittest
from unittest.mock import patch, mock_open
import os
import sys
from configparser import ConfigParser
from config import Config  # Replace 'your_module' with the name of your module
import os
class TestConfig(unittest.TestCase):

    def setUp(self):
        # Save the original environment variables
        self._original_env = dict(os.environ)
        
    def tearDown(self):
        # Restore the original environment variables
        os.environ.clear()
        os.environ.update(self._original_env)
        
    # If config file is empty && envs are not set, properties should be set to defaults
    def test_empty_config(self):
        # Passing test config values
        import os
        os.environ["MIDDLEWARE_CONFIG_FILE"] = os.path.join(os.getcwd(), 'testfiles/middleware_empty.ini')
        obj = Config()
        
        self.assertEqual(obj.project_name, None)
        # self.asse(obj.service_name, None)
        self.assertEqual(obj.access_token, "")
        self.assertEqual(obj.collect_traces, True)
        self.assertEqual(obj.collect_metrics, False)
        self.assertEqual(obj.collect_logs, False)
        self.assertEqual(obj.collect_profiling, False)
        self.assertEqual(obj.otel_propagators, "b3")
        self.assertEqual(obj.mw_agent_service, "localhost")
        self.assertEqual(obj.target, "")
        self.assertEqual(obj.custom_resource_attributes, "")
        self.assertEqual(obj.log_level, "FATAL")
        
    def test_env_overrides(self):
        # Setting configs with Middleware specific 
        os.environ["MIDDLEWARE_CONFIG_FILE"] = os.path.join(os.getcwd(), 'testfiles/middleware_default.ini')
        os.environ["MW_PROJECT_NAME"] = "project123"
        os.environ["MW_SERVICE_NAME"] = "service123"
        os.environ["MW_API_KEY"] = "xxxyyyzzz"
        os.environ["MW_APM_COLLECT_TRACES"] = "false"
        os.environ["MW_APM_COLLECT_METRICS"] = "true"
        os.environ["MW_APM_COLLECT_LOGS"] = "true"
        os.environ["MW_APM_COLLECT_PROFILING"] = "true"
        os.environ["MW_PROPAGATORS"] = "w3c"
        os.environ["MW_TARGET"] = "http://test.middleware.io"
        os.environ["MW_CUSTOM_RESOURCE_ATTRIBUTES"] = "test=123,test2=1234"
        os.environ["MW_LOG_LEVEL"] = "DEBUG"
    
        obj = Config()
        self.assertEqual(obj.project_name, "project123")
        self.assertEqual(obj.service_name, "service123")
        self.assertEqual(obj.access_token, "xxxyyyzzz")
        self.assertEqual(obj.collect_traces, False)
        self.assertEqual(obj.collect_metrics, True)
        self.assertEqual(obj.collect_logs, True)
        self.assertEqual(obj.collect_profiling, True)
        self.assertEqual(obj.otel_propagators, "w3c")
        self.assertEqual(obj.mw_agent_service, "localhost")
        self.assertEqual(obj.target, "http://test.middleware.io")
        self.assertEqual(obj.custom_resource_attributes, "test=123,test2=1234")
        self.assertEqual(obj.log_level, "DEBUG")
        
    def test_otel_env_overrides(self):                
        # Middleware Specific ENVs
        os.environ["MIDDLEWARE_CONFIG_FILE"] = os.path.join(os.getcwd(), 'testfiles/middleware_default.ini')
        os.environ["MW_PROJECT_NAME"] = "project123"
        os.environ["MW_SERVICE_NAME"] = "service123"
        os.environ["MW_API_KEY"] = "xxxyyyzzz"
        os.environ["MW_APM_COLLECT_TRACES"] = "false"
        os.environ["MW_APM_COLLECT_METRICS"] = "true"
        os.environ["MW_APM_COLLECT_LOGS"] = "true"
        os.environ["MW_APM_COLLECT_PROFILING"] = "true"
        os.environ["MW_PROPAGATORS"] = "w3c"
        os.environ["MW_TARGET"] = "http://test.middleware.io"
        os.environ["MW_CUSTOM_RESOURCE_ATTRIBUTES"] = "test=123,test2=1234"
        os.environ["MW_LOG_LEVEL"] = "DEBUG"
        
        # OTEL ENVs
        os.environ["OTEL_SERVICE_NAME"] = "otel-service123"
        os.environ["OTEL_PROPAGATORS"] = "otel-b3"
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://otel-test.middleware.io"
    
        obj = Config()
        self.assertEqual(obj.project_name, "project123")
        self.assertEqual(obj.service_name, "otel-service123")
        self.assertEqual(obj.access_token, "xxxyyyzzz")
        self.assertEqual(obj.collect_traces, False)
        self.assertEqual(obj.collect_metrics, True)
        self.assertEqual(obj.collect_logs, True)
        self.assertEqual(obj.collect_profiling, True)
        self.assertEqual(obj.otel_propagators, "otel-b3")
        self.assertEqual(obj.mw_agent_service, "localhost")
        self.assertEqual(obj.target, "http://otel-test.middleware.io")
        self.assertEqual(obj.custom_resource_attributes, "test=123,test2=1234")
        self.assertEqual(obj.log_level, "DEBUG")

    def test_str_to_bool(self):
        config = Config()
        self.assertTrue(config.str_to_bool('true', False))
        self.assertFalse(config.str_to_bool('false', True))
        self.assertTrue(config.str_to_bool('yes', False))
        self.assertFalse(config.str_to_bool('no', True))
        self.assertTrue(config.str_to_bool('1', False))
        self.assertFalse(config.str_to_bool('0', True))
        self.assertEqual(config.str_to_bool('invalid', True), True)
        self.assertEqual(config.str_to_bool('', True), True)
        
    def test_mw_serverless(self):
        
        os.environ["MW_SERVICE_NAME"] = "service123"
        os.environ["MW_TARGET"] = "http://test.middleware.io"
        obj = Config()
        self.assertIn("mw_serverless",obj.resource_attributes)
        
    def test_not_mw_serverless(self):
        os.environ["MW_SERVICE_NAME"] = "service1234"
        os.environ["MIDDLEWARE_CONFIG_FILE"] = os.path.join(os.getcwd(), 'testfiles/middleware_default.ini')
        obj = Config()
        self.assertNotIn("mw_serverless",obj.resource_attributes)
        
if __name__ == '__main__':
    unittest.main()
