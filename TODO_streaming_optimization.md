# TODO: Make get_code_optimization Function Streaming-Based

## Task Overview
Convert the existing `get_code_optimization` function from a synchronous/blocking implementation to a streaming-based implementation that yields responses as they arrive.

## Current Implementation Analysis
- **Location**: `interview_corvus/core/llm_service.py`
- **Current behavior**: Synchronous function that waits for complete response
- **Usage locations**: 
  - `interview_corvus/api/api_handler.py` (line: optimization = self.llm_service.get_code_optimization(...))
  - `interview_corvus/ui/main_window.py` (line: optimization = self.llm_service.get_code_optimization(...))

## Implementation Plan

### Step 1: ✅ Analyze Current Function Structure
- [x] Review current `get_code_optimization` function implementation
- [x] Identify return type (`CodeOptimization` Pydantic model)
- [x] Understand how LlamaIndex handles streaming
- [x] Check how the function is called in API and UI layers

### Step 2: ✅ Research LlamaIndex Streaming Capabilities
- [x] Investigate LlamaIndex streaming methods for structured LLMs
- [x] Check if `llm.as_structured_llm()` supports streaming
- [x] Find alternative streaming approaches if structured streaming is not available
- [x] Understand how to handle partial responses with streaming

**Findings:**
- LlamaIndex LLMs typically support: `stream_chat()`, `stream_complete()`, `astream_chat()`, `astream_complete()`
- Structured LLMs may not support streaming directly - need to use regular streaming and parse incrementally
- Configuration already has `streaming: bool = False` setting available

### Step 3: ✅ Design Streaming Interface
- [x] Decide on streaming approach:
  - **Selected Option A**: Generator function that yields partial `CodeOptimization` objects
  - Uses callback-based approach for PyQt6 integration with signals
  - Supports both sync and async patterns
- [x] Define how partial responses will be structured
- [x] Plan error handling for streaming scenarios

**Design Decision:**
- Use generator that yields progressive `CodeOptimization` objects
- Add `is_complete` field to track completion status
- Emit PyQt signals for UI updates
- Fallback to non-streaming if streaming fails

### Step 4: ✅ Implement Streaming Function
- [x] Create new `get_code_optimization_stream` method
- [x] Implement streaming logic with LlamaIndex
- [x] Handle both structured and fallback streaming scenarios
- [x] Add proper error handling and recovery
- [x] Ensure compatibility with existing `CodeOptimization` model
- [x] Add streaming-specific signals to LLMService
- [x] Implement progressive parsing of streaming response
- [x] Add fallback to non-streaming mode when needed

### Step 5: ✅ Update API Handler
- [x] Modify `api_handler.py` to use streaming function
- [x] Implement server-sent events (SSE) for real-time updates
- [x] Update API response models to handle streaming
- [x] Add streaming optimization endpoint (`optimize_solution_stream`)
- [x] Keep non-streaming version as fallback
- [x] Add proper SSE headers and JSON formatting

### Step 6: ✅ Update UI Layer  
- [x] Modify `main_window.py` to handle streaming responses
- [x] Update threading approach for streaming
- [x] Add real-time UI updates during optimization
- [x] Show progress indicators and partial results
- [x] Add `on_optimization_progress` signal handler
- [x] Update optimization thread to support streaming
- [x] Connect streaming progress signals conditionally

### Step 7: ✅ Add Fallback Support
- [x] Keep original synchronous function as fallback (existing `get_code_optimization` function is preserved)
- [x] Add configuration option to choose between streaming/non-streaming (uses `settings.llm.streaming`)
- [x] Ensure backward compatibility (streaming function falls back to regular optimization on failure)
- [x] Automatic fallback when LLM doesn't support streaming
- [x] Error handling with graceful degradation

# Streaming Implementation Summary

## ✅ Completed Implementation

The `get_code_optimization` function has been successfully converted to a streaming-based implementation with the following key features:

### Core Streaming Function
- **`get_code_optimization_stream()`**: New generator function that yields partial `CodeOptimization` objects
- **Progressive parsing**: Incrementally parses streaming response with regex and JSON parsing
- **Progress tracking**: Tracks completion status with `is_complete` and `progress` fields
- **Automatic fallback**: Falls back to non-streaming mode if streaming fails or is disabled

### Model Updates
- **Extended `CodeOptimization` model**: Added `is_complete` and `progress` fields for streaming support
- **Backward compatibility**: Original fields remain unchanged, new fields have defaults

### UI Layer Integration
- **Real-time updates**: Added `on_optimization_progress()` handler for streaming updates
- **Threading support**: Modified optimization thread to handle streaming responses
- **Status indicators**: Progress percentage shown in status bar during streaming
- **Conditional signals**: Streaming signals only connected when streaming is enabled

### API Layer Integration
- **Server-Sent Events (SSE)**: Added `optimize_solution_stream()` method with SSE support
- **Dual endpoints**: Both streaming and non-streaming endpoints available
- **Progress metadata**: Stream includes progress, completion status, and type information
- **Error handling**: Graceful error handling with fallback to non-streaming

### Configuration & Fallback
- **Settings integration**: Uses existing `settings.llm.streaming` boolean flag
- **Graceful degradation**: Multiple fallback layers ensure reliability
- **LLM compatibility**: Automatically detects if LLM supports streaming
- **Error recovery**: Falls back to regular optimization on any streaming failure

## Key Benefits

1. **Real-time feedback**: Users see optimization progress as it happens
2. **Better UX**: No more waiting for lengthy optimizations without feedback
3. **Reliability**: Multiple fallback layers ensure functionality always works
4. **Backward compatibility**: Existing code continues to work unchanged
5. **Configuration control**: Streaming can be enabled/disabled via settings

## Usage

### Enable Streaming
Set `settings.llm.streaming = True` in configuration or settings dialog.

### API Usage
- **Non-streaming**: Use existing `/optimize` endpoint
- **Streaming**: Use new `/optimize-stream` endpoint with SSE client

### UI Usage
Streaming is automatically used when enabled in settings - no code changes needed.

## Files Modified
- ✅ `interview_corvus/core/models.py` - Added streaming fields
- ✅ `interview_corvus/core/llm_service.py` - Core streaming implementation
- ✅ `interview_corvus/ui/main_window.py` - UI streaming integration
- ✅ `interview_corvus/api/api_handler.py` - API streaming endpoint
