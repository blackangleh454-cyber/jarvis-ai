# API Builder

**Description:** Generate professional REST and GraphQL APIs with authentication, validation, and documentation.

**Commands:**
- `generate rest <name>` - Generate REST API
- `generate graphql <name>` - Generate GraphQL API
- `add-endpoint <api> <method> <path>` - Add endpoint
- `add-auth <api>` - Add JWT authentication
- `add-swagger <api>` - Add OpenAPI/Swagger docs

**Features:**
- JWT authentication
- Rate limiting
- Input validation (Pydantic)
- OpenAPI/Swagger docs
- WebSocket support
- GraphQL with resolvers

**Usage:**
```bash
python handler.py generate rest myapi
python handler.py generate graphql myapi
python handler.py add-endpoint myapi GET /users
python handler.py add-auth myapi
```
