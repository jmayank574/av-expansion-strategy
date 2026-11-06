{% set subs = ['log_metro_pop', 'city_density', 'taxi_ridehail_share', 'no_vehicle_share', 'enplanements_per_resident',
               'rain_days', 'snow_days', 'heat_days', 'reg_tier', 'new_entrant_score', 'crowding', 'elec_cents_kwh'] %}
{% for s in subs %}
select metro, benchmark, '{{ s }}' as submetric, cast({{ s }} as double) as value from {{ ref('int_features') }}
{% if not loop.last %}union all{% endif %}
{% endfor %}
