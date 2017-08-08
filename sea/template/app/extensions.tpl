{%- if not skip_consul -%}
from sea.contrib.extensions.consul import Consul
{% endif -%}
{%- if not skip_orator -%}
from sea.contrib.extensions.orator import Orator
{% endif %}

{% if not skip_consul -%}
consul = Consul()
{% endif -%}
{%- if not skip_orator -%}
db = Orator()
{% endif %}
