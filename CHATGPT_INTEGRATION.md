# ChatGPT Function Calling Configuration for ARC Raiders API

## How to Add This to ChatGPT

⚠️ **Important**: ChatGPT Actions cannot connect to localhost servers. You need to deploy your API to a public server first.

### Quick Deployment Options:

1. **Railway** (Recommended - Free tier available):
   ```bash
   ./deploy.sh
   # Choose option 3 for Railway setup
   ```

2. **ngrok** (For testing):
   ```bash
   # Install ngrok, then:
   python rest_api_server.py &
   ngrok http 5001
   # Use the https URL provided by ngrok
   ```

### Option 1: ChatGPT Plus with Actions (GPTs)

If you have ChatGPT Plus, you can create a custom GPT with these function definitions:

1. Go to https://chat.openai.com/gpts/editor
2. Create a new GPT
3. In the "Actions" section, import this OpenAPI schema:

```yaml
openapi: 3.1.0
info:
  title: ARC Raiders Map Conditions API
  description: Get real-time ARC Raiders map conditions
  version: 1.0.0
servers:
  - url: https://arc-raiders-production.up.railway.app
    description: Production server

paths:
  /api/v1/conditions:
    get:
      operationId: getAllMapConditions
      summary: Get all map conditions
      description: Get current active map conditions for all ARC Raiders maps
      parameters:
        - name: format
          in: query
          description: Output format
          required: false
          schema:
            type: string
            enum: [json, text, summary]
            default: json
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  format:
                    type: string
                  data:
                    oneOf:
                      - type: object
                      - type: string

  /api/v1/conditions/{map_name}:
    get:
      operationId: getSpecificMapCondition
      summary: Get specific map condition
      description: Get condition details for a specific map
      parameters:
        - name: map_name
          in: path
          required: true
          description: Name of the map (use hyphens, e.g., dam-battlegrounds)
          schema:
            type: string
            enum: 
              - dam-battlegrounds
              - buried-city
              - the-spaceport
              - the-blue-gate
              - practice-range
              - stella-montis
        - name: format
          in: query
          required: false
          description: Output format
          schema:
            type: string
            enum: [json, text]
            default: json
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  format:
                    type: string
                  data:
                    oneOf:
                      - type: object
                      - type: string
        '404':
          description: Map not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string

  /api/v1/conditions/active:
    get:
      operationId: getActiveConditionsOnly
      summary: Get active conditions only
      description: Get only maps that currently have active conditions
      parameters:
        - name: major_only
          in: query
          required: false
          description: If true, only return maps with major conditions
          schema:
            type: boolean
            default: false
        - name: format
          in: query
          required: false
          description: Output format
          schema:
            type: string
            enum: [json, text, summary]
            default: json
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  format:
                    type: string
                  data:
                    oneOf:
                      - type: object
                      - type: string

  /api/v1/conditions/upcoming:
    get:
      operationId: getUpcomingConditions
      summary: Get upcoming conditions
      description: Get upcoming conditions and their timing for all maps
      parameters:
        - name: format
          in: query
          required: false
          description: Output format
          schema:
            type: string
            enum: [json, text]
            default: json
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  format:
                    type: string
                  data:
                    oneOf:
                      - type: object
                      - type: string

  /health:
    get:
      operationId: healthCheck
      summary: Health check
      description: Check if the API is running
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  service:
                    type: string
                  timestamp:
                    type: string
```

### Option 2: Manual Function Calling (ChatGPT Plus)

If you prefer to use function calling directly, provide ChatGPT with these function definitions:

```json
{
  "functions": [
    {
      "name": "get_arc_raiders_conditions",
      "description": "Get current ARC Raiders map conditions for all maps",
      "parameters": {
        "type": "object",
        "properties": {
          "format": {
            "type": "string",
            "enum": ["json", "text", "summary"],
            "description": "Output format for the response",
            "default": "text"
          }
        }
      }
    },
    {
      "name": "get_specific_map_condition", 
      "description": "Get condition details for a specific ARC Raiders map",
      "parameters": {
        "type": "object",
        "properties": {
          "map_name": {
            "type": "string",
            "enum": ["dam-battlegrounds", "buried-city", "the-spaceport", "the-blue-gate", "practice-range", "stella-montis"],
            "description": "Name of the specific map to query"
          },
          "format": {
            "type": "string", 
            "enum": ["json", "text"],
            "description": "Output format",
            "default": "text"
          }
        },
        "required": ["map_name"]
      }
    },
    {
      "name": "get_active_conditions_only",
      "description": "Get only ARC Raiders maps that currently have active conditions",
      "parameters": {
        "type": "object",
        "properties": {
          "major_only": {
            "type": "boolean",
            "description": "If true, only return maps with major conditions",
            "default": false
          },
          "format": {
            "type": "string",
            "enum": ["json", "text", "summary"], 
            "description": "Output format",
            "default": "text"
          }
        }
      }
    },
    {
      "name": "get_upcoming_conditions",
      "description": "Get upcoming ARC Raiders conditions and their timing",
      "parameters": {
        "type": "object",
        "properties": {
          "format": {
            "type": "string",
            "enum": ["json", "text"],
            "description": "Output format", 
            "default": "text"
          }
        }
      }
    }
  ]
}
```

## Usage Examples

Once set up, you can ask ChatGPT:

- "What are the current ARC Raiders map conditions?"
- "Show me only maps with active conditions"
- "What's the condition on Dam Battlegrounds?"
- "Which maps have major conditions?"
- "What conditions are coming up next?"

## Server Setup

### Local Development

1. Start the REST API server:
```bash
python rest_api_server.py
```
The server will start on `https://localhost:5001`

2. Test the endpoints:
```bash
curl https://arc-raiders-production.up.railway.app/api/v1/conditions
curl https://arc-raiders-production.up.railway.app/api/v1/conditions/dam-battlegrounds
curl https://arc-raiders-production.up.railway.app/api/v1/conditions/active?major_only=true
```

**Important**: ChatGPT Actions require:
- Public HTTPS endpoint (localhost won't work)
- Valid SSL certificate
- Replace the server URL in the OpenAPI schema with your actual deployment URL

### Quick Testing with ngrok:
```bash
# Use the provided script for quick testing
./setup_chatgpt_testing.sh
```
This will start your API and create a public HTTPS tunnel for ChatGPT testing.

### Production Deployment

**Free Options** (Perfect for ChatGPT integration):

1. **Railway.app** (Recommended):
   - Free tier: 500 hours/month
   - Automatic HTTPS
   - Simple git-based deployment
   ```bash
   ./deploy.sh  # Choose option 3
   ```

2. **Render.com**:
   - Free tier available
   - Auto-deploy from GitHub
   - Built-in HTTPS

3. **Fly.io**:
   - Free tier: 3 shared CPU apps
   - Global deployment
   - Automatic HTTPS

**Paid Options**:
- **Heroku**: Easy deployment with git
- **DigitalOcean App Platform**: Managed deployment
- **AWS Lambda**: Serverless option
- **Google Cloud Run**: Container-based deployment

After deployment, update the OpenAPI schema `servers` section with your production URL:
```yaml
servers:
  - url: https://arc-raiders-production.up.railway.app
    description: Production server
```

## Alternative: Third-Party Services

### Option 3: Zapier/Make.com Integration
- Create a webhook that calls your API
- Connect it to ChatGPT via Zapier's ChatGPT integration
- Allows ChatGPT to trigger your API through automation

### Option 4: Browser Extension
- Create a browser extension that injects the API data
- ChatGPT can reference the data when it's visible on the page
- More complex but works with free ChatGPT

## Security Considerations

- Add authentication to your API for production use
- Use HTTPS in production
- Consider rate limiting to prevent abuse
- Whitelist allowed origins for CORS if needed