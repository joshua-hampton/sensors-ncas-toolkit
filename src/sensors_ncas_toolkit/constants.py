"""Constants used throughout library
"""

DEVICE_ATTRIBUTES = [
    "description",
    "short_name",
    "long_name",
    "serial_number",
    "manufacturer_uri",
    "manufacturer_name",
    "device_type_uri",
    "device_type_name",
    "status_uri",
    "status_name",
    "model",
    "inventory_number",
    "schema_version",
    "identifer_type",
    "website",
    "group_ids",
    "is_private",
    "is_internal",
    "is_public",
    "keywords",
    "country",
]

MIN_PRIVATE_DEVICE_ATTRIBUTES = [
    "short_name",
    "manufacturer_name",
    "is_private",
    "is_internal",
    "is_public",
]

MIN_INTERNAL_DEVICE_ATTRIBUTES = MIN_PRIVATE_DEVICE_ATTRIBUTES + [
    "group_ids",
]

MIN_PUBLIC_DEVICE_ATTRIBUTES = MIN_INTERNAL_DEVICE_ATTRIBUTES + []


SITE_ATTRIBUTES = [
    "label",
    "geometry",
    "description",
    "epsg_code",
    "is_internal",
    "is_public",
    "group_ids",
    "street",
    "street_number",
    "city",
    "zip_code",
    "country",
    "building",
    "room",
    "site_type_uri",
    "site_type_name",
    "site_usage_uri",
    "site_usage_name",
    "elevation",
    "elevation_datum_name",
    "elevation_datum_uri",
    "website",
    "keywords",
]
