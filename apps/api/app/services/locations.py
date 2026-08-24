from datetime import UTC, datetime

from fastapi import HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Consignment,
    ContainmentScenario,
    Location,
    MovementEvent,
    Outbreak,
    RouteSegment,
    SurveillanceUpdate,
    TraceFinding,
)
from app.models.core import LocationDataSource, LocationType
from app.schemas.core import LocationCreate, LocationUpdate


REGISTRY_TYPE_MAP = {
    "village": LocationType.VILLAGE,
    "livestock_market": LocationType.MARKET,
    "checkpost": LocationType.CHECKPOST,
    "veterinary_centre": LocationType.VETERINARY_CENTRE,
}


class LocationRegistryService:
    """Manual pilot-location lifecycle; never mutates demonstration locations."""

    def _active_duplicate(
        self,
        db: Session,
        *,
        name: str,
        district: str,
        state: str,
        exclude_id: int | None = None,
    ) -> Location | None:
        query = select(Location).where(
            Location.is_active.is_(True),
            func.lower(Location.name) == name.lower(),
            func.lower(Location.district) == district.lower(),
            func.lower(Location.state) == state.lower(),
        )
        if exclude_id is not None:
            query = query.where(Location.id != exclude_id)
        return db.scalar(query)

    def create(self, db: Session, payload: LocationCreate) -> Location:
        if self._active_duplicate(db, name=payload.name, district=payload.district, state=payload.state):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An active location with the same name, district, and state already exists")
        item = Location(
            name=payload.name,
            type=REGISTRY_TYPE_MAP[payload.location_type],
            district=payload.district,
            state=payload.state,
            latitude=payload.latitude,
            longitude=payload.longitude,
            geometry=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326),
            data_source=LocationDataSource.PILOT_ENTERED,
            is_active=True,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, location_id: int, payload: LocationUpdate) -> Location:
        item = db.get(Location, location_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        if item.data_source != LocationDataSource.PILOT_ENTERED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo-seeded locations are read-only in this phase")
        changes = payload.model_dump(exclude_none=True)
        next_name = str(changes.get("name", item.name))
        next_district = str(changes.get("district", item.district))
        next_state = str(changes.get("state", item.state))
        if item.is_active and self._active_duplicate(db, name=next_name, district=next_district, state=next_state, exclude_id=item.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An active location with the same name, district, and state already exists")
        if "location_type" in changes:
            item.type = REGISTRY_TYPE_MAP[str(changes.pop("location_type"))]
        for key in ("name", "district", "state", "latitude", "longitude"):
            if key in changes:
                setattr(item, key, changes[key])
        if "latitude" in changes or "longitude" in changes:
            item.geometry = WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326)
        item.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(item)
        return item

    def archive(self, db: Session, location_id: int) -> Location:
        item = db.get(Location, location_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        if item.data_source != LocationDataSource.PILOT_ENTERED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo-seeded locations are read-only in this phase")
        if not item.is_active:
            return item
        references = self._references(db, item.id)
        if references:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location cannot be archived because it is referenced by existing {', '.join(references)} records",
            )
        item.is_active = False
        item.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def _references(db: Session, location_id: int) -> list[str]:
        references: list[str] = []
        checks = {
            "outbreak": select(Outbreak.id).where(Outbreak.location_id == location_id),
            "consignment": select(Consignment.id).where(or_(Consignment.origin_location_id == location_id, Consignment.destination_location_id == location_id)),
            "movement event": select(MovementEvent.id).where(MovementEvent.location_id == location_id),
            "route segment": select(RouteSegment.id).where(or_(RouteSegment.start_location_id == location_id, RouteSegment.end_location_id == location_id)),
            "surveillance update": select(SurveillanceUpdate.id).where(SurveillanceUpdate.location_id == location_id),
            "trace finding": select(TraceFinding.id).where(
                TraceFinding.entity_id == str(location_id),
                TraceFinding.entity_type.in_(["location", "market", "checkpost"]),
            ),
            "containment scenario": select(ContainmentScenario.id).join(Outbreak).where(Outbreak.location_id == location_id),
        }
        for label, query in checks.items():
            if db.scalar(query.limit(1)) is not None:
                references.append(label)
        return references
