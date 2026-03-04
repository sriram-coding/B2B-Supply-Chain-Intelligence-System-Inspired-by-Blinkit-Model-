Enterprise B2B Supply Chain AI Platform

AI-powered Intelligence System for Modern Quick-Commerce Operations

------------------------------------------------------------

Overview

This project is a production-style enterprise AI platform designed to simulate how a modern quick-commerce organization can manage and optimize its B2B supply chain operations.

It combines Knowledge Graphs, Vector Search, and Large Language Models to deliver intelligent operational insights through dashboards, analytics, and conversational AI.

Key capabilities include:

- Real-time KPI dashboards
- Employee performance analytics and scoring
- Vendor and logistics insights
- Interactive supply chain knowledge graph
- RAG-powered AI assistant for operational queries

This project demonstrates how hybrid AI systems can support enterprise-level decision-making in supply chain environments.

Note: This is an academic and portfolio project inspired by quick-commerce business models. It is not affiliated with or endorsed by any real company.

------------------------------------------------------------

System Architecture

Structured Data (CSV/JSON)
    ->
LLM-based Extraction and Processing (Groq)
    ->
Knowledge Graph (Neo4j)
    ->
Vector Indexing (Pinecone)
    ->
RAG Pipeline
    ->
Interactive Dashboard (Streamlit)

------------------------------------------------------------

Core Features

1. Real-Time KPI Dashboard
   Displays operational metrics, employee performance indicators, and vendor insights through interactive visualizations.

2. Employee Performance Engine
   Automated scoring system that evaluates employees based on measurable metrics and classifies them into performance tiers.

3. Knowledge Graph
   Models relationships between vendors, logistics partners, contracts, and employees using Neo4j with interactive visualization.

4. AI Assistant (RAG-based)
   Uses semantic retrieval from Pinecone combined with LLM reasoning to answer operational questions with multi-turn conversation support.

------------------------------------------------------------

Performance Scoring Model

raw_score =
(projects_handled × 2) +
(clients_managed × 3) +
(tasks_completed × 0.5) +
(on_time_delivery_rate × 5)

final_score = normalized to a scale of 0–100

Tier Classification:

Elite: 85–100
High Performer: 65–84
Moderate: 45–64
Needs Improvement: 0–44

------------------------------------------------------------

Tech Stack

LLM: Groq (Llama 3 8B)
Graph Database: Neo4j
Vector Database: Pinecone
Embeddings: sentence-transformers (MiniLM)
Frontend: Streamlit
Visualization: Plotly and Pyvis
Orchestration: LangChain
Configuration: python-dotenv

------------------------------------------------------------

Setup

1. Create virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Configure .env file
4. Run application:
   streamlit run streamlit_app.py

------------------------------------------------------------

Project Objective

- Hybrid AI architecture (Graph + Vector + LLM)
- Enterprise data modeling
- Retrieval-Augmented Generation (RAG)
- Supply chain intelligence simulation
- Modular production-style Python development

------------------------------------------------------------