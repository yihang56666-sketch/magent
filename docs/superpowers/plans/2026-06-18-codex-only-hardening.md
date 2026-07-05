# Codex-Only Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish converting the project to a Codex-only manual multi-agent workflow and then apply one evidence-based iteration from relevant open-source projects.

**Architecture:** Keep the existing routing and run-artifact structure, but remove external-model runtime assumptions from configuration, wrappers, build files, and documentation. After the baseline is clean, add one small orchestration improvement inspired by established open-source multi-agent projects without introducing new API dependencies.

**Tech Stack:** Python, PyInstaller, Markdown docs, existing Codex-oriented scripts

---
