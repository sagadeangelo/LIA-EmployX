from fastapi import APIRouter, HTTPException, status
from backend.modules.location.models.location_response import LocationRequest, LocationResponse
from backend.modules.location.services.reverse_geocoding_service import ReverseGeocodingService

router = APIRouter(prefix="/api/v1/location", tags=["location"])

@router.post("/reverse", response_model=LocationResponse)
async def reverse_geocode(request: LocationRequest):
    try:
        location = await ReverseGeocodingService.get_location(request.latitude, request.longitude)
        return location
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar la ubicación")
