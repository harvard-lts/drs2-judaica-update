import os
import logging
import requests
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter)
from opentelemetry.sdk.resources import SERVICE_NAME

# tracing setup
JAEGER_NAME = os.getenv('JAEGER_NAME')
JAEGER_SERVICE_NAME = os.getenv('JAEGER_SERVICE_NAME')

resource = Resource(attributes={SERVICE_NAME: JAEGER_SERVICE_NAME})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=JAEGER_NAME, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

logger = logging.getLogger('drs2_judaica_update')

"""
This is the worker class for judaica updates.

Since: 2023=4-02-16
Author: cgoines
"""


class Worker():
    version = None

    def __init__(self):
        self.version = os.getenv("APP_VERSION", "0.0.1")

    def get_version(self):
        return self.version

    # this is call to the DASH healthcheck for integration testing
    def call_api(self):
        with tracer.start_as_current_span("server_request",
                                          attributes={"endpoint":
                                                      "/call_api"}):
            url = "https://dash.harvard.edu/rest/test"
            r = requests.get(url)
            span = trace.get_current_span()
            span.add_event("log", {"call.api": r.text})
            logger.debug("call.api: " + r.text)
            return r.text
