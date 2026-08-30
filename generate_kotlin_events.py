import os
import json
import glob

SCHEMA_DIR = "schemas"
MAPPING_DIR = "mappings"

# Görseldeki klasör hiyerarşisine tam uyan hedef çıktı dizini
OUTPUT_KOTLIN_DIR = "./core/analytics/src/main/java/com/example/core/analytics/generated"

os.makedirs(OUTPUT_KOTLIN_DIR, exist_ok=True)

# JSON Schema tiplerinin Kotlin karşılıkları
TYPE_MAP = {
    "string": "String",
    "number": "Double",
    "integer": "Int",
    "boolean": "Boolean"
}

def to_pascal_case(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))

schema_files = glob.glob(f"{SCHEMA_DIR}/*.schema.json")

for schema_path in schema_files:
    filename = os.path.basename(schema_path).replace(".schema.json", "")
    mapping_path = os.path.join(MAPPING_DIR, f"{filename}.mapping.json")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    mapping = {}
    if os.path.exists(mapping_path):
        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)

    event_name = mapping.get("event_name", filename)
    class_name = f"{to_pascal_case(event_name)}Event"
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    destinations = mapping.get("destinations", [])
    destination_payloads = mapping.get("destination_payloads", {})

    constructor_params = []
    raw_params_map = []

    for prop_name, prop_data in properties.items():
        json_type = prop_data.get("type", "string")
        kotlin_type = TYPE_MAP.get(json_type, "Any")
        is_required = prop_name in required_fields

        if not is_required:
            kotlin_type += "? = null"

        constructor_params.append(f"    val {prop_name}: {kotlin_type}")
        raw_params_map.append(f'        "{prop_name}" to {prop_name}')

    params_code = ",\n".join(constructor_params)
    raw_map_code = ",\n".join(raw_params_map)

    dest_enum_list = ", ".join([f"AnalyticsDestination.{d}" for d in destinations])

    when_branches = []
    for dest, payload_map in destination_payloads.items():
        payload_entries = [f'            "{target_key}" to {source_param}' for target_key, source_param in payload_map.items()]
        entries_code = ",\n".join(payload_entries)
        branch = f"""        AnalyticsDestination.{dest} -> mapOf(
{entries_code}
        )"""
        when_branches.append(branch)

    when_code = "\n".join(when_branches)

    # Paket adı ve Import yolları projendeki yeni :core:analytics modülüne göre güncellendi
    kotlin_class = f"""// Generative AI tarafından otomatik üretilmiştir - Elle değiştirmeyiniz
package com.example.core.analytics.generated

import com.example.core.analytics.EventModel
import com.example.core.analytics.AnalyticsDestination

data class {class_name}(
{params_code}
) : EventModel() {{

    override val eventName: String = "{event_name}"

    override val destinations: List<AnalyticsDestination> = listOf(
        {dest_enum_list}
    )

    override val parameters: Map<String, Any?> = mapOf(
{raw_map_code}
    )

    override fun getMappedParameters(destination: AnalyticsDestination): Map<String, Any?> {{
        return when (destination) {{
{when_code}
            else -> parameters
        }}
    }}
}}
"""

    output_path = os.path.join(OUTPUT_KOTLIN_DIR, f"{class_name}.kt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kotlin_class)

    print(f"Kotlin sınıfı üretildi: {class_name}.kt -> {output_path}")