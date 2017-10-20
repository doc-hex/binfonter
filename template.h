
int ${PREFIX}_lookup_glyph(uint32_t cp, bboxInfo_t *bboxOut);

#ifdef INCL_C_SOURCE
static const bboxInfo_t ${PREFIX}_bboxValues[] = {
    { /* zero unused */ }, 
    $BOXES
};

static const uint8_t ${PREFIX}_bitmapValues[] = {
    $BITS
};

int ${PREFIX}_lookup_glyph(uint32_t cp, bboxInfo_t *bboxOut)
{
    uint16_t offset = 0;

    switch(cp) {
        default: break;

        $RANGES
    }
    if(!offset) return 1;

    if(bboxOut) {
        int idx = ${PREFIX}_bitmapValues[offset];
        *bboxOut = ${PREFIX}_bboxValues[idx];
        bboxOut->bits = &${PREFIX}_bitmapValues[offset+1];
    }

    return 0;
}
#endif
