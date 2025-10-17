# AI Agent for Flight Booking

This AI agent provides intelligent flight booking assistance by understanding natural language queries and searching your flight database.

## Features

- **Natural Language Processing**: Understands user travel intentions from conversational input
- **Flight Search**: Searches flights based on extracted criteria
- **City & Airline Search**: Helps users find cities and airlines
- **Cheapest Flight Finder**: Finds the cheapest flights for specific routes
- **OpenAI Integration**: Uses OpenAI's GPT models for intent extraction and response generation
- **Function Calling**: Provides structured function schemas for external AI integrations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Add your OpenAI API key to your environment:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Database Migration

The AI agent uses existing models, so no additional migrations are needed.

## API Endpoints

### 1. Chat Endpoint (Main)

**POST** `/ai-agent/chat/`

Process natural language messages and return flight search results.

**Request:**
```json
{
    "message": "I want to fly from Tehran to Mashhad tomorrow",
    "session_id": "optional-session-id"
}
```

**Response:**
```json
{
    "message": "I found 5 flights for your trip from THR to MHD for 2024-01-15...",
    "intent": {
        "origin": "THR",
        "destination": "MHD", 
        "departure_date": "2024-01-15",
        "seat_class": null,
        "max_price": null,
        "airline_preference": null,
        "passengers": 1
    },
    "search_results": {
        "count": 5,
        "results": [...]
    },
    "requires_clarification": false,
    "clarification_questions": null,
    "session_id": "session-id"
}
```

### 2. Conversation Endpoint (Advanced)

**POST** `/ai-agent/conversation/`

Process conversations with message history and custom system instructions.

**Request:**
```json
{
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful flight booking assistant for Iranian domestic flights. Always be polite and provide detailed information.",
            "timestamp": "2024-01-15T10:00:00"
        },
        {
            "role": "user", 
            "content": "I need to travel from Tehran to Mashhad",
            "timestamp": "2024-01-15T10:01:00"
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help you find flights from Tehran to Mashhad. When would you like to travel?",
            "timestamp": "2024-01-15T10:01:30"
        },
        {
            "role": "user",
            "content": "Next Friday, and I prefer business class",
            "timestamp": "2024-01-15T10:02:00"
        }
    ],
    "system_instructions": "You are a specialized flight booking assistant. Always provide prices in Iranian Rial and mention airline names in Persian when available."
}
```

**Response:**
```json
{
    "message": "I found several business class options for your trip from Tehran to Mashhad next Friday. Here are the best options...",
    "intent": {
        "origin": "THR",
        "destination": "MHD",
        "departure_date": "2024-01-19",
        "seat_class": "Business",
        "max_price": null,
        "airline_preference": null,
        "passengers": 1
    },
    "search_results": {
        "count": 3,
        "results": [...]
    },
    "requires_clarification": false,
    "clarification_questions": null
}
```

### 3. Direct Flight Search

**POST** `/ai-agent/search_flights/`

Direct flight search with structured parameters.

**Request:**
```json
{
    "origin": "THR",
    "destination": "MHD",
    "departure_timestamp_gte": 1705276800,
    "departure_timestamp_lte": 1705363200,
    "seat_classes": ["Economy"],
    "max_price": 500.0
}
```

### 4. Cheapest Flights

**POST** `/ai-agent/get_cheapest_flights/`

Find cheapest flights for a route within a date range.

**Request:**
```json
{
    "origin": "THR",
    "destination": "MHD",
    "reference_date": "2024-01-15",
    "forward_days": 7,
    "backward_days": 7
}
```

### 5. City Search

**GET** `/ai-agent/search_cities/?query=tehran`

Search for cities by name or code.

### 6. Airline Search

**GET** `/ai-agent/search_airlines/?query=iran`

Search for airlines by name.

### 7. Function Schema

**GET** `/ai-agent/get_function_schema/`

Get OpenAI function calling schema for external integrations.

## OpenAI Function Calling Schema

The AI agent provides these functions for OpenAI integration:

### 1. search_flights
```json
{
    "name": "search_flights",
    "description": "Search for flights between two cities with specific criteria",
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin city code (e.g., 'THR', 'MHD', 'IFN')"},
            "destination": {"type": "string", "description": "Destination city code"},
            "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
            "return_date": {"type": "string", "description": "Return date in YYYY-MM-DD format (for round trips)"},
            "seat_class": {"type": "string", "enum": ["Economy", "Premium Economy", "Business", "First"]},
            "max_price": {"type": "number", "description": "Maximum price limit"},
            "airline_preference": {"type": "array", "items": {"type": "string"}},
            "passengers": {"type": "integer", "default": 1}
        },
        "required": ["origin", "destination", "departure_date"]
    }
}
```

### 2. get_cheapest_flights
```json
{
    "name": "get_cheapest_flights",
    "description": "Find the cheapest flights for a route within a date range",
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin city code"},
            "destination": {"type": "string", "description": "Destination city code"},
            "reference_date": {"type": "string", "description": "Reference date in YYYY-MM-DD format"},
            "forward_days": {"type": "integer", "default": 7},
            "backward_days": {"type": "integer", "default": 7}
        },
        "required": ["origin", "destination", "reference_date"]
    }
}
```

### 3. search_cities
```json
{
    "name": "search_cities",
    "description": "Search for cities by name or get all available cities",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "City name or code to search for"}
        }
    }
}
```

### 4. search_airlines
```json
{
    "name": "search_airlines",
    "description": "Search for airlines by name",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Airline name to search for"}
        }
    }
}
```

## Usage Examples

### Example 1: Basic Flight Search
```bash
curl -X POST http://localhost:8000/ai-agent/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a flight from Tehran to Mashhad on January 15th, 2024"
  }'
```

### Example 2: Conversation with Context
```bash
curl -X POST http://localhost:8000/ai-agent/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful flight booking assistant. Always provide prices in Iranian Rial.",
        "timestamp": "2024-01-15T10:00:00"
      },
      {
        "role": "user",
        "content": "I need to travel from Tehran to Mashhad",
        "timestamp": "2024-01-15T10:01:00"
      },
      {
        "role": "assistant", 
        "content": "I can help you find flights from Tehran to Mashhad. When would you like to travel?",
        "timestamp": "2024-01-15T10:01:30"
      },
      {
        "role": "user",
        "content": "Next Friday, business class preferred",
        "timestamp": "2024-01-15T10:02:00"
      }
    ],
    "system_instructions": "Always mention airline names in Persian when available and provide detailed flight information."
  }'
```

### Example 3: Custom System Instructions
```bash
curl -X POST http://localhost:8000/ai-agent/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Find me cheap flights from THR to MHD next week",
        "timestamp": "2024-01-15T10:00:00"
      }
    ],
    "system_instructions": "You are a budget travel specialist. Always recommend the cheapest options first and mention any additional fees or restrictions. Be enthusiastic about saving money!"
  }'
```

### Example 4: Flexible Date Search
```bash
curl -X POST http://localhost:8000/ai-agent/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me the cheapest flights from THR to MHD next week, business class, under $300"
  }'
```

### Example 5: Round Trip
```bash
curl -X POST http://localhost:8000/ai-agent/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to book a round trip from Tehran to Isfahan, leaving January 20th and returning January 25th"
  }'
```

### Example 6: City Search
```bash
curl -X GET "http://localhost:8000/ai-agent/search_cities/?query=tehran"
```

## Integration with OpenAI Agent Builder

To use this with OpenAI's Agent Builder:

1. **Get the Function Schema:**
   ```bash
   curl -X GET http://localhost:8000/ai-agent/get_function_schema/
   ```

2. **Configure Your Agent:**
   - Use the returned function schema in your OpenAI agent configuration
   - Set the base URL to your Django server
   - Configure authentication if needed

3. **Example Agent Configuration:**
   ```json
   {
     "name": "flight_booking_agent",
     "description": "AI agent for flight booking assistance",
     "functions": [
       {
         "name": "search_flights",
         "description": "Search for flights between two cities",
         "parameters": {
           "type": "object",
           "properties": {
             "origin": {"type": "string"},
             "destination": {"type": "string"},
             "departure_date": {"type": "string"}
           }
         }
       }
     ],
     "api_endpoint": "http://your-server.com/ai-agent/chat/"
   }
   ```

## Architecture

The AI agent consists of:

- **AIAgentService**: Main service handling AI interactions and database queries
- **AIAgentViewSet**: REST API endpoints
- **Interfaces**: Abstract interfaces and data classes
- **OpenAI Integration**: Function calling and natural language processing

## Error Handling

The agent handles various error scenarios:

- Missing or invalid travel information
- No flights found for criteria
- OpenAI API errors
- Database connection issues
- Invalid date formats

## Security Considerations

- API key should be stored securely
- Consider rate limiting for production use
- Validate user inputs
- Implement proper authentication for production

## Performance Optimization

- Results are cached where appropriate
- Database queries are optimized
- OpenAI calls are made only when necessary
- Session management for conversation context

## Future Enhancements

- Conversation memory and context
- Multi-language support
- Advanced filtering options
- Integration with booking systems
- Analytics and usage tracking
