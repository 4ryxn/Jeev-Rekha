"""Deterministic WGS84 spherical geometry. Distances are kilometres; a segment is
tested against a radius using great-circle cross-track distance, not sampling."""
from math import asin, atan2, cos, radians, sin
EARTH_KM=6371.0088
def distance_km(a,b):
 lat1,lon1=map(radians,(a[1],a[0]));lat2,lon2=map(radians,(b[1],b[0]));dlat=lat2-lat1;dlon=lon2-lon1
 return 2*EARTH_KM*asin((sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2)**.5)
def _bearing(a,b):
 lat1,lon1=map(radians,(a[1],a[0]));lat2,lon2=map(radians,(b[1],b[0]));return atan2(sin(lon2-lon1)*cos(lat2),cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))
def point_in_radius(point,centre,radius_km): return distance_km(point,centre)<=radius_km
def segment_intersects_radius(a,b,centre,radius_km):
 d13=distance_km(a,centre)/EARTH_KM;d12=distance_km(a,b)/EARTH_KM
 if not d12:return point_in_radius(a,centre,radius_km)
 delta=_bearing(a,centre)-_bearing(a,b);cross=asin(max(-1,min(1,sin(d13)*sin(delta))))*EARTH_KM
 along=atan2(sin(d13)*cos(delta),cos(d13))*EARTH_KM
 return abs(cross)<=radius_km and 0<=along<=d12*EARTH_KM or min(distance_km(a,centre),distance_km(b,centre))<=radius_km
def line_intersects_radius(line,centre,radius_km): return any(segment_intersects_radius(a,b,centre,radius_km) for a,b in zip(line,line[1:]))
