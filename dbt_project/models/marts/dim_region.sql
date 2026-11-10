select region_code, region_name
from (
    values
        ('APAC', 'Asia Pacific'),
        ('EMEA', 'Europe, Middle East and Africa'),
        ('AMER', 'Americas'),
        ('GLOBAL', 'Global (not region-specific)'),
        ('UNKNOWN', 'Unknown (orphan record)')
) as t(region_code, region_name)