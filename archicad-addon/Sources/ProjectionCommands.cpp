#include "ProjectionCommands.hpp"
#include "MigrationHelper.hpp"

#include <cmath>

Set3DProjectionCommand::Set3DProjectionCommand () :
    CommandBase (CommonSchema::Used)
{}

GS::String Set3DProjectionCommand::GetName () const
{
    return "Set3DProjection";
}

GS::Optional<GS::UniString> Set3DProjectionCommand::GetInputParametersSchema () const
{
    return R"({
    "type": "object",
    "properties": {
        "cameraPosition": {
            "$ref": "#/Coordinate3D",
            "description": "The 3D position of the camera (eye)."
        },
        "targetPosition": {
            "$ref": "#/Coordinate3D",
            "description": "The 3D position the camera looks at."
        },
        "viewCone": {
            "type": "number",
            "description": "Optional view cone (field of view) angle in radians. If omitted, the current value is kept."
        },
        "rollAngle": {
            "type": "number",
            "description": "Optional camera roll angle in radians. If omitted, the current value is kept."
        }
    },
    "additionalProperties": false,
    "required": [
        "cameraPosition",
        "targetPosition"
    ]
})";
}

GS::Optional<GS::UniString> Set3DProjectionCommand::GetResponseSchema () const
{
    return R"({
        "$ref": "#/ExecutionResult"
    })";
}

GS::ObjectState Set3DProjectionCommand::Execute (const GS::ObjectState& parameters, GS::ProcessControl& /*processControl*/) const
{
    const GS::ObjectState* cameraOS = parameters.Get ("cameraPosition");
    const GS::ObjectState* targetOS = parameters.Get ("targetPosition");
    if (cameraOS == nullptr || targetOS == nullptr) {
        return CreateFailedExecutionResult (APIERR_BADPARS, "Both cameraPosition and targetPosition are required.");
    }

    const API_Coord3D camera = Get3DCoordinateFromObjectState (*cameraOS);
    const API_Coord3D target = Get3DCoordinateFromObjectState (*targetOS);

    // Seed from the current projection so unspecified fields stay sane.
    API_3DProjectionInfo proj = {};
    GSErrCode err = ACAPI_View_Get3DProjectionSets (&proj);
    if (err != NoError) {
        return CreateFailedExecutionResult (err, "Failed to read current 3D projection (is a 3D window available?).");
    }

    proj.isPersp = true;

    proj.u.persp.pos.x    = camera.x;
    proj.u.persp.pos.y    = camera.y;
    proj.u.persp.cameraZ  = camera.z;
    proj.u.persp.target.x = target.x;
    proj.u.persp.target.y = target.y;
    proj.u.persp.targetZ  = target.z;

    const double dx = target.x - camera.x;
    const double dy = target.y - camera.y;
    proj.u.persp.distance = std::sqrt (dx * dx + dy * dy);
    proj.u.persp.azimuth  = std::atan2 (dy, dx);

    double viewCone = 0.0;
    if (parameters.Get ("viewCone", viewCone)) {
        proj.u.persp.viewCone = viewCone;
    }
    double rollAngle = 0.0;
    if (parameters.Get ("rollAngle", rollAngle)) {
        proj.u.persp.rollAngle = rollAngle;
    }

    bool switchOnlyAxonoOrPersp = false;
    err = ACAPI_View_Change3DProjectionSets (&proj, &switchOnlyAxonoOrPersp);

    return err == NoError
        ? CreateSuccessfulExecutionResult ()
        : CreateFailedExecutionResult (err, "Failed to set the 3D projection.");
}
