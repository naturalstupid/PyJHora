# AstroCal FastAPI Backend

This module exposes horoscope computations via a simple REST API.

## Endpoints

- `GET /health` – basic health check
- `POST /chart` – compute a Vedic horoscope

### Example request

```json
{
  "name": "John Doe",
  "gender": "M",
  "birth_date": "2000-01-01",
  "birth_time": "12:34:00",
  "place": "Chennai, India",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "timezone": 5.5
}
```

Start the API with:

```bash
uvicorn astroapi.main:app --reload
```

The response contains horoscope information ready for client consumption.
