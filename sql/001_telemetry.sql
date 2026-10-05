CREATE TABLE IF NOT EXISTS observability.llm_events
(
    timestamp DateTime64(3),
    trace_id String,
    span_id String,
    parent_span_id String,
    service String,
    operation String,
    model String,
    status String,
    duration_ms UInt32,
    input_tokens UInt32,
    output_tokens UInt32,
    cost_usd Float64,
    error_message String
)
ENGINE = MergeTree
ORDER BY (service, timestamp, trace_id);
