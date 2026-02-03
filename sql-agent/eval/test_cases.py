"""Chinook-specific test cases for SQL agent evaluation."""

TEST_CASES = [
    # --- Simple lookups ---
    {
        "id": "simple_001",
        "question": "What are all the genres?",
        "expected_answer_contains": ["Rock", "Jazz", "Metal"],
        "category": "simple",
    },
    {
        "id": "simple_002",
        "question": "List all media types.",
        "expected_answer_contains": ["MPEG", "AAC"],
        "category": "simple",
    },
    {
        "id": "simple_003",
        "question": "What are the names of all playlists?",
        "expected_answer_contains": ["Music", "Movies"],
        "category": "simple",
    },
    {
        "id": "simple_004",
        "question": "Show me the first 5 artist names.",
        "expected_answer_contains": ["AC/DC"],
        "category": "simple",
    },
    # --- Aggregations ---
    {
        "id": "agg_001",
        "question": "How many employees are there?",
        "expected_answer_contains": ["8"],
        "category": "aggregation",
    },
    {
        "id": "agg_002",
        "question": "What is the total number of tracks?",
        "expected_answer_contains": ["3,503"],
        "category": "aggregation",
    },
    {
        "id": "agg_003",
        "question": "How many albums are in the database?",
        "expected_answer_contains": ["347"],
        "category": "aggregation",
    },
    {
        "id": "agg_004",
        "question": "What is the total amount of all invoices?",
        "expected_answer_contains": ["2328.6"],
        "category": "aggregation",
    },
    # --- Joins ---
    {
        "id": "join_001",
        "question": "List all albums by AC/DC.",
        "expected_answer_contains": ["For Those About To Rock", "Let There Be Rock"],
        "category": "join",
    },
    {
        "id": "join_002",
        "question": "Which albums did Iron Maiden release?",
        "expected_answer_contains": ["Iron Maiden"],
        "category": "join",
    },
    # --- Filters ---
    {
        "id": "filter_001",
        "question": "Which customers are from Brazil?",
        "expected_answer_contains": ["Luís", "Gonçalves"],
        "category": "filter",
    },
    {
        "id": "filter_002",
        "question": "List employees who were hired after 2002.",
        "expected_answer_contains": ["2003", "2004"],
        "category": "filter",
    },
    {
        "id": "filter_003",
        "question": "Which tracks are longer than 5 minutes?",
        "expected_answer_contains": ["300000"],
        "category": "filter",
    },
    # --- Complex ---
    {
        "id": "complex_001",
        "question": "Who are the top 3 customers by total purchase amount?",
        "expected_answer_contains": ["Helena", "Richard", "Luis"],
        "category": "complex",
    },
    {
        "id": "complex_002",
        "question": "Which artist has the most albums?",
        "expected_answer_contains": ["Iron Maiden"],
        "category": "complex",
    },
    {
        "id": "complex_003",
        "question": "What are the top 5 best-selling tracks by number of times purchased?",
        "expected_answer_contains": ["track"],
        "category": "complex",
    },
]
