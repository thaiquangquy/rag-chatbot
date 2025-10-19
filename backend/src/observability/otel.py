"""Basic OpenTelemetry configuration."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing(service_name: str = "rag-chatbot") -> None:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)
