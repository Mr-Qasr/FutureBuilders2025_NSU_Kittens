# FutureBuilders2025_NSU_Kittens

An AI-powered medical diagnosis application built for the Future Builders 2025 competition by NSU Kittens team.

## Project Overview

This project consists of an AI doctor system with the following components:

- **Backend**: Python Flask API server handling AI diagnosis orchestration
- **Frontend**: React/TypeScript application built with Vite
- **Models**: Local LLM models for reasoning and vision tasks
- **Core System**: Configuration, logging, and runtime management

## Features

- AI-powered medical diagnosis using local LLMs
- Web-based user interface
- Modular architecture with separate AI, API, and core modules
- Support for GGUF model formats
- Comprehensive logging and configuration management

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ai-doctor/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ai-doctor/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Models

The project includes pre-trained GGUF models in the `models/` directory:
- `reasoning/openchat-3.5-1210.Q3_K_S.gguf` - For reasoning tasks

## Project Structure

```
ai-doctor/
├── backend/           # Flask API server
│   ├── src/
│   │   ├── ai/        # AI diagnosis orchestrator and LLM client
│   │   ├── api/       # API routes
│   │   └── core/      # Configuration and logging
│   └── requirements.txt
├── frontend/          # React/TypeScript frontend
│   ├── src/
│   └── package.json
├── models/            # LLM models
└── src/               # Additional system components
```

## Usage

1. Start the backend server
2. Start the frontend development server
3. Access the application through the frontend interface
4. Input medical symptoms for AI-powered diagnosis

## Contributing

This project was developed by the NSU Kittens team for the Future Builders 2025 competition.

## License

[Add license information if applicable]