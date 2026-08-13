import httpx
import logging
from backend.modules.location.models.location_response import LocationResponse

logger = logging.getLogger(__name__)

class ReverseGeocodingService:
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    USER_AGENT = "LIA-EmployX/1.0 (LIA-Tech)"

    @classmethod
    async def get_location(cls, lat: float, lon: float) -> LocationResponse:
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "zoom": 10 # Zoom 10 is usually city level
        }
        headers = {
            "User-Agent": cls.USER_AGENT
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(cls.NOMINATIM_URL, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            logger.error("Timeout fetching reverse geocoding from Nominatim.")
            raise ValueError("Timeout al obtener la ubicación")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Nominatim: {e.response.status_code}")
            raise ValueError("Error del proveedor de ubicación")
        except Exception as e:
            logger.error(f"Unknown error fetching location: {e}")
            raise ValueError("Error al procesar la ubicación")

        if "error" in data:
            logger.warning(f"Nominatim returned error: {data['error']}")
            raise ValueError("No se pudo resolver la ubicación")

        address = data.get("address", {})
        
        # Resolve city
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("municipality")
        )

        # Resolve region/state
        region = (
            address.get("state") or
            address.get("region") or
            address.get("county")
        )

        country = address.get("country")
        country_code = address.get("country_code")
        
        if country_code:
            country_code = country_code.lower()

        # Build a nice display name prioritizing our parsed fields, 
        # or fallback to Nominatim's display_name
        parts = []
        if city:
            parts.append(city)
        if region:
            parts.append(region)
        if country:
            parts.append(country)

        if parts:
            display_name = ", ".join(parts)
        else:
            display_name = data.get("display_name", "Ubicación desconocida")

        return LocationResponse(
            city=city,
            region=region,
            country=country,
            country_code=country_code,
            display_name=display_name
        )
