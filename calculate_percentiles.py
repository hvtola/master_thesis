# ---------------------------------------------------------------------------
# Title: CalcPercentiles
# Created on: 2015-09-26 12:42 by Xander
# Last Edit: 2021-01-20 11:45 by HTLA
# Description: Takes a raster and calculates percentiles for segments in a given mask.
# - As Input this script needs a (segmented) feature class and a raster.
# - The percentile values will be listed in the table of the mask.
# - (In the Scratch workspace the script saves the little rasters that are created by ExtractByMask. They can be useful
# later on.)
# ---------------------------------------------------------------------------
import arcpy

def main():
    # settings
    ras = r'path\to\Troms_rz_int.tif'
    fc = r"path\to\outline_20142019_polygon_norway.shp"
    lst_perc = [2, 5, 10, 25, 50, 75, 90, 95, 98]  # list of percentiles to be calculated
    fld_prefix = "Perc_"
    start_at = 0 # FID value, if arcpy crashes, restart at current FID

    arcpy.env.workspace = "IN_MEMORY"
    arcpy.env.snapRaster = ras
    arcpy.env.overwriteOutput = True

    # add fields if they do not exist in fc
    # be aware, fields that exist will be overwritten!
    arcpy.AddMessage("filling field list and adding fields")
    flds = []
    for perc in lst_perc:
        fld_perc = "{0}{1}".format(fld_prefix, perc)
        flds.append(fld_perc)
        if not FieldExist(fc, fld_perc):
            arcpy.AddField_management(fc, fld_perc, "LONG")
    arcpy.AddMessage("flds={0}".format(flds))

    # Enable Spatial analyst
    arcpy.CheckOutExtension("Spatial")

    # get cell area
    desc = arcpy.Describe(ras)
    cell_area = desc.meanCellHeight * desc.meanCellWidth

    # loop through polygons
    arcpy.AddMessage("loop through polygons")
    flds.append("SHAPE@")
    i = 0
    with arcpy.da.UpdateCursor(fc, flds) as curs:
        for row in curs:
            i += 1
            arcpy.AddMessage("Processing polygon: {0}".format(i))
            if i >= start_at:
                polygon = row[flds.index("SHAPE@")]
                polygon = polygon.projectAs(desc.spatialReference)

                if polygon.area < cell_area:
                    polygon = polygon.buffer((desc.meanCellHeight + desc.meanCellWidth) / 4)

                # Execute ExtractByPolygon (you can't send the polygon object)
                arcpy.AddMessage(" - ExtractByMask...")

                # arcpy.sa.ExtractByPolygon(ras, lst_parts, "INSIDE")
                ras_pol = arcpy.sa.ExtractByMask(ras, polygon)
                del polygon
                outname = "ras{0}".format(i)
                ras_pol.save(outname)
                arcpy.AddMessage(" - saved raster as {0}".format(outname))
                print(outname)

                # create dictionary with value vs count
                arcpy.AddMessage(" - fill dict with Value x Count")
                flds_ras = ("VALUE", "COUNT")
                dct = {row[0]:row[1] for row in arcpy.da.SearchCursor(outname, flds_ras)} # NB! Raster has to be integer type!
                del ras_pol
                # del outname

                # calculate number of pixels in raster
                arcpy.AddMessage(" - determine sum")
                cnt_sum = sum(dct.values())
                arcpy.AddMessage(" - sum={0}".format(cnt_sum))

                # loop through dictionary and create new dictionary with val vs percentile
                arcpy.AddMessage(" - create percentile dict")
                dct_per = {}
                cnt_i = 0
                for val in sorted(dct.keys()):
                    cnt_i += dct[val]
                    dct_per[val] = cnt_i / cnt_sum
                del dct

                # loop through list of percentiles
                arcpy.AddMessage(" - iterate perceniles")
                for perc in lst_perc:
                    # use dct_per to determine percentiles
                    perc_dec = float(perc) / 100
                    arcpy.AddMessage("  - Perc_dec for is {0}".format(perc_dec))
                    pixval = GetPixelValueForPercentile(dct_per, perc_dec)
                    arcpy.AddMessage("  - Perc for {0}% is {1}".format(perc, pixval))

                    # write pixel value to percentile field
                    arcpy.AddMessage("  - Store value")
                    fld_perc = "{0}{1}".format(fld_prefix, perc)
                    row[flds.index(fld_perc)] = pixval
                del dct_per

                # update row
                arcpy.AddMessage(" - update row")
                curs.updateRow(row)

    # return SA license
    arcpy.CheckInExtension("Spatial")


def GetPixelValueForPercentile(dctper, percentile):
    """will return last pixel value
      where percentile LE searched percentile."""
    pix_val = -1
    try:
        pix_val = sorted(dctper.keys())[0]  # initially assign lowest pixel value
        for k in sorted(dctper.keys()):
            perc = dctper[k]
            if perc <= percentile:
                pix_val = k
            else:
                break
    except Exception as e:
        pass
    return pix_val


def FieldExist(featureclass, fieldname):
    """Check if field exists"""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    return len(fieldList) == 1


if __name__ == '__main__':
    main()
