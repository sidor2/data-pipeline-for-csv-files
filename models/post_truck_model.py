from aws_cdk.aws_apigateway import JsonSchema, JsonSchemaType, JsonSchemaVersion

post_truck_schema=JsonSchema(
    schema=JsonSchemaVersion.DRAFT4,
    title="AddTruckModel",
    type=JsonSchemaType.OBJECT,
    properties={
        "originalVin": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=6,
            min_length=6,
            pattern="^([Ee]9[0-9]{4})"
        ),
        "currentVin": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=6,
            min_length=6,
            pattern="^([Ee]9[0-9]{4})"
        ),
        "par": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[A-Za-z0-9]+"
        ),
        "engine": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^([Dd]{2}[0-9]{2})|^([Cc]ummins)"
        ),
        "ats": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^(GATS|gats)[0-9]+\.[0-9]+"
        ),
        "cab": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[Ss]leeper|^[Dd]ay"
        ),
        "chassis": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[a-zA-Z\s]*"
        ),
        "axleRatio": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="[0-9]\.[0-9]+"
        ),
        "powerRating": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[0-9/]+"
        ),
        "fuelmap": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=14,
            min_length=0,
            pattern="^[0-9.]+"
        ),
        "transmission": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[A-Za-z0-9]+"
        ),
        "fanClutchCooler": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[a-zA-Z\s]*"
        ),
        "fanModel": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[A-Za-z0-9]+"
        ),
        "fanClutch": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[A-Za-z0-9]+"
        ),
        "trailerNumber": JsonSchema(
            type=JsonSchemaType.STRING,
            max_length=10,
            min_length=0,
            pattern="^[Tt][0-9]{1,3}"
        ),
    },
    required=["currentVin", "originalVin"]
)