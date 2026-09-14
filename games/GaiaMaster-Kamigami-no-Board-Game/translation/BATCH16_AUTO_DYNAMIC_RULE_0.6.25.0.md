# Batch 16 auto dynamic rule

Promote a curated Japanese semantic string into the dynamic-literal sweep only when all conditions pass:

- source contains Japanese text;
- source has no percent-format token;
- source has no /V or /v runtime control token;
- source length is at least 3 characters;
- estimated Vietnamese runtime bytes are not larger than the original CP932 source bytes.

This deterministic rule produced 100 safe duplicate candidates in the 0.6.25.0 local builder. The goal is to catch duplicate Japanese literals outside the main Translation Master offsets.
