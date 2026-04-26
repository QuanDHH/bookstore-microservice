# AI Service

This is the AI Service for the E-commerce platform, implementing AI-powered recommendations, chat, and behavior prediction based on the provided PDF documentation.

## Features

- **Behavior Prediction**: Uses BiLSTM model to predict next user actions
- **Knowledge Graph**: Stores user-product-behavior relationships in Neo4j
- **RAG Chat**: AI-powered chat assistant using Claude API
- **Product Recommendations**: Collaborative filtering based on graph data

## Setup

1. Ensure Neo4j is running
2. Set CLAUDE_API_KEY in environment
3. Run data generation: `python generate_data.py`
4. Train model: `python train_model.py` (requires TensorFlow)
5. Load KB: `python load_kb.py`

## API Endpoints

- `POST /api/recommend/`: Get product recommendations
- `POST /api/chat/`: Chat with AI assistant
- `POST /api/predict/`: Predict user behavior

## Models

- `data_user500.csv`: Generated user behavior data
- `model_best.h5`: Trained BiLSTM model (if available)