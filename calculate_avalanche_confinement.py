# ---------------------------------------------------------------------------
# Title: Length of avalanche
# Created on: 2020-02-25 15:03 by HTLA
# Description: Python file to play around with concepts, all temporary
# ---------------------------------------------------------------------------
import arcpy


# --- Input files
start_FID = 0
end_FID = 18658
FID = range(start_FID, end_FID, 1)
ras = r"path\to\swissALTI3D_5M.tif"
fc = r"path\to\outline2018_polygon.shp"
fc_line = r"path\to\av_line_18566.shp"


# --- Output files
output = r"path\to\confinement.shp"

# fld_prefix = "Length"
# start_at = 0

arcpy.env.workspace = "IN_MEMORY"
arcpy.env.snapRaster = ras
arcpy.env.overwriteOutput = True

# Enable Spatial analyst
arcpy.CheckOutExtension("Spatial")

for i in FID:
    arcpy.Delete_management("in_memory")

    # --- Select polygon
    arcpy.MakeFeatureLayer_management(in_features=fc, out_layer="polygon", where_clause='"FID" = %s' %i,
                                      workspace="",
                                      field_info="FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;reference reference VISIBLE NONE")

    # --- Select polyline
    arcpy.MakeFeatureLayer_management(in_features=fc_line, out_layer="line", where_clause='"FID" = %s' %i,
                                      workspace="",
                                      field_info="FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;reference reference VISIBLE NONE")

    print("FID selected")

    # --- Polygon to polyline
    arcpy.PolygonToLine_management(in_features="polygon", out_feature_class="polyline", neighbor_option="IGNORE_NEIGHBORS")

    print("Polygon to polyline")

    # --- Generate points along lines every 10m
    arcpy.GeneratePointsAlongLines_management(Input_Features="line",
                                              Output_Feature_Class="points",
                                              Point_Placement="DISTANCE", Distance="10 Meters", Percentage="",
                                              Include_End_Points="")

    print("Points generated every 10m")

    # --- Extract values to points
    arcpy.gp.ExtractValuesToPoints_sa("points", ras,
                                      "points_ras",
                                      "NONE", "VALUE_ONLY")

    print("Values extracted to points")

    # --- Distance between point and outline of avalanche
    arcpy.Near_analysis(in_features="points_ras", near_features="polyline", search_radius="",
                        location="NO_LOCATION", angle="NO_ANGLE", method="PLANAR")

    # --- Append to final shapefile
    arcpy.Append_management(inputs="points_ras", target=output, schema_type="NO_TEST", field_mapping="", subtype="")

    # time.sleep(1)

    print(i)
    print("Finished")
