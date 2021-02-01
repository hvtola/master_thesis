# ---------------------------------------------------------------------------
# Title: Length of avalanche
# Created on: 2020-02-25 15:03 by HTLA
# Description: Python file to play around with concepts, all temporary
# ---------------------------------------------------------------------------
import arcpy


# --- Input files
start_FID = 0
end_FID = 18566
FID = range(start_FID, end_FID, 1)
ras = r"path\to\swissALTI3D_5M.tif"
fc = r"path\to\outline2018_polygon.shp"

# --- Output files
length = r"path\to\av_line_18566.shp"

# --- Set params
arcpy.env.workspace = "IN_MEMORY"
arcpy.env.snapRaster = ras
arcpy.env.overwriteOutput = True

# Enable Spatial analyst
arcpy.CheckOutExtension("Spatial")

for i in FID:

    arcpy.Delete_management("in_memory")

    # --- Select polygon
    arcpy.MakeFeatureLayer_management(in_features=fc, out_layer="polygon", where_clause='"FID" = %s' %i, workspace="", field_info="FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;OBJECTID OBJECTID VISIBLE NONE;typ typ VISIBLE NONE;typ_hum typ_hum VISIBLE NONE;trg_typ trg_typ VISIBLE NONE;frac_wdh frac_wdh VISIBLE NONE;frac_wdh_a frac_wdh_a VISIBLE NONE;aspect aspect VISIBLE NONE;sze sze VISIBLE NONE;start_zone start_zone VISIBLE NONE;dpo_alt dpo_alt VISIBLE NONE;typ_fractu typ_fractu VISIBLE NONE;nte nte VISIBLE NONE;aval_shape aval_shape VISIBLE NONE;Shape_Leng Shape_Leng VISIBLE NONE;Shape_Area Shape_Area VISIBLE NONE;SHAPE_Le_1 SHAPE_Le_1 VISIBLE NONE;SHAPE_Ar_1 SHAPE_Ar_1 VISIBLE NONE")

    print("Polygon selected")

    # --- Polygon to polyline
    arcpy.PolygonToLine_management(in_features="polygon", out_feature_class="polyline", neighbor_option="IGNORE_NEIGHBORS")

    print("Polygon to polyline")

    # --- Extract raster values from where the polyline intersects raster values
    arcpy.gp.ExtractByMask_sa(ras, "polyline", "raster_polyline")

    print("Raster extracted from polyline")

    # --- Euclidean distance
    arcpy.gp.EucDistance_sa("raster_polyline", "euclidean_dist", "", "5", "")

    print("Euclidean distance")

    # --- Extract by mask
    arcpy.gp.ExtractByMask_sa("euclidean_dist", "polygon", "euc_poly")

    print("Euclidean distance extracted by mask")

    # --- Extract by mask
    arcpy.gp.ExtractByMask_sa("euclidean_dist", "polyline", "euc_line")

    print("Euclidean distance extracted by mask")

    arcpy.MosaicToNewRaster_management("euc_poly;euc_line", arcpy.env.workspace, "euclidean", cellsize="5", number_of_bands="1")

    # Get the geoprocessing result object
    elevMAXResult = arcpy.GetRasterProperties_management("euclidean", "MAXIMUM")
    # Get the elevation maximum value from geoprocessing result object
    elevMAX = elevMAXResult.getOutput(0)
    elevMAX = str(elevMAX)
    elevMAX = elevMAX.replace(",", ".")

    print(elevMAX)

    # --- Invert the raster
    arcpy.gp.RasterCalculator_sa('(("euclidean" - %s) * -1) + 0' %elevMAX, "euc_inv_input")

    print("Raster inverted")

    # --- Set nan values to 10000
    arcpy.gp.RasterCalculator_sa('Con(IsNull("euc_inv_input"),60000,"euc_inv_input")',"euc_inv")

    print("Nan values changed to 60000")

    # --- Get high point
    arcpy.gp.ZonalStatistics_sa("polyline", "FID", "raster_polyline", "max_elevation", "MAXIMUM", "DATA")
    arcpy.gp.RasterCalculator_sa('Con("raster_polyline" == "max_elevation","raster_polyline")', "max_value")
    arcpy.RasterToPoint_conversion(in_raster="max_value", out_point_features="max_p", raster_field="Value")
    arcpy.MeanCenter_stats(Input_Feature_Class="max_p", Output_Feature_Class="max_point")

    print("Get high point")

    # Get low point
    arcpy.gp.ZonalStatistics_sa("polyline", "FID", "raster_polyline", "min_elevation", "MINIMUM", "DATA")
    arcpy.gp.RasterCalculator_sa('Con("raster_polyline" == "min_elevation","raster_polyline")', "min_value")
    arcpy.RasterToPoint_conversion(in_raster="min_value", out_point_features="min_p", raster_field="Value")
    arcpy.MeanCenter_stats(Input_Feature_Class="min_p", Output_Feature_Class="min_point")

    print("Get low point")

    # --- Cost Distance
    arcpy.gp.CostDistance_sa("max_point", "euc_inv", "cost_distance", "", "cost_direction", "", "", "", "", "")

    print("Cost distance")

    # --- Least cost path
    arcpy.gp.CostPath_sa("min_point", "cost_distance", "cost_direction", "cost_path", "EACH_CELL", "")

    print("Least cost path")

    # --- Convert result to polyline
    arcpy.RasterToPolyline_conversion(in_raster="cost_path", out_polyline_features="line", background_value="ZERO", minimum_dangle_length="0", simplify="SIMPLIFY", raster_field="Value")

    # --- Unsplit lines
    arcpy.Dissolve_management(in_features="line", out_feature_class="output", dissolve_field="", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="UNSPLIT_LINES")

    # --- Add field
    arcpy.AddField_management(in_table="output", field_name="reference", field_type="LONG", field_is_required="NON_REQUIRED")

    # Add value to reference field
    arcpy.CalculateField_management(in_table="output", field="reference", expression="%s" %i, expression_type="PYTHON", code_block="")

    # --- Append to final shapefile
    arcpy.Append_management(inputs="output", target=length, schema_type="NO_TEST", field_mapping="", subtype="")

    # time.sleep(1)

    print(i)
    print("Finished")
